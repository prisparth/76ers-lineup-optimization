"""
Step 9: Streamlit dashboard for the 76ers 2018-19 lineup analysis.

Run with:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="76ers 2018-19 Lineup Optimization", layout="wide")

st.title("Philadelphia 76ers 2018-19: Lineup Optimization Dashboard")
st.markdown(
    """
    This dashboard analyzes 5-man lineup combinations from the 76ers'
    2018-19 season - a season marked by two major trades (Jimmy Butler in
    Nov 2018, Tobias Harris in Feb 2019), making rotation continuity an
    interesting analytical challenge.
    """
)

# ---- LOAD DATA ----
df = pd.read_csv("data/lineups_processed.csv")
player_impact = pd.read_csv("data/player_impact.csv", index_col=0)

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")
min_threshold = st.sidebar.slider(
    "Minimum minutes played",
    min_value=int(df["MIN"].min()),
    max_value=int(df["MIN"].max()),
    value=int(df["MIN"].min()),
)

filtered = df[df["MIN"] >= min_threshold]

# ---- TOP LINEUPS TABLE ----
st.header("Lineup Rankings (Adjusted Net Rating)")
st.markdown(
    "**Adjusted net rating** shrinks each lineup's raw net rating toward the "
    "team average based on minutes played, so small-sample extreme outliers "
    "don't dominate the rankings."
)

display_cols = ["GROUP_NAME", "MIN", "OFF_RATING", "DEF_RATING", "NET_RATING", "adj_net_rating"]
st.dataframe(
    filtered.sort_values("adj_net_rating", ascending=False)[display_cols]
    .rename(columns={
        "GROUP_NAME": "Lineup",
        "MIN": "Minutes",
        "OFF_RATING": "Off Rating",
        "DEF_RATING": "Def Rating",
        "NET_RATING": "Net Rating (raw)",
        "adj_net_rating": "Net Rating (adjusted)"
    }),
    use_container_width=True,
)

# ---- SCATTER: MINUTES VS ADJUSTED NET RATING ----
st.header("Minutes Played vs. Adjusted Net Rating")
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(filtered["MIN"], filtered["adj_net_rating"], s=80, alpha=0.7)
for _, row in filtered.iterrows():
    ax.annotate(
        row["GROUP_NAME"].split("-")[-1],  # label by last player (often Embiid) for brevity
        (row["MIN"], row["adj_net_rating"]),
        fontsize=8,
        alpha=0.7,
    )
ax.axhline(0, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Minutes Played")
ax.set_ylabel("Adjusted Net Rating")
ax.set_title("Lineup Usage vs. Efficiency")
st.pyplot(fig)

st.markdown(
    """
    **How to read this chart:** lineups in the upper-right (high minutes,
    high net rating) are validated rotation choices. Lineups in the
    upper-left (low minutes, high adjusted net rating) may represent
    *underused* combinations worth revisiting. Lineups in the lower-right
    (high minutes, low/negative net rating) may represent rotation patterns
    worth reconsidering - though context (matchups, injuries, star rest)
    always matters.
    """
)

# ---- PLAYER IMPACT CHART ----
st.header("Estimated Individual Player Impact (Simplified RAPM)")
st.markdown(
    """
    Using a Ridge regression of lineup net ratings (weighted by minutes) on
    binary player-presence indicators, this estimates each player's
    individual contribution to net rating, isolated from who else is on the
    floor. This is a **simplified** version of RAPM - it doesn't account for
    opponent strength, and with limited lineup data the estimates carry
    significant uncertainty.
    """
)

fig2, ax2 = plt.subplots(figsize=(8, 6))
player_impact_sorted = player_impact.sort_values("estimated_impact")
colors = ["crimson" if v < 0 else "steelblue" for v in player_impact_sorted["estimated_impact"]]
ax2.barh(player_impact_sorted.index, player_impact_sorted["estimated_impact"], color=colors)
ax2.axvline(0, color="black", linewidth=0.8)
ax2.set_xlabel("Estimated Impact on Net Rating")
st.pyplot(fig2)

# ---- ROTATION GAP ANALYSIS ----
st.header("Rotation Gap: Actual Usage vs. Recommended")
top_by_minutes = df.sort_values("MIN", ascending=False).head(5)
top_by_adj = df.sort_values("adj_net_rating", ascending=False).head(5)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Most-Used Lineups")
    st.dataframe(top_by_minutes[["GROUP_NAME", "MIN", "adj_net_rating"]], use_container_width=True)
with col2:
    st.subheader("Top Lineups by Adjusted Net Rating")
    st.dataframe(top_by_adj[["GROUP_NAME", "MIN", "adj_net_rating"]], use_container_width=True)

st.markdown(
    """
    **Insight:** compare the two tables above. Any lineup that appears in
    the right table but not the left represents a combination with strong
    efficiency that wasn't given proportional minutes - a candidate for
    coaching staff discussion (with appropriate caveats about sample size
    and matchup context).
    """
)

st.markdown("---")
st.caption(
    "Data: NBA Stats API (stats.nba.com) via nba_api. "
    "Methodology: Bayesian shrinkage toward team average net rating; "
    "Ridge regression for simplified individual player impact (RAPM-style)."
)
