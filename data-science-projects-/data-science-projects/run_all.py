"""Regenerate all four synthetic/local portfolio projects; no AWS deployment."""
from pathlib import Path
import os
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
commands={
 'retail_sql_analytics':['build_db.py','run_queries.py'],
 'hr_attrition_dashboard':['generate_hr_data.py','eda.py','build_dashboard.py'],
 'telco_churn_prediction':['generate_data.py','train.py','threshold_tune.py'],
 'weather_etl_aws':['local_run.py'],
}
if __name__=='__main__':
    env=os.environ.copy();env['MPLBACKEND']='Agg';env['PYTHONUTF8']='1'
    for project,scripts in commands.items():
        for script in scripts:
            print(f'\nRunning {project}/{script}',flush=True)
            subprocess.run([sys.executable,script],cwd=ROOT/'data-science-projects'/project,env=env,check=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,env=env,check=True)
    subprocess.run([sys.executable,'tests/run_tests.py'],cwd=ROOT/'data-science-projects/weather_etl_aws',env=env,check=True)
