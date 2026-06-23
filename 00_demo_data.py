"""
Sample/demo dataset for the 2018-19 Philadelphia 76ers.

This is a SMALL, illustrative subset of real lineup combinations from that
season (the team made the Jimmy Butler trade in Nov 2018 and the Tobias
Harris trade in Feb 2019, so the roster changed mid-season - that's part of
what makes this season interesting to analyze).

When you run 01_pull_data.py locally, it will replace this with the FULL
set of lineup combinations (50-100+ rows) pulled directly from stats.nba.com.
Use this file to test the rest of the pipeline (02, 03, dashboard) before
you have live data, or if you want a quick illustrative example.

Net ratings below are approximate/illustrative, based on publicly reported
season figures - replace with live-pulled exact values for your final
submission.
"""

import pandas as pd

data = [
    # The "core five" after the Harris trade (Feb 2019 onward)
    {"GROUP_NAME": "B. Simmons-J. Butler-T. Harris-J. Redick-J. Embiid",
     "MIN": 110, "OFF_RATING": 116.5, "DEF_RATING": 104.2, "NET_RATING": 12.3},

    # Pre-Harris-trade starting five with Wilson Chandler
    {"GROUP_NAME": "B. Simmons-J. Butler-W. Chandler-J. Redick-J. Embiid",
     "MIN": 340, "OFF_RATING": 112.8, "DEF_RATING": 105.1, "NET_RATING": 7.7},

    # Pre-Butler-trade original starting five
    {"GROUP_NAME": "B. Simmons-R. Covington-D. Saric-J. Redick-J. Embiid",
     "MIN": 580, "OFF_RATING": 111.4, "DEF_RATING": 103.9, "NET_RATING": 7.5},

    # Bench-heavy lineup
    {"GROUP_NAME": "T.J. McConnell-F. Korkmaz-J. Bayless-M. Muscala-B. Mitchell",
     "MIN": 95, "OFF_RATING": 103.2, "DEF_RATING": 110.8, "NET_RATING": -7.6},

    # Closing lineup with Embiid + bench guards
    {"GROUP_NAME": "T.J. McConnell-J. Redick-J. Butler-T. Harris-J. Embiid",
     "MIN": 145, "OFF_RATING": 118.9, "DEF_RATING": 102.1, "NET_RATING": 16.8},

    # Small-sample but extreme net rating (illustrates need for shrinkage)
    {"GROUP_NAME": "B. Simmons-J. Butler-T. Harris-F. Korkmaz-J. Embiid",
     "MIN": 8, "OFF_RATING": 138.0, "DEF_RATING": 92.0, "NET_RATING": 46.0},

    # Non-Embiid lineup (Embiid rest minutes)
    {"GROUP_NAME": "T.J. McConnell-J. Butler-T. Harris-J. Redick-B. Mitchell",
     "MIN": 60, "OFF_RATING": 109.0, "DEF_RATING": 109.5, "NET_RATING": -0.5},

    # Defensive-minded bench unit
    {"GROUP_NAME": "T.J. McConnell-F. Korkmaz-R. Covington-D. Saric-A. Ennis",
     "MIN": 75, "OFF_RATING": 102.5, "DEF_RATING": 101.0, "NET_RATING": 1.5},

    # Another small-sample noisy lineup
    {"GROUP_NAME": "J. Bayless-F. Korkmaz-W. Chandler-M. Muscala-J. Embiid",
     "MIN": 12, "OFF_RATING": 95.0, "DEF_RATING": 118.0, "NET_RATING": -23.0},

    # High-minute Simmons/Embiid pairing across various wings
    {"GROUP_NAME": "B. Simmons-J. Butler-T. Harris-M. Muscala-J. Embiid",
     "MIN": 130, "OFF_RATING": 114.0, "DEF_RATING": 106.0, "NET_RATING": 8.0},
]

df = pd.DataFrame(data)
df.to_csv("data/sixers_lineups_2018_19_DEMO.csv", index=False)
print(f"Saved {len(df)} demo lineups to data/sixers_lineups_2018_19_DEMO.csv")
print(df)

# Team overall net rating for 2018-19 76ers (approx, for shrinkage prior)
# Actual reported full-season net rating was around +3.2
team_overall = pd.DataFrame([{"NET_RATING": 3.2, "TEAM": "Philadelphia 76ers", "SEASON": "2018-19"}])
team_overall.to_csv("data/sixers_team_overall_2018_19_DEMO.csv", index=False)
print("\nSaved team overall net rating (demo): 3.2")
