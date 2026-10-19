"""
Step 2-7: Analysis pipeline for 76ers 2018-19 lineup data.

Input (from 01_pull_data.py):
 - data/sixers_lineups_2018_19_raw.csv
 - data/sixers_team_overall_2018_19.csv

Outputs:
 - data/lineups_processed.csv   (every lineup, with adjusted net rating)
 - data/player_impact.csv       (Ridge regression coefficients per player)
 - Console printout of top/bottom lineups and player impact ranking

(00_demo_data.py can still generate a small illustrative dataset; point
RAW_FILE / TEAM_FILE at the *_DEMO.csv files to use it.)
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

# ---- CONFIG ----
RAW_FILE = "data/sixers_lineups_2018_19_raw.csv"
TEAM_FILE = "data/sixers_team_overall_2018_19.csv"
DISPLAY_MIN = 40            # console rankings only list lineups with at least this many minutes
PRIOR_WEIGHT = 100          # "pseudo-minutes" of shrinkage toward team average
ALPHA_GRID = [1, 10, 100, 1000, 10000]   # Ridge penalties tried; best one chosen by cross-validation
CV_FOLDS = 5
SEED = 42

# ---- STEP 2/3: LOAD + CLEAN ----
df = pd.read_csv(RAW_FILE)
team = pd.read_csv(TEAM_FILE)
team_avg_net_rating = team["NET_RATING"].iloc[0]

# Split the 5-man lineup string ("J. Redick - J. Butler - ...") into player columns.
# The separator is " - " (with spaces) so hyphens inside names do not break the split.
players_split = df["GROUP_NAME"].str.split(" - ", expand=True).apply(lambda c: c.str.strip())
players_split.columns = [f"player_{i+1}" for i in range(players_split.shape[1])]
df = pd.concat([df, players_split], axis=1)

print(f"Loaded {len(df)} lineups, {df['MIN'].sum():,.0f} total lineup minutes")
print(f"Team overall net rating (shrinkage prior): {team_avg_net_rating}")

# ---- STEP 6: BAYESIAN SHRINKAGE ----
df["adj_net_rating"] = (
    (df["NET_RATING"] * df["MIN"] + team_avg_net_rating * PRIOR_WEIGHT)
    / (df["MIN"] + PRIOR_WEIGHT)
)

shown = df[df["MIN"] >= DISPLAY_MIN]
cols = ["GROUP_NAME", "MIN", "NET_RATING", "adj_net_rating"]
print(f"\n(Rankings below list the {len(shown)} lineups with {DISPLAY_MIN}+ minutes.)")

print("\n--- TOP 5 LINEUPS BY RAW NET RATING ---")
print(shown.sort_values("NET_RATING", ascending=False)[cols].head(5).to_string(index=False))

print("\n--- TOP 5 LINEUPS BY ADJUSTED (SHRUNK) NET RATING ---")
print(shown.sort_values("adj_net_rating", ascending=False)[cols].head(5).to_string(index=False))

print("\n--- BOTTOM 5 LINEUPS BY ADJUSTED NET RATING ---")
print(shown.sort_values("adj_net_rating")[cols].head(5).to_string(index=False))

# Save processed lineup data (all lineups; the dashboard filters by minutes)
df.to_csv("data/lineups_processed.csv", index=False)

# ---- STEP 7: SIMPLIFIED RAPM (RIDGE REGRESSION) ----
# Build player indicator matrix: 1 if player is in lineup, else 0
player_cols = [c for c in df.columns if c.startswith("player_")]
all_players = sorted(set(df[player_cols].values.flatten()))

X = pd.DataFrame(0, index=df.index, columns=all_players)
for col in player_cols:
    for idx, player in df[col].items():
        X.loc[idx, player] = 1

y = df["NET_RATING"].values
weights = df["MIN"].values

# Choose the Ridge penalty by minutes-weighted cross-validation instead of guessing.
kf = KFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED)
cv_error = {}
for alpha in ALPHA_GRID:
    errs = []
    for train, test in kf.split(X):
        m = Ridge(alpha=alpha).fit(X.iloc[train], y[train], sample_weight=weights[train])
        resid = y[test] - m.predict(X.iloc[test])
        errs.append(np.average(resid ** 2, weights=weights[test]))
    cv_error[alpha] = float(np.mean(errs))
best_alpha = min(cv_error, key=cv_error.get)
print("\nRidge alpha cross-validation (minutes-weighted MSE): "
      + ", ".join(f"{a}: {e:.1f}" for a, e in cv_error.items()))
print(f"Selected alpha = {best_alpha}")

model = Ridge(alpha=best_alpha)
model.fit(X, y, sample_weight=weights)

player_impact = pd.Series(model.coef_, index=X.columns).sort_values(ascending=False)

print("\n--- SIMPLIFIED RAPM: ESTIMATED INDIVIDUAL PLAYER IMPACT ON NET RATING ---")
print(player_impact.to_string())

player_impact.to_csv("data/player_impact.csv", header=["estimated_impact"])

print("\nSaved processed data to data/lineups_processed.csv")
print("Saved player impact to data/player_impact.csv")

print("""
NOTE: This is a simplified RAPM-style estimate built from lineup totals, not
possession-level stint data. Treat coefficients as directional, especially for
players with few minutes.
""")
