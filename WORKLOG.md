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
