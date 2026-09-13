# Consensus Portfolio: two-year A/B/C test

Open report.html directly. This research is separate from the app and is not served by it.

Frozen test: September 13, 2024 at approximately 3:30 p.m. New York time through September 11, 2026 close. Current seven-stock weights are frozen in portfolio.json. This is a retrospective basket test, not a point-in-time fund-selection backtest.

A sells a portion of each day's winner to buy its paired loser; B holds initial shares; C sells a portion of the loser to buy the winner. Pair the greatest positive mover with the greatest negative mover, then the next pair. Every stock participates at most once daily. Transfer the return gap as a decimal times the smaller current dollar position. Portfolio weights evolve without resetting. Amounts are calculated independently from each strategy's evolving positions.

Signals: the hourly bar ending at 15:30 divided by previous daily close, minus one. Execution: opening price of the 15:30 hourly bar. No future bar close is used to trigger that bar's opening trade. Executions are estimated from hourly data, not precise quotes or executable fills.

Fees/slippage assumptions: 0, 5, 10, 25 basis points per side, including initial buys. Dividend events accrue cash before ex-date transfers using prior-close shares; no cash interest/reinvestment. No income taxes, dividend withholding, or ADR fees. The frozen period contains no stock split events; the runner refuses to proceed if splits appear in other inputs until their treatment is validated. Fractional shares and no leverage. All results are marked at the final daily close, without liquidation costs.

500 sessions are valued. 494 have complete 15:30 data; the first establishes positions. Five early closes and January 30, 2026 (missing intraday inputs) are skipped for trading. All skips are enumerated in results.json and the report; no stale trade-price substitution occurs.

Files:
- data/: 14 raw Yahoo Finance chart responses, each wrapped with exact URL and retrieval timestamp.
- portfolio.json: starting seven holdings and model snapshot timestamp.
- run.py: deterministic calculation; reads cached data, never refetches or modifies the portfolio app.
- test_run.py: eight calculation/data regression tests.
- render.py: builds the standalone HTML report only.
- results.json: all four cost assumptions, full trade ledgers, equity curves, sources, and skips.
- equity.csv and trades.csv: base-case (5 bps per side) audit tables.

From this research directory (Python 3.9 or later):

    python3 run.py
    python3 -m unittest discover -s . -p 'test_*.py' -v
    python3 render.py

No live-trading rule, scheduled test, or brokerage order is enabled by this study.
