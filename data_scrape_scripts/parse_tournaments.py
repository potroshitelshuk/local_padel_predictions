"""
Сырые турниры в CSV

Файл: data/raw/tournaments.csv
"""

from __future__ import annotations

import common as p
from tqdm import tqdm


def main() -> None:
    token = p.load_token()
    client = p.PadelClient(token)
    try:
        by_id = p.collect_tournaments(client)
        print(f"Уникальных турниров: {len(by_id)}")
        rows = [
            p.tournament_row(t)
            for t in tqdm(by_id.values(), desc="Строки tournaments.csv")
        ]
        df = (
            p.pd.DataFrame(rows)
            .sort_values(["start_date", "tournament_id"], na_position="last")
            .reset_index(drop=True)
        )
        p.save_csv(df, p.TOURNAMENTS_CSV)
        print(f"Сохранено: {p.TOURNAMENTS_CSV}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
