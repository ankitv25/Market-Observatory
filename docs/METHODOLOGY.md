# Market Observatory methodology

## Reading an edition

The [live dashboard](https://ankitv25.github.io/Market-Observatory/) runs on GitHub Pages and opens with the cross-asset overview. The repository landing page is the text companion. GitHub renders the three SVG charts and Markdown tables directly. The standalone HTML file contains an interactive chart reader and the same edition data. Download the file to open it locally. No server or API token is needed to read a saved edition.

Each instrument retains its observation date. The compilation time indicates when the edition was assembled. Sector panels measure US sector ETF price returns. The market tape includes index levels, ETF prices, FX quote units and individual futures contracts. The previous observation and six-month anchor are available in the JSON snapshot. The market summaries describe associations and arithmetic; they do not attribute a cause to a day’s price move.

## Sources and calculations

- Yahoo Finance daily history supplies dated price observations. The collector excludes uncompleted daily bars. Compatible existing public Convexity Lab history can fill a source outage with an explicit archive label. Previous verified rows can carry forward on failure. Check the dated source notes for every instrument.
- Daily change equals last price less previous observed price in that row's own units. Daily percentage uses the previous positive price. Six-month price return compares the last price with the last observation on or before the date six calendar months earlier. Missing anchors remain blank. ETF distributions are excluded.
- A futures row identifies a named delivery month. Its change compares vendor daily closes on that contract. A six-month change is the price move of that same contract across the window, if available. Rolled or collateralized strategy returns require separate accounting.
- Treasury supplies nominal par yields. The Federal Reserve's H.15 constant maturity data provide an official fallback. Yield changes are basis points. The 2s10s spread equals ten-year less two-year yield. The chart and macro panel carry their own dates.
- [Macro Regime Score](https://github.com/ankitv25/Macro-Regime-Score) supplies the confirmed monthly regime. The collector verifies that the metadata, composite and pillar scores reconcile for the same month at one repository revision.
- The research notebook evaluates sector participation and historical beta using matched daily price-return endpoints. It identifies model inputs, minimum sample and benchmark. No portfolio risk or alpha is inferred from these ETF betas.
- Price, quote currency, benchmark and quality are visible in [the source ledger](../dashboard/SOURCES.md). The archive contains original market editions. Reproduce an edition’s charts by checking out its publication commit and running the render-only command.

## Operating cadence

GitHub Actions requests two refreshes on weekdays at 11:45 and 23:30 UTC. These correspond to 06:45 and 18:30 New York during standard time and 07:45 and 19:30 during daylight time. GitHub scheduling is best effort. A morning edition can contain prior US closes. Each venue's observation date remains visible through weekends and holidays.

The workflow serializes publication, validates files before committing, pushes the new edition, compares the published README/data/chart/ledger blobs through GitHub's API, and attaches the offline reader to the run. Failed runs are visible in Actions. A refresh that cannot assemble core coverage leaves the previous published edition intact. Concurrent external pushes cause publication to fail safely; re-run against the current main branch.

## Running locally

Requires Python 3.11+ and network access for collection. From the repository root:

```sh
python3 scripts/refresh.py
python3 scripts/verify.py
```

To rebuild the reader and charts from the saved edition without fetching data:

```sh
python3 scripts/refresh.py --render-only
```

The [work log](../WORKLOG.md) records implementation changes. The [refresh ledger](../CADENCE.md) records data editions. The original thesis work and private repository inputs are outside this public collection.

## Live rendering and portfolio books

Each successful edition triggers a Pages deployment. The publishing job checks the bytes returned by the live URL against the built dashboard. The comparison chart aligns observed dates and rebases both instruments at their first common observation within the selected window. Sector tiles switch between daily and six-month price returns. The portfolio lens reads the five public portfolio books at refresh time, preserving their own as-of dates, forecast risk and sleeve contributions. These model risk shares are distinct from daily portfolio performance.
