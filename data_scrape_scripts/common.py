"""Клиент Padel API"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

LEVELS_WITH_POINT_BY_POINT = ("major", "p1", "p2", "finals", "fip_platinum")

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_BASE = REPO_ROOT / "data" / "raw"
TOURNAMENTS_CSV = RAW_BASE / "tournaments.csv"

MATCH_CATEGORIES = ("men", "women")

REQUEST_SLEEP_SEC = 0.5
_NETWORK_RETRY_DELAYS_SEC = (3.0, 6.0, 12.0, 24.0, 45.0)


def load_token() -> str:
    load_dotenv(REPO_ROOT / ".env")
    token = os.environ.get("PADEL_API_TOKEN")
    if not token:
        raise ValueError("Нет PADEL_API_TOKEN в .env в корне репозитория")
    return token


def gender_out_dir(category: str) -> Path:
    return RAW_BASE / category


def tournament_id_from_connections(connections: object) -> int | None:
    if not isinstance(connections, dict):
        return None
    raw = connections.get("tournament")
    if not raw or not isinstance(raw, str):
        return None
    tail = raw.rstrip("/").split("/")[-1]
    if tail.isdigit():
        return int(tail)
    return None


def four_player_ids(players: object) -> tuple[int, int, int, int] | None:
    if not isinstance(players, dict):
        return None
    t1 = players.get("team_1") or []
    t2 = players.get("team_2") or []
    if len(t1) != 2 or len(t2) != 2:
        return None
    a = sorted(p["id"] for p in t1 if isinstance(p, dict) and "id" in p)
    b = sorted(p["id"] for p in t2 if isinstance(p, dict) and "id" in p)
    if len(a) != 2 or len(b) != 2:
        return None
    return (a[0], a[1], b[0], b[1])


def json_cell(x: object) -> str | None:
    if x is None:
        return None
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))


def csv_cell_filled(val: object) -> bool:
    if val is None:
        return False
    if isinstance(val, float) and pd.isna(val):
        return False
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "<na>"):
        return False
    return True


class PadelClient:
    def __init__(self, token: str) -> None:
        self._client = httpx.Client(
            base_url="https://padelapi.org/api",
            headers={"Authorization": f"Bearer {token}"},
            timeout=120.0,
        )

    def close(self) -> None:
        self._client.close()

    def _sleep_after_request(self) -> None:
        time.sleep(REQUEST_SLEEP_SEC)

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        params = dict(params or {})
        retryable = (
            httpx.ReadError,
            httpx.ConnectError,
            httpx.RemoteProtocolError,
            httpx.WriteError,
            httpx.TimeoutException,
        )
        err: BaseException | None = None
        for attempt in range(len(_NETWORK_RETRY_DELAYS_SEC) + 1):
            try:
                r = self._client.get(path, params=params)
                self._sleep_after_request()
                return r
            except retryable as e:
                err = e
                print(
                    f"Сеть: {path} params={params} попытка {attempt + 1}/"
                    f"{len(_NETWORK_RETRY_DELAYS_SEC) + 1}: {e!r}"
                )
                if attempt < len(_NETWORK_RETRY_DELAYS_SEC):
                    time.sleep(_NETWORK_RETRY_DELAYS_SEC[attempt])
                else:
                    print(f"Ошибка сети: {path} {err!r}")
        raise err  # type: ignore[misc]

    def get_json(self, path: str, params: dict | None = None) -> dict:
        params = dict(params or {})
        while True:
            r = self._get(path, params=params)
            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After", "60"))
                time.sleep(wait)
                continue
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"HTTP {e.response.status_code} {path}")
                raise
            return r.json()

    def get_json_skip_404(self, path: str) -> dict | None:
        while True:
            r = self._get(path)
            if r.status_code == 404:
                return None
            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After", "60"))
                time.sleep(wait)
                continue
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"HTTP {e.response.status_code} {path}")
                raise
            return r.json()

    def fetch_all_pages(
        self,
        path: str,
        params: dict | None = None,
        *,
        pages_desc: str | None = None,
        pages_leave: bool = True,
    ) -> list[dict]:
        base = dict(params or {})
        base["per_page"] = 50
        out: list[dict] = []
        payload = self.get_json(path, {**base, "page": 1})
        out.extend(payload["data"])
        last_page = int(payload["meta"]["last_page"])
        disabled = pages_desc is None
        with tqdm(
            total=last_page,
            desc=pages_desc,
            disable=disabled,
            leave=pages_leave,
            unit="стр",
        ) as bar:
            bar.update(1)
            for page in range(2, last_page + 1):
                payload = self.get_json(path, {**base, "page": page})
                out.extend(payload["data"])
                bar.update(1)
        return out


def collect_tournaments(client: PadelClient) -> dict[int, dict]:
    by_id: dict[int, dict] = {}
    for level in tqdm(LEVELS_WITH_POINT_BY_POINT, desc="Турниры по уровням"):
        rows = client.fetch_all_pages(
            "/tournaments",
            {
                "level": level,
                "sort_by": "start_date",
                "order_by": "asc",
            },
            pages_desc=f"Пагинация /tournaments ({level})",
        )
        for t in rows:
            tid = t["id"]
            if tid not in by_id:
                by_id[tid] = t
    return by_id


def tournament_row(t: dict) -> dict:
    return {
        "tournament_id": t["id"],
        "name": t.get("name"),
        "location": t.get("location"),
        "country": t.get("country"),
        "level": t.get("level"),
        "status": t.get("status"),
        "start_date": t.get("start_date"),
        "end_date": t.get("end_date"),
    }


def match_row(m: dict, fallback_tournament_id: int) -> dict | None:
    ids = four_player_ids(m.get("players"))
    if ids is None:
        return None
    p1, p2, p3, p4 = ids
    tid = tournament_id_from_connections(m.get("connections"))
    if tid is None:
        tid = fallback_tournament_id
    return {
        "match_id": m["id"],
        "tournament_id": tid,
        "player_id_1": p1,
        "player_id_2": p2,
        "player_id_3": p3,
        "player_id_4": p4,
        "category": m.get("category"),
        "name": m.get("name"),
        "round": m.get("round"),
        "round_name": m.get("round_name"),
        "index": m.get("index"),
        "played_at": m.get("played_at"),
        "schedule_label": m.get("schedule_label"),
        "court": m.get("court"),
        "court_order": m.get("court_order"),
        "status": m.get("status"),
        "score_json": json_cell(m.get("score")),
        "winner": m.get("winner"),
        "started_time": m.get("started_time"),
        "duration": m.get("duration"),
    }


def player_row(p: dict) -> dict:
    return {
        "player_id": p["id"],
        "name": p.get("name"),
        "short_name": p.get("short_name"),
        "category": p.get("category"),
        "ranking": p.get("ranking"),
        "points": p.get("points"),
        "height": p.get("height"),
        "nationality": p.get("nationality"),
        "birthplace": p.get("birthplace"),
        "birthdate": p.get("birthdate"),
        "age": p.get("age"),
        "hand": p.get("hand"),
        "side": p.get("side"),
    }


def load_tournaments_from_csv(path: Path) -> dict[int, dict]:
    df = pd.read_csv(path)
    by_id: dict[int, dict] = {}
    for _, r in df.iterrows():
        tid = int(r["tournament_id"])
        d = {"id": tid}
        for c in df.columns:
            if c == "tournament_id":
                continue
            d[c] = r[c] if pd.notna(r[c]) else None
        by_id[tid] = d
    return by_id


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def save_csv_checkpoint(df: pd.DataFrame, path: Path, label: str) -> None:
    save_csv(df, path)
    print(f"Сохранено: {path} ({label})")


def collect_matches_for_category(
    client: PadelClient,
    tournaments_by_id: dict[int, dict],
    category: str,
) -> pd.DataFrame:
    match_by_id: dict[int, dict] = {}
    t_list = sorted(
        tournaments_by_id.values(),
        key=lambda x: (str(x.get("start_date") or ""), x["id"]),
    )
    for t in tqdm(t_list, desc=f"Матчи по турнирам ({category})"):
        tid = t["id"]
        matches = client.fetch_all_pages(
            f"/tournaments/{tid}/matches",
            {"category": category},
            pages_desc=f"Страницы матчей (tournament_id={tid})",
            pages_leave=False,
        )
        for m in matches:
            if m.get("category") != category:
                continue
            row = match_row(m, fallback_tournament_id=tid)
            if row is None:
                continue
            match_by_id[row["match_id"]] = row

    rows = list(match_by_id.values())
    return (
        pd.DataFrame(rows)
        .sort_values(["played_at", "match_id"], na_position="last")
        .reset_index(drop=True)
    )


def collect_players_for_matches(
    client: PadelClient,
    matches_df: pd.DataFrame,
    category: str,
) -> pd.DataFrame:
    if matches_df.empty:
        return pd.DataFrame()
    player_ids: set[int] = set()
    for _, r in tqdm(
        matches_df.iterrows(),
        total=len(matches_df),
        desc=f"Уникальные игроки из матчей ({category})",
    ):
        player_ids.update(
            [
                int(r["player_id_1"]),
                int(r["player_id_2"]),
                int(r["player_id_3"]),
                int(r["player_id_4"]),
            ]
        )
    rows: list[dict] = []
    for pid in tqdm(sorted(player_ids), desc=f"Игроки ({category})"):
        pl = client.get_json(f"/players/{pid}")
        rows.append(player_row(pl))
    return (
        pd.DataFrame(rows)
        .sort_values("player_id", na_position="last")
        .reset_index(drop=True)
    )
