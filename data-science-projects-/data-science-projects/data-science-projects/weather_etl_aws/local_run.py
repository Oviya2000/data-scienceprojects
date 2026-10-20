"""Run the supported subset of this repository's ASL locally; never deploy AWS resources."""
import argparse
import importlib
import json
import os
from pathlib import Path
import string
import sys
import time
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'lambdas'))
SUBSTITUTIONS={f'{name}Arn':f'{module}.handler' for name,module in [('Fetch','fetch_weather'),('Validate','validate'),('Transform','transform'),('Load','load_partitioned'),('Notify','notify_failure')]}
SM=json.loads(string.Template((HERE/'statemachine/pipeline.asl.json').read_text()).safe_substitute(SUBSTITUTIONS))

class PipelineFailure(RuntimeError):
    pass

def invoke(ref,payload):
    module,handler=ref.split('.')
    return getattr(importlib.import_module(module),handler)(payload,None)

def run(machine=None, invoke_fn=invoke, sleep_fn=time.sleep, max_transitions=100):
    """Interpreter for this ASL file, with bounded transitions and injected test hooks."""
    machine=machine or SM
    name=machine['StartAt'];ctx={}
    for _ in range(max_transitions):
        state=machine['States'][name];kind=state['Type']
        print(f'[{name}] {kind}')
        if kind=='Task':
            retry=state.get('Retry',[{}])[0]
            jumped=False
            for attempt in range(retry.get('MaxAttempts',0)+1):
                try:
                    payload=invoke_fn(state['Parameters']['FunctionName'],ctx)
                    result={'Payload':payload}
                    break
                except Exception as exc:
                    if attempt<retry.get('MaxAttempts',0):
                        sleep_fn(retry.get('IntervalSeconds',1)*retry.get('BackoffRate',1)**attempt)
                        continue
                    catches=state.get('Catch',[])
                    if not catches:raise
                    ctx={**ctx,'error':{'Error':type(exc).__name__,'Cause':str(exc)}}
                    name=catches[0]['Next'];jumped=True
            if jumped:continue
            selector=state.get('ResultSelector',{})
            if selector:
                new={}
                for key,path in selector.items():
                    value=result
                    for part in path.removeprefix('$.').split('.'):
                        value=value[part]
                    new[key.removesuffix('.$')]=value
                ctx=new
            else:ctx=payload
        elif kind=='Choice':
            name=next((c['Next'] for c in state['Choices'] if ctx.get(c['Variable'].removeprefix('$.'),0)>c['NumericGreaterThan']),state['Default'])
            continue
        elif kind=='Pass':
            ctx=state.get('Result',ctx)
        elif kind=='Fail':
            raise PipelineFailure(state.get('Cause',state.get('Error','Pipeline failed')))
        else:
            raise NotImplementedError(f'Unsupported local ASL state type {kind}')
        if state.get('End'):
            print(json.dumps({k:v for k,v in ctx.items() if k!='records'},default=str))
            return ctx
        name=state['Next']
    raise RuntimeError('Transition limit reached; possible state-machine loop')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true',help='Fetch live Open-Meteo observations; API failures raise errors')
    args=parser.parse_args()
    # This command writes locally even if a developer shell has AWS variables set.
    os.environ.pop('DATA_BUCKET',None);os.environ.pop('TOPIC_ARN',None)
    os.environ['USE_MOCK_WEATHER']='0' if args.live else '1'
    print('Data source:', 'live Open-Meteo' if args.live else 'explicit synthetic mock')
    run()
