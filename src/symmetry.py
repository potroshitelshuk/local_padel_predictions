"""
Симметризация матчей: swap team_1 <-> team_2 как data augmentation

- `team1_X` <-> `team2_X` - значения меняются местами
- `*_p1`, `*_p2`, `*_p3`, `*_p4` или `player_id_1..4` - swap (1<->3, 2<->4)
- `*_diff` - знак инвертируется
- `*_expected_team1` - заменяется на 1 - x
- H2H: `h2h_*_team1_wins` -> `matches - wins`, `h2h_*_team1_winrate` -> 1 - x
- остальное считается симметричным и не трогается (например, `month`, `elo_min_matches`, `h2h_pair_matches`, ...)
"""
import re
import warnings
import pandas as pd

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

PLAYER_PAIR_MAP = {1: 3, 2: 4, 3: 1, 4: 2}

H2H_WINS_PAIRS = {
    "h2h_pair_team1_wins": "h2h_pair_matches",
    "h2h_players_team1_wins": "h2h_players_matches",
}
H2H_WINRATE_COLS = ("h2h_pair_team1_winrate", "h2h_players_team1_winrate")


def _swap_team_pairs(out, src):
    touched = set()
    cols = set(src.columns)
    for c in src.columns:
        if c in touched:
            continue
        other = None
        if c.startswith("team1_"):
            other = "team2_" + c[len("team1_"):]
        elif c.endswith("_team1"):
            other = c[: -len("_team1")] + "_team2"
        if other and other in cols and other not in touched:
            out[c] = src[other].values
            out[other] = src[c].values
            touched.update({c, other})


def _swap_player_slots(out, src):
    touched = set()
    cols = set(src.columns)
    suffix_re = re.compile(r"^(.+)_p([1-4])$")
    pid_re = re.compile(r"^player_id_([1-4])$")
    for c in src.columns:
        if c in touched:
            continue
        m1 = suffix_re.match(c)
        if m1:
            base, idx = m1.group(1), int(m1.group(2))
            other = f"{base}_p{PLAYER_PAIR_MAP[idx]}"
            if other in cols and other not in touched:
                out[c] = src[other].values
                out[other] = src[c].values
                touched.update({c, other})
            continue
        m2 = pid_re.match(c)
        if m2:
            idx = int(m2.group(1))
            other = f"player_id_{PLAYER_PAIR_MAP[idx]}"
            if other in cols and other not in touched:
                out[c] = src[other].values
                out[other] = src[c].values
                touched.update({c, other})


def _negate_diff(out, src):
    for c in src.columns:
        if c.endswith("_diff") and pd.api.types.is_numeric_dtype(src[c]):
            out[c] = -src[c].values


def _flip_expected(out, src):
    for c in src.columns:
        if c.endswith("_expected_team1"):
            out[c] = 1.0 - src[c].values


def _flip_h2h(out, src):
    cols = set(src.columns)
    for w_col, t_col in H2H_WINS_PAIRS.items():
        if w_col in cols and t_col in cols:
            out[w_col] = (src[t_col] - src[w_col]).values
    for c in H2H_WINRATE_COLS:
        if c in cols:
            out[c] = (1.0 - src[c]).values


def swap_match(df, *, binary_invert_cols=("target",), negate_cols=()):
    out = df.copy()

    _swap_team_pairs(out, df)
    _swap_player_slots(out, df)
    _negate_diff(out, df)
    _flip_expected(out, df)
    _flip_h2h(out, df)

    for c in binary_invert_cols:
        if c in df.columns:
            out[c] = 1 - df[c]

    for c in negate_cols:
        if c in df.columns:
            out[c] = -df[c]

    return out


def augment_with_swap(df, *, binary_invert_cols=("target",), negate_cols=()):
    swapped = swap_match(
        df,
        binary_invert_cols=binary_invert_cols,
        negate_cols=negate_cols,
    )
    return pd.concat([df.copy(), swapped], ignore_index=True)
