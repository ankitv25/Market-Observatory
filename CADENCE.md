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
|2026-11-19T13:39:57-05:00|62|2026-11-19|2026-11-17|0|[snapshot](editions/2026-11/20261119T133957-0500.json)|[run 44590186662](https://github.com/ankitv25/Market-Observatory/actions/runs/44590186662)|
|2026-11-19T19:55:44-05:00|62|2026-11-19|2026-11-18|0|[snapshot](editions/2026-11/20261119T195544-0500.json)|[run 44649716113](https://github.com/ankitv25/Market-Observatory/actions/runs/44649716113)|
|2026-11-19T23:19:06-05:00|62|2026-11-19|2026-11-18|1|[snapshot](editions/2026-11/20261119T231906-0500.json)|[run 44673579029](https://github.com/ankitv25/Market-Observatory/actions/runs/44673579029)|
|2026-11-20T11:56:06-05:00|62|2026-11-20|2026-11-18|0|[snapshot](editions/2026-11/20261120T115606-0500.json)|[run 44778286049](https://github.com/ankitv25/Market-Observatory/actions/runs/44778286049)|
|2026-11-20T15:24:39-05:00|62|2026-11-20|2026-11-18|0|[snapshot](editions/2026-11/20261120T152439-0500.json)|[run 44811097629](https://github.com/ankitv25/Market-Observatory/actions/runs/44811097629)|
|2026-11-20T17:58:54-05:00|62|2026-11-20|2026-11-19|1|[snapshot](editions/2026-11/20261120T175854-0500.json)|[run 44833268015](https://github.com/ankitv25/Market-Observatory/actions/runs/44833268015)|
|2026-11-20T21:18:28-05:00|62|2026-11-20|2026-11-19|1|[snapshot](editions/2026-11/20261120T211828-0500.json)|[run 44855143915](https://github.com/ankitv25/Market-Observatory/actions/runs/44855143915)|
|2026-11-20T22:57:07-05:00|62|2026-11-20|2026-11-19|0|[snapshot](editions/2026-11/20261120T225707-0500.json)|[run 44863655314](https://github.com/ankitv25/Market-Observatory/actions/runs/44863655314)|
|2026-11-21T14:36:24-05:00|62|2026-11-20|2026-11-19|1|[snapshot](editions/2026-11/20261121T143624-0500.json)|[run 44941828286](https://github.com/ankitv25/Market-Observatory/actions/runs/44941828286)|
|2026-11-22T13:35:51-05:00|62|2026-11-21|2026-11-19|1|[snapshot](editions/2026-11/20261122T133551-0500.json)|local verification|
|2026-11-22T13:40:05-05:00|62|2026-11-21|2026-11-19|1|[snapshot](editions/2026-11/20261122T134005-0500.json)|local verification|
|2026-11-22T13:43:53-05:00|62|2026-11-21|2026-11-19|2|[snapshot](editions/2026-11/20261122T134353-0500.json)|[run 45056719055](https://github.com/ankitv25/Market-Observatory/actions/runs/45056719055)|
|2026-11-22T13:46:37-05:00|62|2026-11-21|2026-11-19|2|[snapshot](editions/2026-11/20261122T134637-0500.json)|[run 45056978808](https://github.com/ankitv25/Market-Observatory/actions/runs/45056978808)|
|2026-11-23T08:14:25-05:00|62|2026-11-23|2026-11-19|0|[snapshot](editions/2026-11/20261123T081425-0500.json)|local verification|
|2026-11-23T08:16:50-05:00|62|2026-11-23|2026-11-19|0|[snapshot](editions/2026-11/20261123T081650-0500.json)|[run 45182334190](https://github.com/ankitv25/Market-Observatory/actions/runs/45182334190)|
|2026-11-23T16:16:33-05:00|62|2026-11-23|2026-11-19|1|[snapshot](editions/2026-11/20261123T161633-0500.json)|[run 45267975135](https://github.com/ankitv25/Market-Observatory/actions/runs/45267975135)|
|2026-11-23T18:52:26-05:00|62|2026-11-23|2026-11-20|1|[snapshot](editions/2026-11/20261123T185226-0500.json)|[run 45292477664](https://github.com/ankitv25/Market-Observatory/actions/runs/45292477664)|
|2026-11-23T20:35:30-05:00|62|2026-11-23|2026-11-20|1|[snapshot](editions/2026-11/20261123T203530-0500.json)|[run 45306149078](https://github.com/ankitv25/Market-Observatory/actions/runs/45306149078)|
|2026-11-23T22:24:09-05:00|62|2026-11-23|2026-11-20|0|[snapshot](editions/2026-11/20261123T222409-0500.json)|[run 45319240034](https://github.com/ankitv25/Market-Observatory/actions/runs/45319240034)|
|2026-11-24T00:24:23-05:00|62|2026-11-23|2026-11-20|0|[snapshot](editions/2026-11/20261124T002423-0500.json)|[run 45333075467](https://github.com/ankitv25/Market-Observatory/actions/runs/45333075467)|
|2026-11-24T09:19:06-05:00|62|2026-11-24|2026-11-20|0|[snapshot](editions/2026-11/20261124T091906-0500.json)|[run 45412711054](https://github.com/ankitv25/Market-Observatory/actions/runs/45412711054)|
|2026-11-24T17:26:20-05:00|62|2026-11-24|2026-11-23|3|[snapshot](editions/2026-11/20261124T172620-0500.json)|[run 45500891527](https://github.com/ankitv25/Market-Observatory/actions/runs/45500891527)|
|2026-11-24T18:26:38-05:00|62|2026-11-24|2026-11-23|1|[snapshot](editions/2026-11/20261124T182638-0500.json)|[run 45509994064](https://github.com/ankitv25/Market-Observatory/actions/runs/45509994064)|
|2026-11-24T19:39:26-05:00|62|2026-11-24|2026-11-23|1|[snapshot](editions/2026-11/20261124T193926-0500.json)|[run 45519751652](https://github.com/ankitv25/Market-Observatory/actions/runs/45519751652)|
|2026-11-25T04:10:31-05:00|62|2026-11-25|2026-11-23|0|[snapshot](editions/2026-11/20261125T041031-0500.json)|[run 45582875764](https://github.com/ankitv25/Market-Observatory/actions/runs/45582875764)|
|2026-11-25T08:33:54-05:00|62|2026-11-25|2026-11-23|0|[snapshot](editions/2026-11/20261125T083354-0500.json)|[run 45624846386](https://github.com/ankitv25/Market-Observatory/actions/runs/45624846386)|
|2026-11-25T14:15:36-05:00|62|2026-11-25|2026-11-23|1|[snapshot](editions/2026-11/20261125T141536-0500.json)|[run 45683380963](https://github.com/ankitv25/Market-Observatory/actions/runs/45683380963)|
|2026-11-25T16:40:34-05:00|62|2026-11-25|2026-11-24|1|[snapshot](editions/2026-11/20261125T164034-0500.json)|[run 45706490063](https://github.com/ankitv25/Market-Observatory/actions/runs/45706490063)|
|2026-11-25T18:01:42-05:00|62|2026-11-25|2026-11-24|1|[snapshot](editions/2026-11/20261125T180142-0500.json)|[run 45718072189](https://github.com/ankitv25/Market-Observatory/actions/runs/45718072189)|
|2026-11-25T20:03:18-05:00|62|2026-11-25|2026-11-24|1|[snapshot](editions/2026-11/20261125T200318-0500.json)|[run 45733060552](https://github.com/ankitv25/Market-Observatory/actions/runs/45733060552)|
|2026-11-25T21:19:56-05:00|62|2026-11-25|2026-11-24|1|[snapshot](editions/2026-11/20261125T211956-0500.json)|[run 45741680644](https://github.com/ankitv25/Market-Observatory/actions/runs/45741680644)|
