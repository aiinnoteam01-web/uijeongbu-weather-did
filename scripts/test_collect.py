"""Offline regression checks; fixture values never ship as displayed weather."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from collect import assemble, latest_rows, observed_at, query_day, KST
from check_data import check


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 11, 5, 9, 20, tzinfo=KST)
        self.rows = [dict(SPOT_NM=name, SPOT_NO=str(i), SIGUN_NM='의정부시', MESURE_DE='20261105', MESURE_TM='08', TP_INFO=0, RAINF_1HR_INFO=0) for i, name in enumerate(['의정부', '신곡'])]

    def test_recent_only_and_duplicate_removal(self):
        records = self.rows + [self.rows[0], dict(self.rows[0], SPOT_NM='다른지역'), dict(self.rows[0], MESURE_DE='20261001')]
        snapshot, status = assemble({}, records, [], self.now)
        self.assertTrue(status['ok']); self.assertEqual(len(snapshot['rows']), 2)
        self.assertEqual(snapshot['rows'][0]['TP_INFO'], 0)
        self.assertEqual(observed_at(snapshot['rows'][0]).hour, 8)

    def test_outage_retains_previous_receipt_and_reports_error(self):
        snapshot, _ = assemble({}, self.rows, [], self.now)
        previous_time = snapshot['generatedAt']
        snapshot, status = assemble(snapshot, [], ['접속 실패'], self.now + dt.timedelta(minutes=30))
        self.assertFalse(status['ok']); self.assertEqual(snapshot['generatedAt'], previous_time)
        self.assertEqual(len(latest_rows(snapshot['rows'])), 2)

    def test_one_missing_station_is_not_normal(self):
        _, status = assemble({}, self.rows[:1], [], self.now)
        self.assertFalse(status['ok']); self.assertIn('신곡', status['message'])

    def test_midnight_and_stale_dates(self):
        self.assertEqual(observed_at(dict(self.rows[0], MESURE_TM='00')).hour, 0)
        _, status = assemble({}, [dict(r, MESURE_DE='20261104', MESURE_TM='17') for r in self.rows], [], self.now)
        self.assertFalse(status['ok']); self.assertIn('3시간 초과', status['message'])

    def test_check_rejects_empty_and_accepts_complete(self):
        snapshot, status = assemble({}, self.rows, [], self.now)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for name, value in {'observations':snapshot, 'status':status, 'latest':{'rows':self.rows}, 'history':{'rows':self.rows}}.items():
                (path / (name+'.json')).write_text(json.dumps(value))
            self.assertTrue(check(path, self.now))
            (path/'latest.json').write_text('{"rows":[]}')
            self.assertFalse(check(path, self.now))

    def test_request_uses_compact_date_and_never_logs_key(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self): return json.dumps({'AWS1hourObser':[{'head':[{'RESULT':{'CODE':'INFO-000'}},{'list_total_count':2}]},{'row':self_rows}]}).encode()
        self_rows = self.rows
        with patch('urllib.request.urlopen', return_value=Response()) as fetch:
            self.assertEqual(len(query_day('offline-test-key', '20261105')),2)
            self.assertIn('MESURE_DE=20261105', fetch.call_args.args[0])
            self.assertIn('https://', fetch.call_args.args[0])


if __name__ == '__main__': unittest.main()
