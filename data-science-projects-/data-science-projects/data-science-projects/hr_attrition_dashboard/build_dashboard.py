"""Build a single-file offline HTML dashboard from the current CSV."""
from pathlib import Path
import hashlib
import json
import pandas as pd
ROOT=Path(__file__).resolve().parent

def main():
    frame=pd.read_csv(ROOT/'hr_attrition.csv')
    template=(ROOT/'dashboard_template.html').read_text()
    library=(ROOT/'vendor/chart.umd.min.js').read_text()
    output=template.replace('__CHART_JS__',library.replace('</script','<\\/script')).replace('__HR_DATA__',frame.to_json(orient='records'))
    if '__HR_DATA__' in output or '__CHART_JS__' in output:raise ValueError('Unresolved dashboard template')
    (ROOT/'dashboard.html').write_text(output)
    manifest={'data_source':'synthetic generated snapshot','csv_sha256':hashlib.sha256((ROOT/'hr_attrition.csv').read_bytes()).hexdigest(),'employees':len(frame),'chart_js_version':'4.4.4','chart_js_sha256':hashlib.sha256((ROOT/'vendor/chart.umd.min.js').read_bytes()).hexdigest()}
    (ROOT/'dashboard_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Built offline dashboard for',len(frame),'synthetic employees')

if __name__=='__main__':main()
