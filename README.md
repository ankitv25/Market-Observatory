# Market Observatory

**[Open the live dashboard →](https://ankitv25.github.io/Market-Observatory/)**

![Market Observatory · US market edition](assets/banner.svg)

[Full project plan](docs/PROJECT_PLAN.md) · [Research brief](docs/Market-Observatory-Research.pdf) · [Milestones](https://github.com/ankitv25/Market-Observatory/milestones)

**[Market tape](#market-tape) · [Sector rotation](#sector-rotation) · [Treasury curve](#treasury-curve) · [Research notebook](dashboard/RESEARCH.md) · [Cadence log](CADENCE.md) · [Work log](WORKLOG.md)**

Edition compiled **2026-11-24T00:24:23-05:00** · 62 market instruments · dated observations below. Prices and changes use each instrument’s own feed and session. Percentages use unrounded prices.

## The daily reading

**Market assessment:** risk-on · evidence agreement 83/100 · as of 2026-11-23. This score is not a forecast probability.

The US equity benchmark median returned +4.07%, against +5.07% for developed ex-US and emerging-market ETFs. VIX changed -25.83%. High-yield ETF prices outpaced short Treasuries by 0.30 pp. The counterweight is small-cap and equal-weight participation.

[Assessment rules](docs/METHODOLOGY.md#market-intelligence-and-historical-story) · [Pipeline execution records](runs/)

**US equities.** The S&P 500 reached 7,237.17 on 2026-11-23, a move of +326.78 points (+4.73%) against 2026-11-20. Its six-month price change was -3.16% from 2026-05-22.

**Sector participation.** 9 of 11 reporting sector ETFs rose on 2026-11-23. Technology led at +8.97%; Energy finished at -1.06%.

**Equity style.** On 2026-11-23 large-cap growth (+7.97%) finished 5.97 percentage points ahead of large-cap value (+2.00%), measured by IWF and IWD.

**Energy.** The Jan 2027 WTI contract closed at $80.17/bbl on 2026-11-23, -3.24 dollars per barrel against its own 2026-11-20 close.

**US rates.** On 2026-11-20 the 2-year par yield was 4.63% and the 10-year was 4.92%. The 2s10s spread stood at +29 bp, changing by +1 bp versus 2026-11-19.

**Macro backdrop.** The latest available MRS observation is 2026-09-30. Its regime is Neutral with a composite score of 0.2537.

## Market tape

| Instrument | Last | Δ units | Δ % | 6 months | Observation |
|---|---:|---:|---:|---:|---|
|**Indices**||||||
|[S&P 500](https://finance.yahoo.com/quote/%5EGSPC/history/) · ^GSPC|7,237.17|+326.78|+4.73%|-3.16%|2026-11-23|
|[Nasdaq Composite](https://finance.yahoo.com/quote/%5EIXIC/history/) · ^IXIC|24,089.56|+1,471.83|+6.51%|-8.56%|2026-11-23|
|[Nasdaq 100](https://finance.yahoo.com/quote/%5ENDX/history/) · ^NDX|26,746.10|+1,717.12|+6.86%|-9.28%|2026-11-23|
|[Dow Industrials](https://finance.yahoo.com/quote/%5EDJI/history/) · ^DJI|49,595.31|+1,447.98|+3.01%|-1.95%|2026-11-23|
|[Russell 2000](https://finance.yahoo.com/quote/%5ERUT/history/) · ^RUT|2,669.66|+87.87|+3.40%|-6.96%|2026-11-23|
|**Sectors**||||||
|[Technology](https://finance.yahoo.com/quote/XLK/history/) · XLK|162.38|+13.37|+8.97%|-9.98%|2026-11-23|
|[Communication Services](https://finance.yahoo.com/quote/XLC/history/) · XLC|103.60|+3.57|+3.57%|-10.27%|2026-11-23|
|[Consumer Discretionary](https://finance.yahoo.com/quote/XLY/history/) · XLY|116.93|+4.47|+3.97%|-1.89%|2026-11-23|
|[Consumer Staples](https://finance.yahoo.com/quote/XLP/history/) · XLP|90.38|-0.08|-0.09%|+6.58%|2026-11-23|
|[Energy](https://finance.yahoo.com/quote/XLE/history/) · XLE|59.87|-0.64|-1.06%|+0.64%|2026-11-23|
|[Financials](https://finance.yahoo.com/quote/XLF/history/) · XLF|55.65|+1.08|+1.98%|+7.14%|2026-11-23|
|[Health Care](https://finance.yahoo.com/quote/XLV/history/) · XLV|179.42|+2.18|+1.23%|+19.70%|2026-11-23|
|[Industrials](https://finance.yahoo.com/quote/XLI/history/) · XLI|162.47|+6.10|+3.90%|-5.41%|2026-11-23|
|[Materials](https://finance.yahoo.com/quote/XLB/history/) · XLB|49.90|+1.56|+3.23%|-0.78%|2026-11-23|
|[Real Estate](https://finance.yahoo.com/quote/XLRE/history/) · XLRE|42.90|+0.44|+1.04%|-3.73%|2026-11-23|
|[Utilities](https://finance.yahoo.com/quote/XLU/history/) · XLU|43.32|+0.63|+1.48%|-4.48%|2026-11-23|
|**Styles**||||||
|[US large cap](https://finance.yahoo.com/quote/SPY/history/) · SPY|722.29|+32.48|+4.71%|-3.13%|2026-11-23|
|[Equal-weight S&P 500](https://finance.yahoo.com/quote/RSP/history/) · RSP|212.82|+5.38|+2.59%|+3.02%|2026-11-23|
|[US large-cap growth](https://finance.yahoo.com/quote/IWF/history/) · IWF|109.83|+8.11|+7.97%|-12.14%|2026-11-23|
|[US large-cap value](https://finance.yahoo.com/quote/IWD/history/) · IWD|252.37|+4.96|+2.00%|+6.79%|2026-11-23|
|[US small cap](https://finance.yahoo.com/quote/IWM/history/) · IWM|265.74|+9.13|+3.56%|-6.80%|2026-11-23|
|[US momentum](https://finance.yahoo.com/quote/MTUM/history/) · MTUM|63.94|+3.67|+6.09%|-15.76%|2026-11-23|
|[US quality](https://finance.yahoo.com/quote/QUAL/history/) · QUAL|53.86|+1.99|+3.84%|+0.49%|2026-11-23|
|**Global**||||||
|[Euro STOXX 50](https://finance.yahoo.com/quote/%5ESTOXX50E/history/) · ^STOXX50E|6,074.47|+132.52|+2.23%|+0.91%|2026-11-23|
|[FTSE 100](https://finance.yahoo.com/quote/%5EFTSE/history/) · ^FTSE|10,480.80|+134.50|+1.30%|+0.14%|2026-11-23|
|[Nikkei 225](https://finance.yahoo.com/quote/%5EN225/history/) · ^N225|56,436.65|-3,007.56|-5.06%|-5.63%|2026-11-20|
|[Hang Seng](https://finance.yahoo.com/quote/%5EHSI/history/) · ^HSI|22,383.74|-27.06|-0.12%|-12.58%|2026-11-23|
|[Nifty 50](https://finance.yahoo.com/quote/%5ENSEI/history/) · ^NSEI|25,349.65|-450.95|-1.75%|+6.87%|2026-11-23|
|[S&P/TSX Composite](https://finance.yahoo.com/quote/%5EGSPTSE/history/) · ^GSPTSE|34,082.10|+892.20|+2.69%|-1.13%|2026-11-23|
|[All-country equity](https://finance.yahoo.com/quote/ACWI/history/) · ACWI|148.94|+6.35|+4.45%|-4.52%|2026-11-23|
|[Developed ex-US/Canada](https://finance.yahoo.com/quote/EFA/history/) · EFA|98.76|+2.62|+2.73%|-5.02%|2026-11-23|
|[Emerging markets](https://finance.yahoo.com/quote/EEM/history/) · EEM|57.83|+3.99|+7.41%|-12.22%|2026-11-23|
|**Futures**||||||
|[WTI crude](https://finance.yahoo.com/quote/CLF27.NYM/history/) · CLF27.NYM|80.17|-3.24|-3.88%|+0.65%|2026-11-23|
|[Brent crude](https://finance.yahoo.com/quote/BZF27.NYM/history/) · BZF27.NYM|89.37|-3.20|-3.46%|+3.46%|2026-11-23|
|[Natural gas](https://finance.yahoo.com/quote/NGF27.NYM/history/) · NGF27.NYM|3.52|-0.22|-6.00%|-19.90%|2026-11-23|
|[Gold](https://finance.yahoo.com/quote/GCZ26.CMX/history/) · GCZ26.CMX|3,651.40|+136.00|+3.87%|-21.02%|2026-11-23|
|[Silver](https://finance.yahoo.com/quote/SIZ26.CMX/history/) · SIZ26.CMX|43.17|+2.10|+5.13%|-44.35%|2026-11-23|
|[Copper](https://finance.yahoo.com/quote/HGZ26.CMX/history/) · HGZ26.CMX|5.63|+0.15|+2.72%|-13.71%|2026-11-23|
|[Corn](https://finance.yahoo.com/quote/ZCH27.CBT/history/) · ZCH27.CBT|449.75|+1.00|+0.22%|-10.18%|2026-11-23|
|[S&P 500 E-mini](https://finance.yahoo.com/quote/ESZ26.CME/history/) · ESZ26.CME|7,254.50|+319.50|+4.61%|-4.73%|2026-11-23|
|[10Y Treasury note](https://finance.yahoo.com/quote/ZNZ26.CBT/history/) · ZNZ26.CBT|106.75|-0.09|-0.09%|-1.95%|2026-11-23|
|**FX**||||||
|[US Dollar Index](https://finance.yahoo.com/quote/DX-Y.NYB/history/) · DX-Y.NYB|104.3200|+0.5100|+0.49%|+5.03%|2026-11-23|
|[EUR/USD](https://finance.yahoo.com/quote/EURUSD%3DX/history/) · EURUSD=X|1.0972|+0.0002|+0.02%|-5.59%|2026-11-23|
|[USD/JPY](https://finance.yahoo.com/quote/JPY%3DX/history/) · JPY=X|158.9310|-0.7760|-0.49%|-0.05%|2026-11-23|
|[GBP/USD](https://finance.yahoo.com/quote/GBPUSD%3DX/history/) · GBPUSD=X|1.3095|+0.0008|+0.06%|-2.52%|2026-11-23|
|[USD/CHF](https://finance.yahoo.com/quote/CHF%3DX/history/) · CHF=X|0.8409|-0.0032|-0.38%|+6.92%|2026-11-23|
|**Credit**||||||
|[Short Treasuries](https://finance.yahoo.com/quote/SHY/history/) · SHY|81.57|-0.04|-0.05%|-0.67%|2026-11-23|
|[Intermediate Treasuries](https://finance.yahoo.com/quote/IEF/history/) · IEF|91.64|-0.01|-0.01%|-2.39%|2026-11-23|
|[Long Treasuries](https://finance.yahoo.com/quote/TLT/history/) · TLT|81.69|+0.24|+0.29%|-3.53%|2026-11-23|
|[Inflation-linked Treasuries](https://finance.yahoo.com/quote/TIP/history/) · TIP|105.57|-0.17|-0.16%|-4.36%|2026-11-23|
|[Investment-grade credit](https://finance.yahoo.com/quote/LQD/history/) · LQD|103.93|+0.24|+0.23%|-4.10%|2026-11-23|
|[High-yield credit](https://finance.yahoo.com/quote/HYG/history/) · HYG|76.52|+0.19|+0.25%|-4.24%|2026-11-23|
|[Agency mortgages](https://finance.yahoo.com/quote/MBB/history/) · MBB|91.62|+0.03|+0.03%|-2.61%|2026-11-23|
|[Municipal bonds](https://finance.yahoo.com/quote/MUB/history/) · MUB|103.74|+0.23|+0.22%|-2.29%|2026-11-23|
|[EM dollar debt](https://finance.yahoo.com/quote/EMB/history/) · EMB|90.70|+0.78|+0.87%|-4.70%|2026-11-23|
|[Senior loans](https://finance.yahoo.com/quote/BKLN/history/) · BKLN|20.45|-0.01|-0.05%|-0.10%|2026-11-23|
|**Alternatives**||||||
|[Listed real estate](https://finance.yahoo.com/quote/VNQ/history/) · VNQ|93.67|+1.11|+1.20%|-3.20%|2026-11-23|
|[Listed infrastructure](https://finance.yahoo.com/quote/IGF/history/) · IGF|64.76|+0.57|+0.89%|-3.92%|2026-11-23|
|[Managed futures](https://finance.yahoo.com/quote/DBMF/history/) · DBMF|31.56|+0.11|+0.35%|+1.51%|2026-11-23|
|[Physical gold ETF](https://finance.yahoo.com/quote/GLD/history/) · GLD|333.02|+10.15|+3.14%|-19.53%|2026-11-23|
|[Bitcoin](https://finance.yahoo.com/quote/BTC-USD/history/) · BTC-USD|61,161.91|+1,067.82|+1.78%|-18.98%|2026-11-22|
|[Cboe VIX](https://finance.yahoo.com/quote/%5EVIX/history/) · ^VIX|26.62|-9.27|-25.83%|+59.40%|2026-11-23|

## Sector rotation

![Daily US sector proxy returns](assets/sectors.svg)

## Treasury curve

![US Treasury par yields](assets/curve.svg)

[US Treasury par yields](https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=300&from=&to=&filetype=csv&label=include&layout=seriescolumn) · 2026-11-20 versus 2026-11-19.

| Maturity | Yield | Δ bp |
|---|---:|---:|
|1M|4.19%|-1|
|3M|4.32%|-2|
|6M|4.38%|-4|
|1Y|4.51%|-11|
|2Y|4.63%|-13|
|3Y|4.65%|-16|
|5Y|4.71%|-15|
|7Y|4.80%|-14|
|10Y|4.92%|-12|
|20Y|5.34%|-9|
|30Y|5.31%|-9|

## Edition record

[Quality and source notes](dashboard/SOURCES.md) · [Archived editions](editions/) · [Refresh runs](https://github.com/ankitv25/Market-Observatory/actions/workflows/refresh.yml) · [Methodology](docs/METHODOLOGY.md)

For interactive charts, filters and source detail, download [the self-contained HTML reader](dashboard/observatory.html) using GitHub’s **Download raw file** button and open it locally. Each refresh run also provides the reader as an artifact.
