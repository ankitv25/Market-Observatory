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

The requested weekday collection targets are **07:17 international morning, 09:00 US pre-open, 12:30 midday, 16:30 US close and 22:47 final reconciliation**, in America/New_York. Weekends target 10:17. Catch-up checks at minutes 13, 28, 43 and 58 collect a missed slot; they also retry hourly when completed US core prices remain behind. The exchange calendar includes the published 2026–2028 US holidays and early closes. Beyond that dated calendar, calendar coverage is explicitly unverified.

[GitHub documents that scheduled starts can be delayed or dropped](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). These are requested targets, not a guaranteed execution SLA. Each executed check records lateness and intervening missed slots. A missed intraday edition cannot be reconstructed by a later close. An independently hosted scheduler can invoke the `market-refresh` repository dispatch endpoint; no independent scheduler is configured by this release.

Collection and validation run in an isolated candidate directory. Failed candidates cannot replace the reader. The workflow records collection, quality checks, repository publication and remote verification separately; a source transport success does not imply a fresh observation. Failed sources retain their dated earlier observations where allowed. Every attempt, including skips and failures, gets a durable JSON record under `runs/YYYY-MM/`; rejected candidates are separately retained. The bounded `runs/latest.json` index is read by the dashboard's **Refresh & reliability** tab, including failures occurring after the last successful edition. Offline readers use their embedded log snapshot.

Pages compares a content manifest, waits for the uploaded artifact to become visible, retries one failed deployment, and compares the served HTML bytes with the validated artifact. No-op checks record a skip without uploading the identical site. Publication records also enter the durable ledger. The open reader checks for a new edition and new run records every five minutes.

## Running locally

Requires Python 3.11+ and network access for collection. From the repository root:

```sh
python3 scripts/pipeline.py refresh
```

To rebuild the reader and charts from the saved edition without fetching data:

```sh
python3 scripts/refresh.py --render-only
```

The [work log](../WORKLOG.md) records implementation changes. The [refresh ledger](../CADENCE.md) records data editions. The original thesis work and private repository inputs are outside this public collection.

## Live rendering and portfolio books

Each successful edition triggers a Pages deployment. The publishing job checks the bytes returned by the live URL against the built dashboard. The comparison chart aligns observed dates and rebases both instruments at their first common observation within the selected window. Sector tiles switch between daily and six-month price returns. The portfolio lens reads the five public portfolio books at refresh time, preserving their own as-of dates, forecast risk and sleeve contributions. These model risk shares are distinct from daily portfolio performance.

## Market intelligence and historical story

Each newly collected edition contains `intelligence`: the exact observations, eligibility, rules, thresholds, votes, confidence, commentary and portfolio review considerations available then. Its immutable edition file is the record. The dashboard links the ten latest published assessments; the complete story remains in the edition archive and Git history. Earlier editions without this model are not retroactively labelled with a market call.

The model compares **one, five and 21 common reference-session intervals**, with matched price endpoints for every input. Six equal-weight domains cover US equity direction, international equity direction, US sector participation, small-cap/equal-weight participation, VIX and HYG relative to SHY. US-listed scored inputs must reach the expected completed US session. An old reference session cannot support a current regime. Treasury, dollar, commodity and monthly macro observations retain their separate freshness and explanatory roles. Stale context is labelled and excluded from current interpretation.

Risk-on requires at least two thirds of eligible domains voting positively and at most one opposing vote; risk-off is symmetric. At least four of six domains, one equity-direction domain and one volatility/credit domain are necessary. Otherwise the model reports insufficient evidence. Neutral bands prevent tiny daily changes from generating directional votes. Longer-window price thresholds scale by the square root of the interval count; sector breadth uses fixed 70%/30% bands. The full edition includes the exact thresholds.

**Evidence confidence is a heuristic, not a forecast probability:** 100 × eligible domains / 6 × larger directional vote count / eligible domains. The equity-related domains are correlated, so this is not six independent economic confirmations. HYG/SHY relative price performance includes duration and distribution effects; it is not a measured change in credit spreads. Daily funding liquidity and daily credit-spread series are missing, so the model cannot confirm a liquidity crisis from these inputs. Regime transitions compare the preceding window of equal length; the separately archived story shows what was actually published at the time.

[Federal Reserve staff research](https://www.federalreserve.gov/econres/notes/feds-notes/updating-the-recession-risk-and-the-excess-bond-premium-20161006.html) supplies monthly Gilchrist–Zakrajšek corporate credit spreads and the excess bond premium. These retain their observation month, are displayed in basis points from percentage-point source units, and carry no daily vote. Monthly macro and credit context expire after 45 calendar days following the observation period end. Recession probability columns are not collected or presented.

Portfolio implications are conditional risk-review considerations. Strategic exposure is tied to the mandate and dated macro context; tactical review uses eligible market signals and horizon agreement. No target weight, hedge size or expected return is inferred from this uncalibrated model.

## Session quotes and completed analytics

Cash benchmark quote cards can show a newer timestamped vendor regular-session quote, with the change anchored to the prior verified daily price. This enables a midday view without treating an unfinished daily bar as a close. Daily analytics, sector comparisons and regime detection continue to use completed observations. Quotes can be delayed and are labelled with their actual timestamp. Named futures contracts retain their verified daily price basis.
