"""
Дописывает в matches.csv колонку stats_json из GET /matches/{id}/stats
"""

from __future__ import annotations

import argparse

import pandas as pd
from tqdm import tqdm

import common as p


def enrich_category(
    category: str,
    client: p.PadelClient,
    *,
    force: bool,
    save_every: int,
) -> None:
    path = p.gender_out_dir(category) / "matches.csv"
    if not path.is_file():
        print(f"Нет файла {path}")
        return

    df = pd.read_csv(path)
    if "stats_json" not in df.columns:
        df["stats_json"] = pd.NA

    to_fetch_idx = [
        i
        for i in range(len(df))
        if force or not p.csv_cell_filled(df.iloc[i].get("stats_json"))
    ]

    col = df.columns.get_loc("stats_json")
    n_ok = 0
    for i in tqdm(to_fetch_idx, desc=f"Match stats ({category})"):
        mid = int(df.iloc[i]["match_id"])
        try:
            st = client.get_json_skip_404(f"/matches/{mid}/stats")
            df.iloc[i, col] = p.json_cell(st) if st is not None else None
            n_ok += 1
            if save_every > 0 and n_ok % save_every == 0:
                p.save_csv_checkpoint(df, path, f"батч stats, успешных с начала запуска: {n_ok}")
        except Exception as e:
            print(f"stats match_id={mid}: {e!r}")
            p.save_csv_checkpoint(df, path, "после ошибки по матчу (stats)")

    p.save_csv_checkpoint(df, path, "финал stats")


def main() -> None:
    parser = argparse.ArgumentParser(description="Match stats в matches.csv")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Перезаписать stats_json даже если уже заполнен",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=25,
        metavar="N",
        help="Сохранять CSV каждые N успешных ответов (0 = только в конце и при ошибке)",
    )
    args = parser.parse_args()

    token = p.load_token()
    client = p.PadelClient(token)
    try:
        for cat in tqdm(p.MATCH_CATEGORIES, desc="Категории (stats)"):
            enrich_category(
                cat,
                client,
                force=args.force,
                save_every=args.save_every,
            )
    finally:
        client.close()


if __name__ == "__main__":
    main()
