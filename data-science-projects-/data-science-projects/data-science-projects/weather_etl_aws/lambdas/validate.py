"""Drop malformed observations without crashing the whole batch."""
from datetime import datetime, timezone
import math
REQUIRED=['city','country','latitude','longitude','observed_at_utc','temperature_c','humidity_pct','wind_speed_kmh','condition','data_source']
RANGES={'latitude':(-90,90),'longitude':(-180,180),'temperature_c':(-70,60),'humidity_pct':(0,100),'wind_speed_kmh':(0,250)}

def observation_time(value):
    if not isinstance(value,str):raise ValueError('Expected ISO timestamp')
    timestamp=datetime.fromisoformat(value.replace('Z','+00:00'))
    if timestamp.tzinfo is None:raise ValueError('Timestamp must specify UTC offset')
    return timestamp.astimezone(timezone.utc)

def valid(row):
    if not isinstance(row,dict) or any(row.get(k) is None for k in REQUIRED):return False
    if any(not isinstance(row[k],str) or not row[k].strip() for k in ['city','country','condition']):return False
    if row['data_source'] not in ['mock','open-meteo']:return False
    try:observation_time(row['observed_at_utc'])
    except (TypeError,ValueError,OverflowError):return False
    for name,(low,high) in RANGES.items():
        value=row[name]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low<=value<=high:return False
    return True

def handler(event,context=None):
    records=event.get('records',[])
    kept=[r for r in records if valid(r)]
    return {'run_id':event.get('run_id'),'records':kept,'valid_count':len(kept),'dropped_count':len(records)-len(kept)}
