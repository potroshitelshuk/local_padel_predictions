"""
Raw матчи по турнирам из tournaments.csv в CSV (men и women).

Файлы: data/raw/men/matches.csv, data/raw/women/matches.csv
"""

from __future__ import annotations

import common as p
from tqdm import tqdm


def main() -> None:
    tournaments_by_id = p.load_tournaments_from_csv(p.TOURNAMENTS_CSV)
    token = p.load_token()
    client = p.PadelClient(token)
    try:
        for cat in tqdm(p.MATCH_CATEGORIES, desc="Категории (matches)"):
            mdf = p.collect_matches_for_category(client, tournaments_by_id, cat)
            out = p.gender_out_dir(cat) / "matches.csv"
            p.save_csv(mdf, out)
            print(f"{cat}: матчей {len(mdf)}, файл {out}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
