"""
Step 2-7: Analysis pipeline for 76ers 2018-19 lineup data.

Works on either:
 - data/sixers_lineups_2018_19_raw.csv  (full data, from 01_pull_data.py)
 - data/sixers_lineups_2018_19_DEMO.csv (small illustrative set, from 00_demo_data.py)

Edit RAW_FILE / TEAM_FILE below to point at whichever you have.

Outputs:
 - data/lineups_processed.csv   (with adjusted net rating)
 - data/player_impact.csv       (Ridge regression coefficients per player)
 - Console printout of top/bottom lineups and player impact ranking
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge

# ---- CONFIG ----
RAW_FILE = "data/sixers_lineups_2018_19_DEMO.csv"      # swap to _raw.csv when you have live data
TEAM_FILE = "data/sixers_team_overall_2018_19_DEMO.csv"
MIN_THRESHOLD = 0          # raise to e.g. 40 once you have full real data
PRIOR_WEIGHT = 100          # "pseudo-minutes" of shrinkage toward team average
RIDGE_ALPHA = 1.0

# ---- STEP 2/3: LOAD + CLEAN ----
df = pd.read_csv(RAW_FILE)
team = pd.read_csv(TEAM_FILE)
team_avg_net_rating = team["NET_RATING"].iloc[0]

df = df[df["MIN"] >= MIN_THRESHOLD].copy()

# Split the 5-man lineup string into individual player columns
players_split = df["GROUP_NAME"].str.split("-", expand=True)
players_split.columns = [f"player_{i+1}" for i in range(players_split.shape[1])]
df = pd.concat([df, players_split], axis=1)

print(f"Loaded {len(df)} lineups (after MIN >= {MIN_THRESHOLD} filter)")
print(f"Team overall net rating (shrinkage prior): {team_avg_net_rating}")

# ---- STEP 6: BAYESIAN SHRINKAGE ----
df["adj_net_rating"] = (
    (df["NET_RATING"] * df["MIN"] + team_avg_net_rating * PRIOR_WEIGHT)
    / (df["MIN"] + PRIOR_WEIGHT)
)

print("\n--- TOP 5 LINEUPS BY RAW NET RATING ---")
print(df.sort_values("NET_RATING", ascending=False)
        [["GROUP_NAME", "MIN", "NET_RATING", "adj_net_rating"]].head(5).to_string(index=False))

print("\n--- TOP 5 LINEUPS BY ADJUSTED (SHRUNK) NET RATING ---")
print(df.sort_values("adj_net_rating", ascending=False)
        [["GROUP_NAME", "MIN", "NET_RATING", "adj_net_rating"]].head(5).to_string(index=False))

print("\n--- BOTTOM 5 LINEUPS BY ADJUSTED NET RATING ---")
print(df.sort_values("adj_net_rating")
        [["GROUP_NAME", "MIN", "NET_RATING", "adj_net_rating"]].head(5).to_string(index=False))

# Save processed lineup data
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

model = Ridge(alpha=RIDGE_ALPHA)
model.fit(X, y, sample_weight=weights)

player_impact = pd.Series(model.coef_, index=X.columns).sort_values(ascending=False)

print("\n--- SIMPLIFIED RAPM: ESTIMATED INDIVIDUAL PLAYER IMPACT ON NET RATING ---")
print(player_impact.to_string())

player_impact.to_csv("data/player_impact.csv", header=["estimated_impact"])

print("\nSaved processed data to data/lineups_processed.csv")
print("Saved player impact to data/player_impact.csv")

print("""
NOTE: With only 10 demo lineups and ~13 players, this regression is heavily
underdetermined (more variables than independent data points) -- the Ridge
penalty keeps it numerically stable, but coefficients here are illustrative
only. With the FULL season's lineup data (50-100+ combinations) from
01_pull_data.py, this becomes a meaningful (if still simplified) RAPM-style
estimate.
""")
