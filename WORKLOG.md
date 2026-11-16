# Work log

| Date | Delivery | Evidence |
|---|---|---|
| 2026-11-07 | Opened the public Market Observatory repository. Built the README edition, S&P 500 masthead, sector chart, Treasury curve, market tape and offline chart reader. | [Dashboard](README.md) · [Charts](assets/) · [Reader source](scripts/reader.html) |
| 2026-11-07 | Integrated market histories, named futures contracts, official Treasury/H.15 curves, confirmed MRS vintage, and sector risk calculations. | [Source ledger](dashboard/SOURCES.md) · [Research notebook](dashboard/RESEARCH.md) |
| 2026-11-07 | Added weekday collection, immutable dated snapshots, run ledger, artifact validation and GitHub readback. | [Workflow](.github/workflows/refresh.yml) · [Edition ledger](CADENCE.md) |
| 2026-11-07 | Shipped the GitHub Pages monitor with benchmark comparison, sector rotation, rates and macro, portfolio risk and searchable market tape. | [Live dashboard](https://ankitv25.github.io/Market-Observatory/) · [Publication workflow](.github/workflows/pages.yml) |

## November 8 desk design edition

Twelve navigable review pages with authored tables, sample desk commentary, analytical exhibits and proposed interactions. The design uses the November 7 archived edition. [Desk designs](https://ankitv25.github.io/Market-Observatory/design/) · [Source manuscript](docs/DESK_DESIGNS.md)

## November 7 project review

Three independent reviewers evaluated desk depth, portfolio-manager workflow and release controls. The [delivery plan](docs/PROJECT_PLAN.md), [five-page research brief](docs/Market-Observatory-Research.pdf), [milestones](https://github.com/ankitv25/Market-Observatory/milestones) and [financial quality workflow](.github/workflows/quality.yml) now govern the next release. Live site remains the prior edition.

## Earlier build queue

1. Add real Treasury yields and breakevens alongside nominal yields. Verify the tenors, units and release timestamps.
2. Add a dated FOMC event card and a forecast-versus-outcome record. Resolve the source and horizon of each expectation.
3. Extend credit with dated OAS and duration where eligible. Add full repricing and risk-factor attribution when the required inputs are available.
4. Add explicit user-authored public theses with revision history. Company comparison and the equity valuation agent belong to the separate equity research project.

## November 13 market homepage

Rebuilt the live opening screen with a benchmark strip, a dated closing brief, six asset-class rows, same-session gainers and decliners, and regional index boards. The historical Market Board entry now opens the current edition.


## November 16 daily briefing and portfolio monitor

Expanded the overview into eight regional and asset desks with original dated commentary, levels, absolute moves, one-month sector rankings, leadership changes, size/style spreads, automatically selected active charts, and portfolio thesis evidence.

The dedicated portfolio monitor covers all five published books. NAV and reference histories, underwater charts, return scorecards, cumulative holding and modeled factor attribution, reconciled completed-session contributors, costs, concentration, construction constraints and scenarios retain their source vintages. Portfolio ingestion pins one source revision and verifies its NAV arithmetic and attribution. A daily decomposition is shown only when it reconciles to the corresponding dated NAV.

The refresh schedule now targets 07:17, 13:17, 18:47 and 22:47 America/New_York on weekdays, plus 10:17 on weekends. Hourly checks at minute 43 recover missed targets. The dashboard shows actual compilation times, next targets, observation dates and the recent run history. An open reader checks for a newer edition every five minutes.

Validation covers 25 Python regressions, browser controls and layouts at 320, 390, 768 and 1440 pixels, and replay of historical editions through all five views. Design references were inspected at [Bloomberg Markets](https://www.bloomberg.com/markets) and [WSJ Market Data](https://www.wsj.com/market-data). Commentary is calculated from this edition's observations.
