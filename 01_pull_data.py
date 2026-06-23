"""
Step 1: Pull 76ers 2018-19 lineup data from the NBA Stats API.

Run this on a machine with normal internet access (stats.nba.com is often
blocked by sandboxed environments / VPNs / some corporate networks).

Output: data/sixers_lineups_2018_19_raw.csv
"""

from nba_api.stats.endpoints import leaguedashlineups
import pandas as pd
import time

TEAM_ID = "1610612755"  # Philadelphia 76ers
SEASON = "2018-19"

print("Pulling lineup data... (this can take 10-20 seconds)")

lineups = leaguedashlineups.LeagueDashLineups(
    team_id_nullable=TEAM_ID,
    season=SEASON,
    season_type_all_star="Regular Season",
    measure_type_detailed_defense="Advanced",
    group_quantity=5,
    per_mode_detailed="Totals",
)

df = lineups.get_data_frames()[0]

print(f"Pulled {len(df)} lineup combinations")
print(df.columns.tolist())

df.to_csv("data/sixers_lineups_2018_19_raw.csv", index=False)
print("Saved to data/sixers_lineups_2018_19_raw.csv")

# Also pull team-level overall stats for the baseline net rating used in shrinkage
from nba_api.stats.endpoints import teamdashboardbygeneralsplits

time.sleep(1)  # be polite to the API

team_stats = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(
    team_id=TEAM_ID,
    season=SEASON,
    season_type_all_star="Regular Season",
    measure_type_detailed_defense="Advanced",
)
overall = team_stats.get_data_frames()[0]
overall.to_csv("data/sixers_team_overall_2018_19.csv", index=False)
print("Team overall net rating:", overall["NET_RATING"].iloc[0])
print("Saved to data/sixers_team_overall_2018_19.csv")
