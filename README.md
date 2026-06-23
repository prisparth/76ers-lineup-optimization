# Philadelphia 76ers 2018-19 Lineup Optimization

A lineup analysis project examining 5-man rotation efficiency for the 2018-19
Philadelphia 76ers - a season defined by two major in-season trades (Jimmy
Butler, November 2018; Tobias Harris, February 2019) that repeatedly
reshuffled the team's rotation.

## Objective

Identify which 5-man lineup combinations were most effective (adjusted for
sample size) and compare those rankings against how rotation minutes were
actually distributed, to surface potential gaps between usage and
on-court performance.

## Project structure

```
sixers_lineup_project/
├── 00_demo_data.py        # Generates small illustrative dataset (for testing pipeline)
├── 01_pull_data.py        # Pulls real lineup data from stats.nba.com (run locally)
├── 02_analysis.py         # Cleaning, shrinkage, and Ridge regression (RAPM-style)
├── data/                   # CSV outputs
├── dashboard/
│   └── app.py             # Streamlit dashboard
└── README.md
```

## How to run

1. Install dependencies:
   ```
   pip install nba_api pandas numpy scikit-learn streamlit matplotlib
   ```

2. Pull live data (run on a machine with normal internet access -
   stats.nba.com is sometimes blocked on sandboxed/VPN networks):
   ```
   python 01_pull_data.py
   ```
   This produces `data/sixers_lineups_2018_19_raw.csv` and
   `data/sixers_team_overall_2018_19.csv`.

3. Update `RAW_FILE` and `TEAM_FILE` paths in `02_analysis.py` to point at
   the files from step 2 (instead of the `_DEMO` files), then run:
   ```
   python 02_analysis.py
   ```

4. Launch the dashboard:
   ```
   cd dashboard
   streamlit run app.py
   ```

## Methodology

### 1. Data source
Lineup-level advanced stats (minutes, offensive rating, defensive rating,
net rating) for all 5-man combinations used by the 76ers during the 2018-19
regular season, pulled via the `nba_api` Python package (`LeagueDashLineups`
endpoint, advanced measure type).

### 2. Sample-size filtering
Lineups below a minimum-minutes threshold are flagged separately, since
small-sample net ratings can be extremely noisy (a few good or bad
possessions can swing a lineup's rating by 20+ points).

### 3. Bayesian shrinkage
Rather than dropping small-sample lineups entirely, each lineup's net rating
is shrunk toward the team's season-long average net rating, weighted by how
many minutes that lineup played relative to a "prior weight" of 100
pseudo-minutes:

```
adjusted_net_rating = (net_rating * minutes + team_avg * 100) / (minutes + 100)
```

This means a lineup that played 5 minutes with a +40 net rating gets pulled
heavily toward the team average, while a lineup that played 500 minutes with
a +8 net rating barely moves - reflecting our relative confidence in each
estimate.

### 4. Simplified RAPM (player impact)
To estimate each player's individual contribution to net rating, independent
of who else was on the floor, a Ridge regression is run:

- **Features (X):** binary indicator per player (1 if on the floor in that
  lineup, 0 otherwise)
- **Target (y):** lineup net rating
- **Sample weight:** minutes played
- **Regularization:** Ridge (L2) penalty, needed because lineup combinations
  are highly collinear (most players appear alongside the same teammates
  repeatedly)

This produces an estimate analogous to (a simplified version of) Regularized
Adjusted Plus-Minus.

### 5. Rotation gap analysis
The top 5 lineups by minutes played are compared against the top 5 lineups
by adjusted net rating. Lineups appearing in the efficiency ranking but not
the usage ranking are highlighted as potential under-utilized combinations.

## Key findings

*(Fill in after running on full season data)*

- Top lineup by adjusted net rating: ___
- Most-used lineup: ___
- Highest-impact players per simplified RAPM: ___
- Notable gap(s) between usage and efficiency: ___

## Limitations

- **Sample size:** even a full season produces relatively few minutes for
  many lineup combinations, especially after a mid-season trade disrupts
  continuity.
- **No opponent adjustment:** net ratings aren't adjusted for opponent
  strength or schedule (back-to-backs, home/away).
- **No context variables:** doesn't account for which players were injured,
  in foul trouble, or being rested when certain lineups were/weren't used -
  some "gaps" between usage and efficiency may be fully explained by
  availability, not coaching decisions.
- **Mid-season roster turnover:** the Butler and Harris trades mean some
  lineups simply didn't have time to accumulate large samples - shrinkage
  helps, but doesn't fully solve this.
- **RAPM simplification:** the Ridge regression here doesn't separate
  offense/defense, doesn't use possession-level (stint) data, and uses a
  single regularization parameter rather than cross-validated tuning.

## Possible extensions

- Repeat the analysis separately for the pre-Butler, Butler-era, and
  post-Harris-trade segments of the season to see how lineup value shifted.
- Add opponent-adjusted ratings using opponent-strength as a control.
- Extend the RAPM regression with stint-level (possession) data instead of
  lineup totals.
- Compare 76ers findings against another team for a relative-value
  perspective.
