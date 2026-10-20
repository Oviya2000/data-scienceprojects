"""Real-browser checks with network blocked. Requires requirements-browser.txt and Chromium."""
from itertools import product
from pathlib import Path
import argparse
import csv
import json
import tempfile
import pandas as pd
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HR=ROOT/'data-science-projects/hr_attrition_dashboard'

def main(screenshots=False):
    df=pd.read_csv(HR/'hr_attrition.csv')
    mounts={'Department':'#slicer-dept','OverTime':'#slicer-ot','Gender':'#slicer-gender','BusinessTravel':'#slicer-travel'}
    errors=[];requests=[];checks=0
    with sync_playwright() as pw:
        browser=pw.chromium.launch(args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1100},accept_downloads=True)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http://','https://')) else None)
        page.route('https://**/*',lambda route:route.abort())
        page.route('http://**/*',lambda route:route.abort())
        page.goto((HR/'dashboard.html').as_uri())
        assert page.evaluate('Object.keys(Chart.instances).length')==7
        assert page.locator('#kpis .value').nth(0).inner_text()==f'{len(df):,}'
        choices=[[None]+sorted(df[f].unique().tolist()) for f in mounts]
        for values in product(*choices):
            page.locator('#reset').click();expected=df
            for (field,mount),value in zip(mounts.items(),values):
                if value is not None:
                    page.locator(mount).get_by_role('button',name=value,exact=True).click()
                    expected=expected[expected[field]==value]
            kpis=page.locator('#kpis .value').all_text_contents()
            assert int(kpis[0].replace(',',''))==len(expected),(values,kpis)
            assert int(kpis[1].replace(',',''))==int((expected.Attrition=='Yes').sum())
            if not len(expected):assert kpis[2]=='N/A'
            charts=page.evaluate("({department:Chart.getChart('c-dept').data.datasets.map(d=>d.data),age:Chart.getChart('c-age').data.datasets[0].data})")
            assert sum(charts['department'][0])+sum(charts['department'][1])==len(expected)
            age=pd.cut(expected.Age,bins=[20,30,40,50,100],right=False,labels=['20-29','30-39','40-49','50+'])
            for i,label in enumerate(['20-29','30-39','40-49','50+']):
                group=expected[age==label]
                rate=100*(group.Attrition=='Yes').mean() if len(group) else 0
                assert abs(float(charts['age'][i])-rate)<=.051
            checks+=1
        # A real UI selection and downloaded data must agree.
        page.locator('#reset').click()
        page.locator('#slicer-dept').get_by_role('button',name='Sales',exact=True).click()
        expected=df[df.Department=='Sales']
        with page.expect_download() as pending:page.locator('#download').click()
        with open(pending.value.path(),encoding='utf-8') as handle:downloaded=list(csv.DictReader(handle))
        assert len(downloaded)==len(expected)
        assert {r['EmployeeID'] for r in downloaded}==set(expected.EmployeeID.astype(str))
        page.locator('#reset').click()
        for width in [320,390,768,1440]:
            page.set_viewport_size({'width':width,'height':1000})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
            if screenshots and width in [390,1440]:
                page.screenshot(path=str(ROOT.parent/f'improved-hr-{width}-qa.png'),full_page=True)
        assert not errors,errors
        assert not requests,requests
        browser.close()
    print(json.dumps({'filter_combinations':checks,'charts':7,'phone_widths_checked':[320,390,768,1440],'external_requests':len(requests),'page_errors':errors,'csv_export':'reconciled'},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--screenshots',action='store_true');args=parser.parse_args()
    main(args.screenshots)
