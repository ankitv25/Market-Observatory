"""Source recovery must fetch actual observations and report what was selected."""
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from urllib.error import URLError, HTTPError
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import markets
from refresh import market_rows
from cadence import refresh_due,ZONE

class FeedRecoveryTests(unittest.TestCase):
    def test_chart_retries_other_endpoint(self):
        data={'chart':{'result':[{'meta':{'symbol':'CHF=X'}}]}}
        with patch.object(markets,'get_json',side_effect=[URLError('temporary'),data]) as fetch,patch.object(markets.time,'sleep'):
            self.assertEqual(markets.chart('CHF=X')['meta']['symbol'],'CHF=X')
        self.assertIn('query1.',fetch.call_args_list[0].args[0])
        self.assertIn('query2.',fetch.call_args_list[1].args[0])

    def test_chart_rejects_wrong_symbol_on_every_attempt(self):
        data={'chart':{'result':[{'meta':{'symbol':'EURUSD=X'}}]}}
        with patch.object(markets,'get_json',return_value=data),patch.object(markets.time,'sleep'):
            with self.assertRaisesRegex(ValueError,'Unexpected series'):
                markets.chart('CHF=X')

    def test_nonexistent_contract_is_bounded(self):
        error=HTTPError('url',404,'Not found',{},None)
        with patch.object(markets,'get_json',side_effect=error) as fetch,patch.object(markets.time,'sleep'):
            with self.assertRaises(HTTPError):markets.chart('BZX26.NYM')
        self.assertEqual(fetch.call_count,2)

    def test_failed_contract_resolution_is_rechecked_before_archive(self):
        spec={'id':'brent','symbol':'BZ=F'}
        with patch.object(markets,'INSTRUMENTS',[spec]),patch.object(markets,'live_record',side_effect=[ValueError('mismatched cached contract bars'),dict(spec,history=[['2026-11-19',90],['2026-11-20',91]])]),patch.object(markets,'archived_series') as archive:
            rows=markets.collect()
        archive.assert_not_called()
        self.assertEqual(rows[0]['collection']['status'],'live')

    def test_older_archive_does_not_masquerade_as_selected_source(self):
        old={'id':'usdchf','symbol':'CHF=X','history':[['2026-11-19',.84],['2026-11-20',.85]],'source':'Yahoo Finance'}
        archive=dict(old,source='Convexity Lab archive',history=[['2026-11-17',.82],['2026-11-18',.83]],collection={'status':'archive'})
        selected=market_rows([archive],[old],datetime(2026,11,22,tzinfo=timezone.utc))[0]
        self.assertEqual(selected['source'],'Yahoo Finance')
        self.assertEqual(selected['collection']['status'],'retained')
        self.assertEqual(selected['stats']['day'],'2026-11-20')

    def test_current_prices_with_failed_feed_are_retried_after_one_hour(self):
        created='2026-11-22T13:46:37-05:00'
        edition={'markets':[{'group':'Indices','id':'spx','stats':{'day':'2026-11-20'}}], 'market_health':{'checked':62,'live':61,'retained':1}}
        self.assertTrue(refresh_due(created,datetime(2026,11,22,15,tzinfo=ZONE),edition))
        self.assertFalse(refresh_due(created,datetime(2026,11,22,14,tzinfo=ZONE),edition))
        edition['market_health']={'checked':62,'live':62}
        self.assertFalse(refresh_due(created,datetime(2026,11,22,15,tzinfo=ZONE),edition))

if __name__=='__main__':unittest.main()
