"""Mock-only tests for validation, genuine Parquet output, retries and terminal failure."""
from pathlib import Path
import copy
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import pyarrow.parquet as pq
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(HERE.parent/'lambdas'))
import fetch_weather,validate,transform,load_partitioned,local_run

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.environment=patch.dict(os.environ,{'USE_MOCK_WEATHER':'1','DATA_BUCKET':'','TOPIC_ARN':''})
        self.environment.start()
    def tearDown(self):self.environment.stop()
    def records(self):return fetch_weather.handler({})
    def test_explicit_mock_provenance(self):
        result=self.records()
        self.assertEqual(len(result['records']),10)
        self.assertTrue(all(r['data_source']=='mock' for r in result['records']))
    def test_live_failure_never_substitutes_mock(self):
        from urllib.error import URLError
        with patch.dict(os.environ,{'USE_MOCK_WEATHER':'0'}),patch.object(fetch_weather,'fetch_one',side_effect=URLError('offline')):
            self.assertRaises(RuntimeError,fetch_weather.handler,{})
    def test_validation_handles_bad_types_and_nonfinite_values(self):
        good=self.records()['records'][0]
        for value in ['hot',None,float('nan'),float('inf'),True]:
            self.assertFalse(validate.valid({**good,'temperature_c':value}))
        self.assertFalse(validate.valid({**good,'observed_at_utc':'not a timestamp'}))
        self.assertFalse(validate.valid({**good,'observed_at_utc':'2026-01-01T00:00:00'}))
        self.assertTrue(validate.valid(good))
    def test_validation_counts_bad_rows(self):
        result=self.records();result['records'].append({'city':'broken'})
        out=validate.handler(result)
        self.assertEqual((out['valid_count'],out['dropped_count']),(10,1))
    def test_transform_preserves_inputs(self):
        result=self.records();before=copy.deepcopy(result)
        out=transform.handler(result)
        self.assertEqual(result,before)
        self.assertIn('feels_like_c',out['records'][0])
    def test_partition_dates_and_idempotent_keys(self):
        event=transform.handler(self.records());event['run_id']='fixed'
        event['records'][0]['observed_at_utc']='2026-01-01T23:59:59Z'
        event['records'][1]['observed_at_utc']='2026-01-02T00:00:00Z'
        event['records']=event['records'][:2]
        with tempfile.TemporaryDirectory() as directory:
            previous=os.getcwd();os.chdir(directory)
            try:
                first=load_partitioned.handler(event);second=load_partitioned.handler(event)
                self.assertEqual(first['s3_uris'],second['s3_uris'])
                self.assertEqual(len(first['s3_uris']),2)
                self.assertEqual(sum(pq.read_table(p).num_rows for p in first['s3_uris']),2)
                self.assertIn('day=01',first['s3_uris'][0]);self.assertIn('day=02',first['s3_uris'][1])
            finally:os.chdir(previous)
    def test_retry_recovers(self):
        calls=[];delays=[]
        machine={'StartAt':'One','States':{'One':{'Type':'Task','Parameters':{'FunctionName':'fake.handler'},'Retry':[{'MaxAttempts':2,'IntervalSeconds':1,'BackoffRate':2}],'End':True}}}
        def invoke(ref,payload):
            calls.append(ref)
            if len(calls)<3:raise RuntimeError('transient')
            return {'ok':True}
        self.assertEqual(local_run.run(machine,invoke_fn=invoke,sleep_fn=delays.append),{'ok':True})
        self.assertEqual(delays,[1,2])
    def test_notify_then_fail_terminates(self):
        calls=[]
        def invoke(ref,payload):
            calls.append(ref)
            if ref=='fetch_weather.handler':raise RuntimeError('injected failure')
            self.assertIn('error',payload)
            return {'notified':False}
        with self.assertRaises(local_run.PipelineFailure):
            local_run.run(invoke_fn=invoke,sleep_fn=lambda _:None,max_transitions=10)
        self.assertEqual(calls.count('notify_failure.handler'),1)
    def test_no_records_skips_transform_and_load(self):
        calls=[]
        def invoke(ref,payload):
            calls.append(ref)
            return {'run_id':'empty','records':[],'valid_count':0}
        out=local_run.run(invoke_fn=invoke)
        self.assertEqual(out['status'],'no records to load')
        self.assertFalse(any('load_partitioned' in c for c in calls))

if __name__=='__main__':unittest.main()
