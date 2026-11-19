# Refresh ledger

Automatic targets are 07:17, 13:17, 16:17, 17:17, 18:47 and 22:47 America/New_York Monday–Friday, and 10:17 Saturday–Sunday. The timezone follows daylight saving time. Catch-up checks at minutes 13, 28, 43 and 58 collect when a target is outstanding or US closing observations are still behind after 16:17. Price-date retries are spaced at least one hour apart, including exchange holidays. Manual runs refresh immediately.

Collection runs the market, Treasury, macro and portfolio adapters, regenerates commentary and charts, validates the financial calculations, archives the inputs and publishes GitHub Pages. Prices, portfolio valuations and macro readings retain their individual observation dates. The open reader checks for a new edition every five minutes.

Actual completion times appear below and in the dashboard's **Cadence & sources** panel. GitHub may delay scheduled starts. [Workflow runs](https://github.com/ankitv25/Market-Observatory/actions/workflows/refresh.yml) · [GitHub scheduling behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

| Compiled (New York) | Instruments | Latest price observation | Treasury through | Quality notes | Edition | Run |
|---|---:|---|---|---:|---|---|
|2026-11-07T16:39:52-05:00|62|2026-11-06|2026-11-05|0|[snapshot](editions/2026-11/20261107T163952-0500.json)|local verification|
|2026-11-07T16:41:57-05:00|62|2026-11-06|2026-11-05|0|[snapshot](editions/2026-11/20261107T164157-0500.json)|[run 42417076925](https://github.com/ankitv25/Market-Observatory/actions/runs/42417076925)|
|2026-11-07T16:43:34-05:00|62|2026-11-06|2026-11-05|0|[snapshot](editions/2026-11/20261107T164334-0500.json)|[run 42417203790](https://github.com/ankitv25/Market-Observatory/actions/runs/42417203790)|
|2026-11-07T17:18:16-05:00|62|2026-11-06|2026-11-05|0|[snapshot](editions/2026-11/20261107T171816-0500.json)|local verification|
|2026-11-07T17:20:33-05:00|62|2026-11-06|2026-11-05|0|[snapshot](editions/2026-11/20261107T172033-0500.json)|[run 42420149834](https://github.com/ankitv25/Market-Observatory/actions/runs/42420149834)|
|2026-11-09T16:37:58-05:00|62|2026-11-09|2026-11-06|0|[snapshot](editions/2026-11/20261109T163758-0500.json)|[run 42704316869](https://github.com/ankitv25/Market-Observatory/actions/runs/42704316869)|
|2026-11-09T23:45:05-05:00|62|2026-11-09|2026-11-06|0|[snapshot](editions/2026-11/20261109T234505-0500.json)|[run 42757809845](https://github.com/ankitv25/Market-Observatory/actions/runs/42757809845)|
|2026-11-10T13:49:58-05:00|62|2026-11-10|2026-11-06|0|[snapshot](editions/2026-11/20261110T134958-0500.json)|[run 42879140362](https://github.com/ankitv25/Market-Observatory/actions/runs/42879140362)|
|2026-11-10T21:55:58-05:00|62|2026-11-10|2026-11-09|0|[snapshot](editions/2026-11/20261110T215558-0500.json)|[run 42949322629](https://github.com/ankitv25/Market-Observatory/actions/runs/42949322629)|
|2026-11-11T13:52:50-05:00|62|2026-11-11|2026-11-09|0|[snapshot](editions/2026-11/20261111T135250-0500.json)|[run 43081910572](https://github.com/ankitv25/Market-Observatory/actions/runs/43081910572)|
|2026-11-11T23:02:20-05:00|62|2026-11-11|2026-11-09|1|[snapshot](editions/2026-11/20261111T230220-0500.json)|[run 43152117317](https://github.com/ankitv25/Market-Observatory/actions/runs/43152117317)|
|2026-11-12T14:08:32-05:00|62|2026-11-12|2026-11-09|0|[snapshot](editions/2026-11/20261112T140832-0500.json)|[run 43287067625](https://github.com/ankitv25/Market-Observatory/actions/runs/43287067625)|
|2026-11-12T22:32:14-05:00|62|2026-11-12|2026-11-10|0|[snapshot](editions/2026-11/20261112T223214-0500.json)|[run 43359609732](https://github.com/ankitv25/Market-Observatory/actions/runs/43359609732)|
|2026-11-13T13:46:45-05:00|62|2026-11-13|2026-11-10|0|[snapshot](editions/2026-11/20261113T134645-0500.json)|[run 43485893158](https://github.com/ankitv25/Market-Observatory/actions/runs/43485893158)|
|2026-11-13T22:28:20-05:00|62|2026-11-13|2026-11-12|0|[snapshot](editions/2026-11/20261113T222820-0500.json)|[run 43551793029](https://github.com/ankitv25/Market-Observatory/actions/runs/43551793029)|
|2026-11-14T11:00:18-05:00|62|2026-11-13|2026-11-12|0|[snapshot](editions/2026-11/20261114T110018-0500.json)|local verification|
|2026-11-16T08:31:09-05:00|62|2026-11-16|2026-11-12|1|[snapshot](editions/2026-11/20261116T083109-0500.json)|local verification|
|2026-11-16T08:35:56-05:00|62|2026-11-16|2026-11-12|0|[snapshot](editions/2026-11/20261116T083556-0500.json)|[run 43877291706](https://github.com/ankitv25/Market-Observatory/actions/runs/43877291706)|
|2026-11-16T18:01:53-05:00|62|2026-11-16|2026-11-13|2|[snapshot](editions/2026-11/20261116T180153-0500.json)|[run 43975553981](https://github.com/ankitv25/Market-Observatory/actions/runs/43975553981)|
|2026-11-16T20:52:41-05:00|62|2026-11-16|2026-11-13|0|[snapshot](editions/2026-11/20261116T205241-0500.json)|[run 43998844384](https://github.com/ankitv25/Market-Observatory/actions/runs/43998844384)|
|2026-11-17T00:14:21-05:00|62|2026-11-16|2026-11-13|1|[snapshot](editions/2026-11/20261117T001421-0500.json)|[run 44022668095](https://github.com/ankitv25/Market-Observatory/actions/runs/44022668095)|
|2026-11-17T09:53:11-05:00|62|2026-11-17|2026-11-13|0|[snapshot](editions/2026-11/20261117T095311-0500.json)|[run 44107993479](https://github.com/ankitv25/Market-Observatory/actions/runs/44107993479)|
|2026-11-17T15:57:18-05:00|62|2026-11-17|2026-11-13|0|[snapshot](editions/2026-11/20261117T155718-0500.json)|[run 44174677217](https://github.com/ankitv25/Market-Observatory/actions/runs/44174677217)|
|2026-11-17T22:05:13-05:00|62|2026-11-17|2026-11-16|0|[snapshot](editions/2026-11/20261117T220513-0500.json)|local verification|
|2026-11-17T22:06:45-05:00|62|2026-11-17|2026-11-16|1|[snapshot](editions/2026-11/20261117T220645-0500.json)|[run 44228062836](https://github.com/ankitv25/Market-Observatory/actions/runs/44228062836)|
|2026-11-17T23:43:42-05:00|62|2026-11-17|2026-11-16|0|[snapshot](editions/2026-11/20261117T234342-0500.json)|[run 44239304072](https://github.com/ankitv25/Market-Observatory/actions/runs/44239304072)|
|2026-11-18T14:35:22-05:00|62|2026-11-18|2026-11-16|0|[snapshot](editions/2026-11/20261118T143522-0500.json)|[run 44381965207](https://github.com/ankitv25/Market-Observatory/actions/runs/44381965207)|
|2026-11-18T20:28:50-05:00|62|2026-11-18|2026-11-17|0|[snapshot](editions/2026-11/20261118T202850-0500.json)|[run 44437192658](https://github.com/ankitv25/Market-Observatory/actions/runs/44437192658)|
|2026-11-18T21:36:05-05:00|62|2026-11-18|2026-11-17|2|[snapshot](editions/2026-11/20261118T213605-0500.json)|[run 44445479358](https://github.com/ankitv25/Market-Observatory/actions/runs/44445479358)|
|2026-11-18T23:30:54-05:00|62|2026-11-18|2026-11-17|0|[snapshot](editions/2026-11/20261118T233054-0500.json)|[run 44458814825](https://github.com/ankitv25/Market-Observatory/actions/runs/44458814825)|
