"""Write genuine Parquet with a stable schema, grouped by UTC observation date."""
import hashlib
import os
from pathlib import Path
import uuid
from datetime import timezone
from collections import defaultdict
from validate import observation_time

def handler(event,context=None):
    import pyarrow as pa
    import pyarrow.parquet as pq
    records=event.get('records',[])
    run_id=str(event.get('run_id') or uuid.uuid4())
    if not records:return {'run_id':run_id,'loaded':0,'s3_uri':None,'s3_uris':[]}
    schema=pa.schema([('city',pa.string()),('country',pa.string()),('latitude',pa.float64()),('longitude',pa.float64()),
        ('observed_at_utc',pa.timestamp('us')),('temperature_c',pa.float64()),('humidity_pct',pa.float64()),
        ('wind_speed_kmh',pa.float64()),('condition',pa.string()),('data_source',pa.string()),
        ('feels_like_c',pa.float64()),('comfort_band',pa.string())])
    groups=defaultdict(list)
    for row in records:
        timestamp=observation_time(row['observed_at_utc'])
        # Store UTC wall time as a Parquet timestamp matching the Athena TIMESTAMP column.
        groups[timestamp.date()].append({**row,'observed_at_utc':timestamp.replace(tzinfo=None)})
    uris=[]
    token=hashlib.sha256(run_id.encode()).hexdigest()[:16]
    for day,group in sorted(groups.items()):
        key=f'curated/readings/year={day:%Y}/month={day:%m}/day={day:%d}/readings_{token}.parquet'
        table=pa.Table.from_pylist(group,schema=schema)
        if os.getenv('DATA_BUCKET'):
            import boto3
            buffer=pa.BufferOutputStream();pq.write_table(table,buffer)
            boto3.client('s3').put_object(Bucket=os.environ['DATA_BUCKET'],Key=key,Body=buffer.getvalue().to_pybytes(),ContentType='application/vnd.apache.parquet')
            uri=f"s3://{os.environ['DATA_BUCKET']}/{key}"
        else:
            path=Path(key);path.parent.mkdir(parents=True,exist_ok=True);pq.write_table(table,path);uri=str(path)
        uris.append(uri)
    return {'run_id':run_id,'loaded':len(records),'s3_uri':uris[0] if len(uris)==1 else None,'s3_uris':uris}
