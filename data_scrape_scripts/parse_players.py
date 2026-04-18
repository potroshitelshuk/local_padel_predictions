"""
Raw карточки игроков по id из matches.csv в CSV (men и women)

Файлы: data/raw/men/players.csv, data/raw/women/players.csv
"""

from __future__ import annotations

import common as p
from tqdm import tqdm


def main() -> None:
    token = p.load_token()
    client = p.PadelClient(token)
    try:
        for cat in tqdm(p.MATCH_CATEGORIES, desc="Категории (players)"):
            matches_path = p.gender_out_dir(cat) / "matches.csv"
            if not matches_path.is_file():
                print(f"Пропуск {cat}: нет {matches_path}")
                continue
            mdf = p.pd.read_csv(matches_path)
            pdf = p.collect_players_for_matches(client, mdf, cat)
            out = p.gender_out_dir(cat) / "players.csv"
            p.save_csv(pdf, out)
            print(f"{cat}: игроков {len(pdf)}, файл {out}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
