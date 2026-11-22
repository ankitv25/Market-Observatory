# Market Observatory

**[Open the live dashboard →](https://ankitv25.github.io/Market-Observatory/)**

![Market Observatory · US market edition](assets/banner.svg)

[Full project plan](docs/PROJECT_PLAN.md) · [Research brief](docs/Market-Observatory-Research.pdf) · [Milestones](https://github.com/ankitv25/Market-Observatory/milestones)

**[Market tape](#market-tape) · [Sector rotation](#sector-rotation) · [Treasury curve](#treasury-curve) · [Research notebook](dashboard/RESEARCH.md) · [Cadence log](CADENCE.md) · [Work log](WORKLOG.md)**

Edition compiled **2026-11-22T13:46:37-05:00** · 62 market instruments · dated observations below. Prices and changes use each instrument’s own feed and session. Percentages use unrounded prices.

## The daily reading

**Market assessment:** risk-off · evidence agreement 83/100 · as of 2026-11-20. This score is not a forecast probability.

The US equity benchmark median returned -3.23%, against -3.90% for developed ex-US and emerging-market ETFs. VIX changed +26.20%. High-yield ETF prices trailed short Treasuries by 0.54 pp. The counterweight is small-cap and equal-weight participation.

[Assessment rules](docs/METHODOLOGY.md#market-intelligence-and-historical-story) · [Pipeline execution records](runs/)

**Source status.** Live feed unavailable; checked archived coverage for CHF=X Prior observations retained for BZF27.NYM

**US equities.** The S&P 500 reached 6,910.39 on 2026-11-20, a move of -265.44 points (-3.70%) against 2026-11-19. Its six-month price change was -7.03% from 2026-05-20.

**Sector participation.** 1 of 11 reporting sector ETFs rose on 2026-11-20. Consumer Staples led at +0.67%; Technology finished at -7.27%.

**Equity style.** On 2026-11-20 large-cap growth (-6.02%) finished 4.39 percentage points behind large-cap value (-1.63%), measured by IWF and IWD.

**Energy.** The Jan 2027 WTI contract closed at $83.41/bbl on 2026-11-20, +0.97 dollars per barrel against its own 2026-11-19 close.

**US rates.** On 2026-11-19 the 2-year par yield was 4.76% and the 10-year was 5.04%. The 2s10s spread stood at +28 bp, changing by +1 bp versus 2026-11-18.

**Macro backdrop.** The latest available MRS observation is 2026-09-30. Its regime is Neutral with a composite score of 0.2537.

## Market tape

| Instrument | Last | Δ units | Δ % | 6 months | Observation |
|---|---:|---:|---:|---:|---|
|**Indices**||||||
|[S&P 500](https://finance.yahoo.com/quote/%5EGSPC/history/) · ^GSPC|6,910.39|-265.44|-3.70%|-7.03%|2026-11-20|
|[Nasdaq Composite](https://finance.yahoo.com/quote/%5EIXIC/history/) · ^IXIC|22,617.73|-1,261.47|-5.28%|-13.90%|2026-11-20|
|[Nasdaq 100](https://finance.yahoo.com/quote/%5ENDX/history/) · ^NDX|25,028.98|-1,488.07|-5.61%|-14.57%|2026-11-20|
|[Dow Industrials](https://finance.yahoo.com/quote/%5EDJI/history/) · ^DJI|48,147.33|-949.73|-1.93%|-3.72%|2026-11-20|
|[Russell 2000](https://finance.yahoo.com/quote/%5ERUT/history/) · ^RUT|2,581.79|-73.32|-2.76%|-8.36%|2026-11-20|
|**Sectors**||||||
|[Technology](https://finance.yahoo.com/quote/XLK/history/) · XLK|149.01|-11.68|-7.27%|-15.88%|2026-11-20|
|[Communication Services](https://finance.yahoo.com/quote/XLC/history/) · XLC|100.03|-2.73|-2.66%|-13.84%|2026-11-20|
|[Consumer Discretionary](https://finance.yahoo.com/quote/XLY/history/) · XLY|112.46|-3.42|-2.95%|-4.65%|2026-11-20|
|[Consumer Staples](https://finance.yahoo.com/quote/XLP/history/) · XLP|90.46|+0.60|+0.67%|+5.78%|2026-11-20|
|[Energy](https://finance.yahoo.com/quote/XLE/history/) · XLE|60.51|-0.38|-0.62%|+1.19%|2026-11-20|
|[Financials](https://finance.yahoo.com/quote/XLF/history/) · XLF|54.57|-1.01|-1.82%|+5.63%|2026-11-20|
|[Health Care](https://finance.yahoo.com/quote/XLV/history/) · XLV|177.24|-0.22|-0.12%|+20.46%|2026-11-20|
|[Industrials](https://finance.yahoo.com/quote/XLI/history/) · XLI|156.37|-4.99|-3.09%|-8.41%|2026-11-20|
|[Materials](https://finance.yahoo.com/quote/XLB/history/) · XLB|48.34|-1.08|-2.19%|-2.78%|2026-11-20|
|[Real Estate](https://finance.yahoo.com/quote/XLRE/history/) · XLRE|42.46|-0.42|-0.98%|-4.43%|2026-11-20|
|[Utilities](https://finance.yahoo.com/quote/XLU/history/) · XLU|42.69|-0.32|-0.74%|-4.09%|2026-11-20|
|**Styles**||||||
|[US large cap](https://finance.yahoo.com/quote/SPY/history/) · SPY|689.81|-26.06|-3.64%|-6.94%|2026-11-20|
|[Equal-weight S&P 500](https://finance.yahoo.com/quote/RSP/history/) · RSP|207.44|-4.19|-1.98%|+1.77%|2026-11-20|
|[US large-cap growth](https://finance.yahoo.com/quote/IWF/history/) · IWF|101.72|-6.52|-6.02%|-18.40%|2026-11-20|
|[US large-cap value](https://finance.yahoo.com/quote/IWD/history/) · IWD|247.41|-4.11|-1.63%|+5.82%|2026-11-20|
|[US small cap](https://finance.yahoo.com/quote/IWM/history/) · IWM|256.61|-7.61|-2.88%|-8.31%|2026-11-20|
|[US momentum](https://finance.yahoo.com/quote/MTUM/history/) · MTUM|60.27|-3.63|-5.68%|-19.53%|2026-11-20|
|[US quality](https://finance.yahoo.com/quote/QUAL/history/) · QUAL|51.87|-1.44|-2.70%|-2.24%|2026-11-20|
|**Global**||||||
|[Euro STOXX 50](https://finance.yahoo.com/quote/%5ESTOXX50E/history/) · ^STOXX50E|5,941.95|-171.91|-2.81%|-0.57%|2026-11-20|
|[FTSE 100](https://finance.yahoo.com/quote/%5EFTSE/history/) · ^FTSE|10,346.30|-106.40|-1.02%|-0.82%|2026-11-20|
|[Nikkei 225](https://finance.yahoo.com/quote/%5EN225/history/) · ^N225|56,436.65|-3,007.56|-5.06%|-5.63%|2026-11-20|
|[Hang Seng](https://finance.yahoo.com/quote/%5EHSI/history/) · ^HSI|22,410.80|-430.82|-1.89%|-12.63%|2026-11-20|
|[Nifty 50](https://finance.yahoo.com/quote/%5ENSEI/history/) · ^NSEI|25,800.60|+286.30|+1.12%|+9.05%|2026-11-20|
|[S&P/TSX Composite](https://finance.yahoo.com/quote/%5EGSPTSE/history/) · ^GSPTSE|33,189.90|-838.80|-2.46%|-2.84%|2026-11-20|
|[All-country equity](https://finance.yahoo.com/quote/ACWI/history/) · ACWI|142.59|-5.15|-3.49%|-8.07%|2026-11-20|
|[Developed ex-US/Canada](https://finance.yahoo.com/quote/EFA/history/) · EFA|96.14|-2.64|-2.67%|-7.22%|2026-11-20|
|[Emerging markets](https://finance.yahoo.com/quote/EEM/history/) · EEM|53.84|-2.91|-5.13%|-17.75%|2026-11-20|
|**Futures**||||||
|[WTI crude](https://finance.yahoo.com/quote/CLF27.NYM/history/) · CLF27.NYM|83.41|+0.97|+1.18%|+4.69%|2026-11-20|
|[Brent crude](https://finance.yahoo.com/quote/BZF27.NYM/history/) · BZF27.NYM|92.57|+0.59|+0.64%|+7.25%|2026-11-20|
|[Natural gas](https://finance.yahoo.com/quote/NGF27.NYM/history/) · NGF27.NYM|3.75|+0.07|+1.82%|-17.12%|2026-11-20|
|[Gold](https://finance.yahoo.com/quote/GCZ26.CMX/history/) · GCZ26.CMX|3,515.40|-170.10|-4.62%|-24.15%|2026-11-20|
|[Silver](https://finance.yahoo.com/quote/SIZ26.CMX/history/) · SIZ26.CMX|41.07|-3.29|-7.41%|-47.04%|2026-11-20|
|[Copper](https://finance.yahoo.com/quote/HGZ26.CMX/history/) · HGZ26.CMX|5.49|-0.15|-2.64%|-15.37%|2026-11-20|
|[Corn](https://finance.yahoo.com/quote/ZCH27.CBT/history/) · ZCH27.CBT|448.75|-3.75|-0.83%|-10.83%|2026-11-20|
|[S&P 500 E-mini](https://finance.yahoo.com/quote/ESZ26.CME/history/) · ESZ26.CME|6,935.00|-262.25|-3.64%|-8.42%|2026-11-20|
|[10Y Treasury note](https://finance.yahoo.com/quote/ZNZ26.CBT/history/) · ZNZ26.CBT|106.84|+0.97|+0.91%|-1.99%|2026-11-20|
|**FX**||||||
|[US Dollar Index](https://finance.yahoo.com/quote/DX-Y.NYB/history/) · DX-Y.NYB|103.8100|-0.0900|-0.09%|+4.74%|2026-11-20|
|[EUR/USD](https://finance.yahoo.com/quote/EURUSD%3DX/history/) · EURUSD=X|1.0970|-0.0002|-0.02%|-5.49%|2026-11-20|
|[USD/JPY](https://finance.yahoo.com/quote/JPY%3DX/history/) · JPY=X|159.7070|+0.3260|+0.20%|+0.42%|2026-11-20|
|[GBP/USD](https://finance.yahoo.com/quote/GBPUSD%3DX/history/) · GBPUSD=X|1.3086|-0.0060|-0.46%|-2.31%|2026-11-20|
|[USD/CHF](https://finance.yahoo.com/quote/CHF%3DX/history/) · CHF=X|0.8441|+0.0006|+0.07%|+7.01%|2026-11-20|
|**Credit**||||||
|[Short Treasuries](https://finance.yahoo.com/quote/SHY/history/) · SHY|81.61|+0.23|+0.28%|-0.66%|2026-11-20|
|[Intermediate Treasuries](https://finance.yahoo.com/quote/IEF/history/) · IEF|91.65|+0.83|+0.91%|-2.23%|2026-11-20|
|[Long Treasuries](https://finance.yahoo.com/quote/TLT/history/) · TLT|81.45|+1.10|+1.37%|-2.93%|2026-11-20|
|[Inflation-linked Treasuries](https://finance.yahoo.com/quote/TIP/history/) · TIP|105.74|+0.71|+0.68%|-4.19%|2026-11-20|
|[Investment-grade credit](https://finance.yahoo.com/quote/LQD/history/) · LQD|103.69|+0.61|+0.59%|-3.95%|2026-11-20|
|[High-yield credit](https://finance.yahoo.com/quote/HYG/history/) · HYG|76.33|-0.20|-0.26%|-4.42%|2026-11-20|
|[Agency mortgages](https://finance.yahoo.com/quote/MBB/history/) · MBB|91.59|+0.69|+0.76%|-2.31%|2026-11-20|
|[Municipal bonds](https://finance.yahoo.com/quote/MUB/history/) · MUB|103.51|+0.41|+0.40%|-2.28%|2026-11-20|
|[EM dollar debt](https://finance.yahoo.com/quote/EMB/history/) · EMB|89.92|-0.40|-0.44%|-5.27%|2026-11-20|
|[Senior loans](https://finance.yahoo.com/quote/BKLN/history/) · BKLN|20.46|-0.04|-0.20%|-0.20%|2026-11-20|
|**Alternatives**||||||
|[Listed real estate](https://finance.yahoo.com/quote/VNQ/history/) · VNQ|92.56|-0.91|-0.97%|-4.07%|2026-11-20|
|[Listed infrastructure](https://finance.yahoo.com/quote/IGF/history/) · IGF|64.19|-0.65|-1.00%|-4.48%|2026-11-20|
|[Managed futures](https://finance.yahoo.com/quote/DBMF/history/) · DBMF|31.45|-0.35|-1.10%|+1.09%|2026-11-20|
|[Physical gold ETF](https://finance.yahoo.com/quote/GLD/history/) · GLD|322.87|-12.31|-3.67%|-22.65%|2026-11-20|
|[Bitcoin](https://finance.yahoo.com/quote/BTC-USD/history/) · BTC-USD|60,094.09|+1,295.11|+2.20%|-22.50%|2026-11-21|
|[Cboe VIX](https://finance.yahoo.com/quote/%5EVIX/history/) · ^VIX|35.89|+7.45|+26.20%|+105.79%|2026-11-20|

## Sector rotation

![Daily US sector proxy returns](assets/sectors.svg)

## Treasury curve

![US Treasury par yields](assets/curve.svg)

[US Treasury par yields](https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=300&from=&to=&filetype=csv&label=include&layout=seriescolumn) · 2026-11-19 versus 2026-11-18.

| Maturity | Yield | Δ bp |
|---|---:|---:|
|1M|4.20%|+10|
|3M|4.34%|+0|
|6M|4.42%|-1|
|1Y|4.62%|+0|
|2Y|4.76%|-4|
|3Y|4.81%|-3|
|5Y|4.86%|-3|
|7Y|4.94%|-2|
|10Y|5.04%|-3|
|20Y|5.43%|-1|
|30Y|5.40%|-1|

## Edition record

[Quality and source notes](dashboard/SOURCES.md) · [Archived editions](editions/) · [Refresh runs](https://github.com/ankitv25/Market-Observatory/actions/workflows/refresh.yml) · [Methodology](docs/METHODOLOGY.md)

For interactive charts, filters and source detail, download [the self-contained HTML reader](dashboard/observatory.html) using GitHub’s **Download raw file** button and open it locally. Each refresh run also provides the reader as an artifact.
