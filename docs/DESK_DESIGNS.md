# Market Observatory · Desk designs

Design edition based on the November 7 archive and market observations through November 6, 2026. Figures are price changes unless stated otherwise. Proposed fields that need new inputs are listed within the relevant desk. The analysis below is an editorial example for this edition. No personal investment thesis is attributed to the owner.

## Market board

### The six desks at the close

| Desk | Primary observation | Daily move | Second observation | Daily move | Through |
|---|---|---:|---|---:|---|
| Equities | S&P 500 · 7,376.86 | +23.13 pts | Euro STOXX 50 · 6,170.49 | −61.05 pts | Nov 6, local closes |
| Sovereign rates | US 2Y · 4.46% | −12 bp | US 10Y · 4.84% | −6 bp | Nov 5 |
| Credit | IG ETF LQD · $104.53 | −0.12% | HY ETF HYG · $77.23 | −0.06% | Nov 6 |
| FX | Dollar index · 102.30 | +0.74% | USD/JPY · 157.498 | −0.54% | Nov 6, vendor close |
| Commodities | Dec WTI · $90.83/bbl | +$0.31 | Dec copper · $6.238/lb | −$0.0325 | Nov 6, contract closes |
| Alternatives | Listed property VNQ · $95.73 | −0.52% | Managed futures DBMF · $31.48 | +1.29% | Nov 6 |

### The close in context

US stocks finished higher, but the advance depended on what you owned. The S&P 500 gained 0.31%, while the equal-weight ETF fell 0.38% and eight of eleven sector ETFs declined. Small caps also advanced. That combination calls for separate readings of index concentration and size leadership. A single breadth score would obscure the small-cap move.

### Signals worth carrying into the next session

| Signal | Evidence today | Longer comparison | Next observation |
|---|---|---|---|
| Growth leadership | IWF beat IWD by 1.62 pp | Growth trailed value by 18.53 pp across six months | Does growth continue to lead when more sectors advance? |
| US curve | The 2Y fell twice as far as the 10Y | The 2s10s slope widened to +38 bp | Check the policy path before interpreting the move as Fed repricing |
| Diversification | Latest 63 matched S&P–IEF returns correlated +0.06 | Preceding disjoint window was +0.48 | Recheck the path and the downside sample after the next selloff |

### Design contract

Land on the board. Keep desks in a fixed order and show native moves and observation dates without scrolling on desktop. Selecting a desk opens its own analysis. Below the board, show the three dated signals and upcoming releases. On mobile show compact desk rows first; put extended horizons and source notes inside the row. Restore the selected edition when returning from a drilldown.

## Market tape

### Session sheet

| Region | Instrument | Close | Points | 1D | 6M | Basis |
|---|---|---:|---:|---:|---:|---|
| US | S&P 500 | 7,376.86 | +23.13 | +0.31% | +0.16% | Cash index |
| US | Nasdaq 100 | 26,989.99 | +360.18 | +1.35% | −5.63% | Cash index |
| Euro area | Euro STOXX 50 | 6,170.49 | −61.05 | −0.98% | +2.38% | Cash index |
| Japan | Nikkei 225 | 57,434.77 | -3,643.13 | -5.96% | -3.49% | Cash index |

@chart tape

### What the tape establishes

The Nasdaq 100 gained 1.35% in its US session while Euro STOXX 50 lost 0.98% in its local session. A reader comparing the closes gets geographic dispersion. To call one move a reaction to the other would require event timestamps and overlapping trading hours. The market tape should show venue and time before offering that interpretation.

### Instrument detail

| Field group | Visible columns or values | Reader use |
|---|---|---|
| Identity | Name, symbol, venue, asset class, currency, unit, proxy status | Distinguish an ETF price from index points |
| Observation | Close, comparison close, dates, session, source, stale state | Verify the subtraction without leaving the page |
| Horizon | 1D, 5 sessions, 1M, 3M, 6M, YTD, 1Y, actual anchors | Select a horizon and see the same date basis in the chart |
| Risk | Window high/low, drawdown, realized volatility, sample | Place the move in its own recent distribution |

### Design contract

Default to grouped regional closes, then covered assets. Sort only within comparable return units; use a separate basis-point view for yields. Selecting a row opens a dated price path and lookup details beside the table. Filters narrow the universe and preserve the edition. A missing eligible close gets its reason and last valid date.

## Equities

### Leadership across two horizons

| Exposure | Vehicle | 1D | 6M | Interpretation |
|---|---|---:|---:|---|
| US large cap | S&P 500 index | +0.31% | +0.16% | Headline benchmark |
| US equal weight | RSP | −0.38% | +5.47% | Participation proxy |
| Large growth | IWF | +1.26% | −8.73% | Short rebound within a weaker six-month trend |
| Large value | IWD | −0.36% | +9.80% | Longer leadership survived a weak day |
| US small cap | IWM | +0.99% | −4.58% | Size participation, separate from the large-cap style split |

@chart equity

### What changed in leadership

A large-growth investor and a large-value investor experienced different markets on November 6. Growth beat value by 1.62 percentage points that session, yet lagged by 18.53 points over six months. The Russell 2000 also rose, so the day's strength reached beyond large-cap growth. Watch whether equal weight and more industries participate over the next several closes before revising the longer-horizon leadership view.

### Nine-cell style matrix · six-month price return

| Size | Value | Blend | Growth |
|---|---|---|---|
| Large | IWD · +9.80% | Matched-family blend series required | IWF · −8.73% |
| Mid | Mid-value series required | Mid-blend series required | Mid-growth series required |
| Small | Small-value series required | IWM broad small-cap proxy · −4.58% | Small-growth series required |

The blanks are meaningful. Combining an arbitrary mid-cap ETF with a different style methodology can manufacture a size effect. Keep the chosen index family, breakpoints, reconstitution dates and return basis visible when completing the matrix.

### Sector leaders seen from two horizons

| Sector proxy | Daily price return | Six-month price return | Reading |
|---|---:|---:|---|
| Technology · XLK | +1.45% | −3.11% | Led the session while still below its six-month starting price |
| Health care · XLV | −0.06% | +27.10% | A quiet session in the strongest six-month sector in this edition |
| Financials · XLF | −0.59% | +10.26% | Longer leadership with a negative day |
| Staples · XLP | −1.28% | +6.93% | Largest daily decline among the 11 sector proxies |

### Size, style and sector tables

| Production table | Row grain | Columns, in reading order | Distinct comparison |
|---|---|---|---|
| Size × style | Nine cells: large/mid/small × value/blend/growth | Named benchmark or proxy, return type, 1D/1W/1M/3M/6M/YTD/1Y, drawdown, as-of | Relative to the cell's broad size benchmark |
| Sector and industry | Eleven GICS sectors, expandable to industries | Weight, return, active return, index contribution, advancers/eligible, above 50D/200D, dispersion | Sector proxy performance vs point-in-time constituent attribution |
| Earnings and valuation | Sector or selected industry | Trailing EPS, forward EPS vintage, revisions breadth, P/E, multiple percentile, income and residual | Market rerating vs earnings change across a stable cohort |
| Factors | Market, size, value, profitability, investment, momentum | Factor return, beta/loading, contribution, annualization, interval, R², N, through-date | CAPM Jensen's alpha vs separately fitted multifactor intercept |

### How to interpret the model

A stock with beta two has historically moved twice as much as the benchmark on average for a one-unit change, conditional on the fitted model. That loading says nothing by itself about skill. Jensen's alpha comes from excess total returns after accounting for market exposure and the risk-free series. Present the intercept alongside its uncertainty, currency, benchmark and fitting window. Constituents, total-return factors and the complete mid-cap grid need new verified inputs.

### Design contract

Default to US, 6M, price-return basis. The size/style grid and sector table sit above the valuation and factor sections. Selecting a size cell fixes the cohort for all downstream panels. Selecting an industry compares it with its sector and broad market on one chart. When a cell lacks a matched benchmark, keep the cell in place with its data requirement.

## Sovereign rates

### What moved along the curve

| Tenor | Nov 5 yield | Nov 4 yield | Move |
|---|---:|---:|---:|
| 3M | 4.17% | 4.21% | −4 bp |
| 2Y | 4.46% | 4.58% | −12 bp |
| 5Y | 4.59% | 4.69% | −10 bp |
| 10Y | 4.84% | 4.90% | −6 bp |
| 30Y | 5.25% | 5.28% | −3 bp |

@chart rates

### Reading the shape

The curve bull-steepened: yields fell, with the two-year falling more than the ten-year. The 2s10s spread widened from 32 to 38 bp. This establishes the change in shape. To investigate its driver, compare same-window meeting futures, matched-tenor real yields and inflation compensation. A constant-maturity yield is a curve observation; a portfolio P&L requires a position and its risk sensitivities.

### Nine bond analytics on the instrument sheet

| Row | Display and unit | Calculation or required input |
|---|---|---|
| 1. Yield | YTM / YTW, % | Settlement date, cash flows, coupon convention, exercise assumptions |
| 2. Carry | Currency and % over selected holding period | Accrual, coupons, funding basis |
| 3. Roll-down | Currency and % over the same period | Advance maturity along unchanged reference curve; reconcile carry separately |
| 4. Spread / OAS | bp over named reference curve | Matched maturity and option model where applicable |
| 5. Duration and DV01 | Years; currency per bp for position | Modified/effective measure, position size, parallel bump |
| 6. Key-rate DV01 | Currency per bp by tenor | Full curve, interpolation and bump convention |
| 7. Spread DV01 | Currency per bp of spread | Reprice at constant Treasury curve |
| 8. Convexity | Second-order response with stated scale | Central bumps; optional cash flows require repricing model |
| 9. Total-return attribution | Carry, roll, rates, spread, FX, residual in pp | Dated position, cash flows and consistent realized return basis |

### Worked instrument

A model five-year bond paying 5% semiannually, settled on a coupon date at a 5% yield, prices at 100 per 100 face. Its modified duration is 4.376 years; its DV01 magnitude is about 0.04376 per 100 face. A full reprice at 6% gives 95.7349. Display the approximation beside the full reprice so the reader can see the effect of convexity. This is a teaching fixture, separate from the Treasury observations above.

### Design contract

Default to nominal Treasury, prior close and one-month comparison. Toggle real/nominal, select two tenors for a spread, then open the instrument sheet. Give each missing analytic its input requirement. Use tenor in years or explicitly label equally spaced categorical maturities.

## Credit

### Traded credit exposures

| Segment | Proxy | 1D price | 6M price | Next evidence needed |
|---|---|---:|---:|---|
| Investment grade | LQD | −0.12% | −4.27% | Duration-matched Treasury return and IG OAS |
| High yield | HYG | −0.06% | −3.66% | HY OAS and rating dispersion |
| Agency mortgages | MBB | −0.03% | −2.88% | Effective duration and prepayment assumptions |
| Senior loans | BKLN | +0.24% | −0.82% | Reset schedule, credit quality and distributions |
| Municipal bonds | MUB | +0.10% | −1.94% | Muni/Treasury ratio, matched tenor and tax basis |
| EM dollar debt | EMB | 0.00% | −4.48% | Sovereign spreads, duration and country composition |

@chart credit

### Spread monitor · evidence available in this edition

| Segment | Traded price observation | OAS level / daily bp move | Duration-matched excess return |
|---|---|---|---|
| IG corporates | LQD · $104.53 | Awaiting dated index OAS | Requires same-period Treasury benchmark and total returns |
| HY corporates | HYG · $77.23 | Awaiting dated index OAS | Requires rating/maturity composition and duration match |

### Credit reading

HYG fell less than LQD on November 6, and senior loans gained. Those moves establish a ranking of traded prices. They cannot establish whether corporate spreads tightened: the instruments carry different rate sensitivities, coupons and issuer exposures. A spread-led reading should appear only after a dated OAS series and a matched Treasury comparison arrive.

### Spread and stress tables

| Section | Rows | Columns and chart |
|---|---|---|
| Spread monitor | Rating × maturity buckets | OAS level, Δ bp, 1M/6M move, historical percentile, effective duration, source and observation time; plot matched spread curves |
| Return bridge | Selected segment vs benchmark | Income, rates, spread, FX, residual, realized total return; waterfall reconciles to the same period |
| Credit stress | Parallel rates, spread widening, downgrade/default case | Position, key-rate DV01, spread duration, recovery assumption, shocked price, P&L, model date |

### Design contract

Start with traded segments in the available edition. When OAS is licensed, make spreads the lead metric with ETF returns beside them. A rating or maturity selection applies to both curves and attribution. Preserve blanks for an unpublished spread and show the dated proxy independently.

## FX and global sessions

### Currency board

| Instrument | 1D | 6M | Positive move means |
|---|---:|---:|---|
| Dollar index | +0.74% | +4.37% | Basket strengthened |
| EUR/USD | −0.06% | −4.16% | More USD per EUR |
| USD/JPY | −0.54% | −0.11% | More JPY per USD |
| GBP/USD | −0.16% | −0.83% | More USD per GBP |
| USD/CHF | −0.13% | +4.35% | More CHF per USD |

@chart fx

### Currency reading

The dollar basket rose while USD/JPY fell. A USD investor holding yen gained on the currency leg over matched fixes; another investor holding a broad dollar basket saw a gain as well. Weighting and quote direction explain how those observations can coexist. Regional cash equity returns require one more step: match the local-market return period to the FX fixing before translating the move into dollars.

### Translation and hedge tables

| Table | Columns | Required distinction |
|---|---|---|
| Session handoff | Region, exchange, local close/timezone, UTC close, FX fix, next session, holiday state | Identify unmatched observation endpoints |
| USD translation | Local index return, USD-per-local FX return, interaction, USD return, residual | Multiply gross local and gross currency return |
| Hedge comparison | Hedge ratio, forward points, tenor, rebalance date, costs, hedged/unhedged return | Spot direction and forward carry have different inputs |

### Design contract

Default to local quote conventions with direction written out. Switch to USD-per-local for comparisons and invert both endpoints before calculating returns. Exclude stale or misaligned fixes from attribution. A region selection brings its cash index and FX history into one pane.

## Commodities and futures

### Contract board

| Instrument | Contract | Price move on Nov 6 | Six-month same-contract change |
|---|---|---:|---:|
| WTI crude | Dec 2026 | +0.34% | +17.85% |
| Brent crude | Jan 2027 | +0.03% | +18.06% |
| Copper | Dec 2026 | −0.52% | −1.49% |

@chart commodities

### Energy reading

December WTI rose $0.31 to $90.83 per barrel. January Brent closed at $98.32. The price difference between these rows includes a delivery-month difference. To examine regional crude pricing, first match delivery months, grade and units. To examine scarcity over time, compare consecutive contracts on the same oil curve and check physical inventories against their seasonal range.

### Structure, supply and positioning

| Exhibit | Rows | Columns or marks |
|---|---|---|
| Forward curve | Individual delivery months | Settlement or vendor close, date, volume, open interest, Δ1D; overlay prior month on the same contracts |
| Calendar spreads | Front/next and seasonal pairs | Both legs, expiry, absolute spread, change, percentile and observation |
| Physical balance | Inventories, production, refinery inputs | Report period, release time, value, change, seasonal range, revision and units |
| Positioning and roll | CFTC trader groups; strategy roll dates | Net position, open-interest share, as-of vs publication date; separate price, roll, collateral and costs |

### Design contract

Default to oil and named contracts. Selecting a point on the curve reveals its delivery month and source. Keep outright price, curve shape and rolled-strategy return in separate panels. When one leg is missing, suppress that spread and retain the single observed contract.

## Alternatives and real estate

### Listed exposures

| Sleeve | Observable proxy | 1D | 6M | Economic question |
|---|---|---:|---:|---|
| Listed property | VNQ | −0.52% | −1.40% | Are operating results or financing costs changing? |
| Listed infrastructure | IGF | −0.56% | −4.16% | How much revenue resets with inflation? |
| Managed futures | DBMF | +1.29% | +3.38% | Which trend exposures contributed? |
| Gold | GLD | −0.79% | −13.56% | How did real yields and the dollar move? |
| Bitcoin | BTC-USD | −0.26% | −6.98% | Does the UTC observation align with the other closes? |

@chart alternatives

### Real-estate reading

Listed real estate fell on the day while the managed-futures proxy rose. The daily market price offers no same-day observation of rent, occupancy or property NAV. The useful next panel is property type. Office, industrial, retail and residential landlords have different tenant demand, lease duration and debt maturities. A quarterly fall in same-store NOI with rising interest expense would challenge an operating recovery even if listed shares rallied.

### Underlying economics and marks

| Table | Rows | Columns |
|---|---|---|
| Listed property fundamentals | Property type and issuer cohort | Price/total return, FFO per share, same-store NOI growth, occupancy, leverage, debt maturity, fixed-rate share, reporting quarter |
| Private assets | Fund and vintage | NAV as-of, report date, contributions, distributions, net IRR, MOIC, PME benchmark, valuation lag |
| Diversifiers | Gold, infrastructure, trend, crypto | Return basis, exposure estimate, correlation window, drawdown, source, sample and next observation |

### Design contract

Start with liquid proxies. Open property types beneath real estate, and put private marks on a separate quarterly timeline. Charts of FFO, NOI and leverage use their own release dates. A listed proxy can contextualize a private mark but never fills its missing quarters.

## Macro and policy

### Confirmed macro evidence

| MRS pillar | Sep 30 score (z) | Direction relative to its reference mean |
|---|---:|---|
| Growth | +0.12 | Above |
| Credit | +0.90 | Above |
| Market stress pillar | +0.52 | Above on the model's signed scale |
| Inflation | −0.28 | Below |
| Liquidity/rates | −0.16 | Below |

### Policy reading

The last confirmed monthly regime in the sample was Neutral at +0.2537z through September 30. Credit provided positive support while inflation and liquidity/rates scores were below their reference means. November Treasury moves are newer observations. Put them in the incoming-evidence column until a new confirmed composite is published. A change in yields alone cannot establish a change in the Fed's stated outlook.

### Forecasts, decisions and releases

| Exhibit | Rows | Columns and required annotation |
|---|---|---|
| Policy paths | FOMC decision, SEP, market futures, NY Fed survey, house scenario | Owner, release timestamp, target horizon, rate basis, range/dispersion and revision |
| Economic release ledger | CPI, PCE, payrolls, GDP, credit, funding | Period, actual, prior as known, revised prior, timestamped expectation, surprise, revision |
| Event study | Selected release or meeting | Event time, pre/post observation windows, instrument, change, eligible sample and competing events |

### Design contract

Land on confirmed regime and incoming evidence side by side. Select an event to inspect the release, pre-release expectation and comparable reaction window. Never compare an end-year dot with a near-meeting rate without aligning horizons. Unavailable consensus leaves the surprise cell blank.

## Cross-asset relationships

### Equity correlation across windows

| S&P 500 versus | Prior 63 | Latest 63 | Latest 21 | Change in 63-window estimate |
|---|---:|---:|---:|---:|
| IEF · intermediate Treasuries | +0.48 | +0.06 | −0.28 | −0.42 |
| VNQ · listed real estate | −0.10 | +0.39 | +0.41 | +0.49 |
| IGF · listed infrastructure | +0.26 | +0.36 | +0.39 | +0.10 |
| HYG · high yield | +0.69 | +0.55 | +0.59 | −0.14 |
| DBMF · managed futures | +0.27 | +0.09 | +0.31 | −0.18 |

@chart dependence

### What changed in diversification

S&P–IEF correlation fell from +0.48 to +0.06 in successive 63-observation windows. S&P–VNQ moved in the opposite direction, from −0.10 to +0.39. Broad labels such as “bonds” and “real assets” would conceal that divergence. The latest 21-observation S&P–IEF reading was −0.28, showing how sensitive the apparent hedge is to window choice. These are paired daily price returns through November 6. Income-inclusive and currency-hedged series answer different questions.

### Diagnostics beneath the matrix

| Exhibit | Columns or marks | Reading rule |
|---|---|---|
| Pairwise matrix | Asset pairs, correlation, N, first/last common endpoints, currency, return basis | Select a cell to inspect the rolling path |
| Dependence stability | 21/63/126-observation estimates, prior nonoverlapping window, change, eligible percentage | Suppress zero variance and inadequate samples |
| Downside dependence | Benchmark-down observations, count, conditional beta/correlation, threshold | Display sample before any conclusion |
| Portfolio covariance | Common sample or documented PSD estimator, weights date, marginal and component risk | Never feed an unchecked pairwise-deletion matrix to the optimizer |

### Design contract

Default to 63 common return intervals against US equities. Show the two adjacent windows and the continuous rolling path, then let the reader select another benchmark. Match both start and end dates. Call out stale pairs and exclude partial sessions.

## Portfolio lens

### SAA risk versus capital

| Sleeve | Capital | Risk share | Difference |
|---|---:|---:|---:|
| US equities | 35.0% | 51.0% | +16.0 pp |
| Emerging equities | 9.0% | 16.6% | +7.6 pp |
| Long Treasuries | 20.0% | 16.3% | −3.7 pp |
| Developed ex-US equity | 7.0% | 8.1% | +1.1 pp |
| Managed futures | 8.0% | −1.5% | −9.5 pp |

@chart portfolio

### Portfolio reading

The November 6 SAA book had 9.5% forecast volatility against a 12.0% budget. US equities accounted for 51% of modeled risk against 35% of capital. Managed futures had a negative modeled risk contribution, consistent with a diversifying marginal contribution in this covariance estimate. Neither number measures the day's P&L. To explain realized performance, begin with actual start-of-period holdings and reconcile contributions to the published return.

### Portfolio budget check

| Measure | Published reading | Interpretation |
|---|---:|---|
| Forecast volatility | 9.5% | Risk estimate at the November 6 book date |
| Volatility budget | 12.0% | Mandate reference |
| Budget utilization | About 79% | Forecast risk divided by budget, using the rounded inputs |
| Growth assets | 62% of capital | Allocation classification from the book |

### Portfolio and stress tables

| Table | Rows | Columns |
|---|---|---|
| Book comparison | Certain, Endowment, SAA, DAA, Alpha | As-of, mandate, benchmark, active/static, risk budget, forecast risk, latest live return basis |
| Attribution | Sleeve and holding | Beginning weight, return, contribution, benchmark weight/return, active effect and residual |
| Stress and scenarios | Equity selloff, rate twist, spread shock, currency move | Shock assumptions, dates, position size, modeled impact, driver ranking and residual |

### Design contract

Default to SAA and its dated holdings. A book selection updates every chart, benchmark and risk limit. Separate live history and backtest explicitly. Changing a market scenario updates stress P&L while the actual published portfolio edition stays visible.

## Research journal

### Daily research entries

| Proposed watch | Original evidence | Alternative explanation | Test at next review |
|---|---|---|---|
| US leadership is narrowing over the short horizon | S&P +0.31%, RSP −0.38%, three sector ETFs advanced | Small caps rose; the move may be concentrated by industry rather than size | Track five-session participation and compare size-matched growth/value cohorts |
| The Treasury sleeve has become a more useful diversifier | S&P–IEF correlation weakened across two 63-observation windows | A short window or event cluster may explain the shift | Repeat with total returns, downside sample and 126 observations |

### Editorial reading

Both entries are candidate hypotheses derived from the archived edition. Neither is an adopted house thesis. A manager could accept the first, shorten its horizon, or reject it after seeing constituent breadth. Preserve the original observation, the decision and the reason. When the evidence changes, append a dated revision so the earlier judgment can be assessed on what was knowable at the time.

### Journal and edition tables

| Exhibit | Columns | Behavior |
|---|---|---|
| Thesis register | ID, owner, asset/industry, horizon, claim, benchmark, state, original edition, invalidator, next catalyst | Separate candidate, adopted, challenged, resolved and withdrawn entries |
| Revision history | Original claim, timestamp, changed evidence, counterevidence, decision, author | Reopen the prior edition without replacing its contents |
| Outcome review | Predicted direction/probability, resolution rule/date, realized outcome, error, sample | Score only resolved forecasts with a predefined horizon |
| Source and cadence ledger | Instrument/claim, source, as-of, revision, quality state, publication time | Trace every number to the input used for that edition |

### Design contract

Default to open market watches and changes since the previous edition. Select a watch to see its original note, later revisions and full evidence table together. Saving an actual private note needs an authenticated store. This public design contains illustrative hypotheses and no private authoring control.
