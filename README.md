# Philadelphia 76ers 2018-19 Lineup Analysis

Which five-man lineups worked best for the 2018-19 76ers, adjusted for sample size, and how
did that compare with how the minutes were actually used? The season was reshaped by two
in-season trades (Jimmy Butler in November 2018, Tobias Harris in February 2019).

**Live app:** add your Streamlit URL here.

## Run it

```
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The repo already contains the real data and results, so the app runs immediately.

## Rebuild from scratch

```
python pull_data.py     # downloads lineup data from the NBA Stats API (needs open internet)
python analysis.py      # writes data/lineups_processed.csv and data/player_impact.csv
```

## Files

| File | What it is |
| --- | --- |
| `pull_data.py` | Pulls 2018-19 lineup and team data with `nba_api` |
| `analysis.py` | Bayesian shrinkage, lineup rankings, cross-validated Ridge player impact |
| `app.py` | Streamlit dashboard (shows a data check line and refuses to run on partial data) |
| `data/sixers_lineups_2018_19_raw.csv` | 518 five-man lineups, advanced stats |
| `data/sixers_team_overall_2018_19.csv` | Team baseline (net rating +2.6) |
| `data/lineups_processed.csv` | Raw data plus adjusted net rating |
| `data/player_impact.csv` | Ridge player-impact estimates |

## Method

1. **Data:** lineup minutes, offensive, defensive and net rating from the NBA Stats API
   (`LeagueDashLineups`, advanced), via `nba_api`.
2. **Shrinkage:** each lineup's net rating is pulled toward the team average, weighted by minutes
   against 100 pseudo-minutes: `(net * min + team_avg * 100) / (min + 100)`.
3. **Player impact (RAPM-style):** Ridge regression of lineup net rating on player on-floor
   indicators, weighted by minutes. The penalty is chosen by 5-fold, minutes-weighted
   cross-validation (selected alpha = 1000).
4. **Gap analysis:** top lineups by adjusted net rating versus top lineups by minutes.

## Results (lineups with 40+ minutes)

- **Top lineup by adjusted net rating:** Redick - Harris - Butler - Embiid - Simmons
  (161 min, +19.4 raw, +13.0 adjusted).
- **Most-used lineup:** Redick - Chandler - Butler - Embiid - Simmons (293 min, +12.6 raw,
  +10.1 adjusted).
- **Highest player impact:** Embiid +4.1, Butler +2.8, Redick +2.2.
- **Usage gaps:** three lineups with Muscala or Shamet rank in the top five by adjusted net
  rating but not by minutes (61-68 minutes each). These are small samples, so treat them as
  leads for film review.

## Limitations

- Small samples for most lineups, worsened by mid-season trades.
- No opponent or schedule adjustment, and no injury or rest context.
- Player impact comes from lineup totals, not possession-level stints, and does not separate
  offense from defense. Treat it as directional.
