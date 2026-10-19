"""
Step 9: Streamlit dashboard for the 76ers 2018-19 lineup analysis.

Run with:
    streamlit run dashboard/app.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="76ers 2018-19 Lineup Optimization", layout="wide")

SIXERS_BLUE = "#006BB6"
SIXERS_RED = "#ED174C"
SIXERS_NAVY = "#002B5C"
SIXERS_SILVER = "#C4CED4"
SIXERS_WHITE = "#FFFFFF"


def section_label(icon_text, title, description):
    st.markdown(
        f"""
        <div class="section-label">
            <div class="section-icon">{icon_text}</div>
            <div>
                <h2>{title}</h2>
                <p>{description}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
        :root {
            --sixers-blue: #006BB6;
            --sixers-red: #ED174C;
            --sixers-navy: #002B5C;
            --sixers-silver: #C4CED4;
            --sixers-ice: #F5F8FB;
        }

        .stApp {
            background:
                linear-gradient(90deg, rgba(237, 23, 76, .08), transparent 24%, transparent 76%, rgba(0, 107, 182, .10)),
                #F8FAFD;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--sixers-navy), var(--sixers-blue));
        }

        [data-testid="stSidebar"] * {
            color: white !important;
        }

        .block-container {
            padding-top: 2rem;
        }

        .hero {
            background: var(--sixers-navy);
            border-bottom: 10px solid var(--sixers-blue);
            border-top: 10px solid var(--sixers-red);
            box-shadow: inset 0 0 0 2px rgba(196, 206, 212, .55);
            color: white;
            margin-bottom: 1.4rem;
            padding: 2rem 2.25rem;
        }

        .hero h1 {
            color: white;
            font-size: 2.55rem;
            letter-spacing: 0;
            line-height: 1.05;
            margin: 0 0 .7rem;
        }

        .hero p {
            color: #E8EEF5;
            font-size: 1.05rem;
            margin: 0;
            max-width: 980px;
        }

        .summary-grid {
            display: grid;
            gap: .8rem;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            margin: .6rem 0 1.4rem;
        }

        .summary-card {
            background: white;
            border: 1px solid #D9E2EA;
            border-left: 7px solid var(--sixers-red);
            min-height: 118px;
            padding: 1rem;
        }

        .summary-card:nth-child(2) {
            border-left-color: var(--sixers-blue);
        }

        .summary-card:nth-child(3) {
            border-left-color: var(--sixers-navy);
        }

        .summary-card .badge {
            align-items: center;
            background: var(--sixers-blue);
            clip-path: polygon(50% 0, 100% 30%, 100% 70%, 50% 100%, 0 70%, 0 30%);
            color: white;
            display: inline-flex;
            font-size: .78rem;
            font-weight: 800;
            height: 48px;
            justify-content: center;
            margin-bottom: .6rem;
            width: 56px;
        }

        .summary-card:nth-child(1) .badge {
            background: var(--sixers-red);
        }

        .summary-card:nth-child(3) .badge {
            background: var(--sixers-navy);
        }

        .summary-card h3 {
            color: var(--sixers-navy);
            font-size: 1rem;
            margin: 0 0 .35rem;
        }

        .summary-card p {
            color: #263746;
            font-size: .93rem;
            margin: 0;
        }

        .section-label {
            align-items: center;
            display: flex;
            gap: 1rem;
            margin: 1.6rem 0 .65rem;
        }

        .section-icon {
            align-items: center;
            background: linear-gradient(135deg, var(--sixers-red), var(--sixers-blue));
            clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
            color: white;
            display: inline-flex;
            flex: 0 0 76px;
            font-size: .78rem;
            font-weight: 900;
            height: 76px;
            justify-content: center;
            text-align: center;
        }

        .section-label h2 {
            color: var(--sixers-navy);
            font-size: 1.45rem;
            margin: 0 0 .25rem;
        }

        .section-label p,
        .readout {
            color: #263746;
            font-size: .98rem;
            margin: 0;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #D9E2EA;
        }

        .gap-table-title {
            align-items: center;
            color: var(--sixers-navy);
            display: flex;
            font-size: 1.08rem;
            font-weight: 800;
            line-height: 1.2;
            margin: 0 0 .55rem;
            min-height: 2.7rem;
        }

        @media (max-width: 800px) {
            .summary-grid {
                grid-template-columns: 1fr;
            }

            .section-label {
                align-items: flex-start;
                flex-direction: column;
                gap: .65rem;
            }

            .hero {
                padding: 1.35rem;
            }

            .hero h1 {
                font-size: 2rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- LOAD DATA ----
ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "lineups_processed.csv")
player_impact = pd.read_csv(ROOT / "data" / "player_impact.csv", index_col=0)

if len(df) < 100:
    st.error(
        f"Only {len(df)} lineups loaded. The full 2018-19 data has 518. "
        "Re-run analysis.py on data/sixers_lineups_2018_19_raw.csv and commit the new CSVs."
    )
    st.stop()
st.caption(
    f"Data check: {len(df)} lineups, {df['MIN'].sum():,.0f} lineup-minutes, "
    f"{len(player_impact)} players (2018-19 regular season)."
)

st.markdown(
    """
    <div class="hero">
        <h1>Philadelphia 76ers 2018-19 Lineup Optimization</h1>
        <p>
            A jersey-inspired dashboard for comparing how the 2018-19 76ers actually used
            their five-man groups against how those lineups performed after small-sample
            shrinkage. The analysis focuses on minutes, offensive rating, defensive rating,
            raw net rating, adjusted net rating, and estimated player impact.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="summary-grid">
        <div class="summary-card">
            <div class="badge">5</div>
            <h3>Five-player lineup rows</h3>
            <p>Each row represents one 76ers lineup combination and the ratings it produced while those five players shared the floor.</p>
        </div>
        <div class="summary-card">
            <div class="badge">NET</div>
            <h3>Adjusted net rating is the main score</h3>
            <p>Raw net rating is blended toward the team average, so lineups with only a few minutes do not overpower the rankings.</p>
        </div>
        <div class="summary-card">
            <div class="badge">GAP</div>
            <h3>Usage vs. efficiency</h3>
            <p>The dashboard highlights places where productive lineups may have received fewer minutes than their performance suggests.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Rotation filter")
st.sidebar.markdown(
    "Use the minutes threshold to hide lineups with very small samples before reading the table and charts."
)
DEFAULT_MIN_MINUTES = 40
min_threshold = st.sidebar.slider(
    "Minimum minutes played",
    min_value=int(df["MIN"].min()),
    max_value=int(df["MIN"].max()),
    value=min(DEFAULT_MIN_MINUTES, int(df["MIN"].max())),
)

filtered = df[df["MIN"] >= min_threshold]

# ---- TOP LINEUPS TABLE ----
section_label(
    "RANK",
    "Lineup Rankings by Adjusted Net Rating",
    "This table lists every qualifying five-man lineup, sorted by adjusted net rating. Minutes show the sample size; offensive and defensive ratings show points scored and allowed per 100 possessions; raw net rating is the direct margin; adjusted net rating is the stabilized version used for ranking.",
)

display_cols = ["GROUP_NAME", "MIN", "OFF_RATING", "DEF_RATING", "NET_RATING", "adj_net_rating"]
st.dataframe(
    filtered.sort_values("adj_net_rating", ascending=False)[display_cols].rename(
        columns={
            "GROUP_NAME": "Lineup",
            "MIN": "Minutes",
            "OFF_RATING": "Off Rating",
            "DEF_RATING": "Def Rating",
            "NET_RATING": "Net Rating (raw)",
            "adj_net_rating": "Net Rating (adjusted)",
        }
    ),
    width="stretch",
)

# ---- SCATTER: MINUTES VS ADJUSTED NET RATING ----
section_label(
    "MAP",
    "Minutes Played vs. Adjusted Net Rating",
    "Each dot is a five-player lineup. The x-axis shows how much that lineup played, and the y-axis shows its adjusted scoring margin per 100 possessions. Dots above zero helped the 76ers outscore opponents after adjustment.",
)
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(SIXERS_WHITE)
ax.set_facecolor("#F5F8FB")
ax.scatter(
    filtered["MIN"],
    filtered["adj_net_rating"],
    alpha=0.82,
    color=SIXERS_BLUE,
    edgecolor=SIXERS_RED,
    linewidth=1.2,
    s=95,
)
for _, row in filtered.iterrows():
    ax.annotate(
        row["GROUP_NAME"].split("-")[-1],
        (row["MIN"], row["adj_net_rating"]),
        alpha=0.7,
        fontsize=8,
    )
ax.axhline(0, color=SIXERS_RED, linestyle="--", linewidth=1.2)
ax.grid(color=SIXERS_SILVER, alpha=0.35, linewidth=0.8)
ax.set_xlabel("Minutes Played")
ax.set_ylabel("Adjusted Net Rating")
ax.set_title("Lineup Usage vs. Efficiency")
st.pyplot(fig)

st.markdown(
    """
    <p class="readout">
        <strong>What you are seeing:</strong> upper-right dots are lineups that were both used often
        and performed well. Upper-left dots are efficient lineups with limited minutes, which makes
        them candidates for further review. Lower-right dots are heavily used lineups that performed
        below the break-even line and may require matchup, injury, or role context.
    </p>
    """,
    unsafe_allow_html=True,
)

# ---- PLAYER IMPACT CHART ----
section_label(
    "IMPACT",
    "Estimated Individual Player Impact",
    "This chart estimates how each player is associated with lineup net rating after accounting for which teammates appeared in the same five-man groups. Positive bars indicate a player was tied to stronger lineup margins in this simplified RAPM-style model.",
)

fig2, ax2 = plt.subplots(figsize=(8, 6))
fig2.patch.set_facecolor(SIXERS_WHITE)
ax2.set_facecolor("#F5F8FB")
player_impact_sorted = player_impact.sort_values("estimated_impact")
colors = [SIXERS_RED if v < 0 else SIXERS_BLUE for v in player_impact_sorted["estimated_impact"]]
ax2.barh(player_impact_sorted.index, player_impact_sorted["estimated_impact"], color=colors)
ax2.axvline(0, color=SIXERS_NAVY, linewidth=0.9)
ax2.grid(axis="x", color=SIXERS_SILVER, alpha=0.35, linewidth=0.8)
ax2.set_xlabel("Estimated Impact on Net Rating")
st.pyplot(fig2)

# ---- ROTATION GAP ANALYSIS ----
section_label(
    "GAP",
    "Rotation Gap: Actual Usage vs. Recommended",
    "The left table shows the five lineups that received the most minutes. The right table shows the five lineups with the best adjusted net rating. Comparing them reveals whether the highest-performing groups also received the largest roles.",
)
top_by_minutes = df.sort_values("MIN", ascending=False).head(5)
top_by_adj = df.sort_values("adj_net_rating", ascending=False).head(5)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="gap-table-title">Most-Used Lineups</div>', unsafe_allow_html=True)
    st.dataframe(top_by_minutes[["GROUP_NAME", "MIN", "adj_net_rating"]], width="stretch")
with col2:
    st.markdown(
        '<div class="gap-table-title">Top Lineups by Adjusted Net Rating</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(top_by_adj[["GROUP_NAME", "MIN", "adj_net_rating"]], width="stretch")

st.markdown(
    """
    <p class="readout">
        <strong>What the comparison means:</strong> a lineup that appears on the right but not the
        left produced strong adjusted results without being one of the most-used groups. That does
        not automatically mean it should play more, but it gives coaches and analysts a precise
        starting point for film review, matchup checks, and availability context.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.caption(
    "Data: NBA Stats API (stats.nba.com) via nba_api. "
    "Methodology: Bayesian shrinkage toward team average net rating; "
    "Ridge regression for simplified individual player impact (RAPM-style)."
)
