"""Regression checks for analytical correctness after run_all.py generates outputs."""
from pathlib import Path
import importlib.util
import json
import sqlite3
import sys
import unittest
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]/'data-science-projects'
sys.path.insert(0,str(ROOT/'telco_churn_prediction'))
from evaluation import dataset_splits,features,target

class RetailTests(unittest.TestCase):
    def setUp(self):
        self.root=ROOT/'retail_sql_analytics'
        self.con=sqlite3.connect(self.root/'retail.db')
    def tearDown(self):self.con.close()
    def test_revenue_and_foreign_keys(self):
        self.assertEqual(self.con.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertEqual(self.con.execute('PRAGMA foreign_key_check').fetchall(),[])
        expected=self.con.execute('SELECT sum(quantity*unit_price) FROM order_items').fetchone()[0]
        for name in ['q1','q3']:
            self.assertAlmostEqual(pd.read_csv(self.root/f'results/{name}.csv').revenue.sum(),expected,places=6)
    def test_q10_counts_include_first_purchase(self):
        rows=pd.read_csv(self.root/'results/q10.csv')
        self.assertEqual(len(rows),15)
        for row in rows.itertuples():
            actual=self.con.execute('SELECT count(*) FROM orders WHERE customer_id=?',(row.customer_id,)).fetchone()[0]
            self.assertEqual(row.orders,actual)
            self.assertGreaterEqual(actual,3)
    def test_cohort_denominators_and_unobserved_horizons(self):
        rows=pd.read_csv(self.root/'results/q6.csv')
        self.assertEqual(rows.cohort_customers.sum(),5000)
        self.assertTrue(pd.isna(rows.iloc[-1].m6_activity_pct))
        self.assertTrue(rows.filter(like='_pct').stack().between(0,100).all())

class HRTests(unittest.TestCase):
    def test_career_constraints(self):
        df=pd.read_csv(ROOT/'hr_attrition_dashboard/hr_attrition.csv')
        self.assertTrue(df.EmployeeID.is_unique)
        self.assertFalse(df.isna().any().any())
        for field in ['YearsAtCompany','YearsInCurrentRole','YearsWithCurrManager']:
            self.assertTrue((df[field]<=df.TotalWorkingYears).all())
        self.assertTrue((df.TotalWorkingYears<=df.Age-18).all())
        self.assertTrue((df.YearsSinceLastPromotion<=df.YearsInCurrentRole).all())
    def test_aggregates_reconcile(self):
        root=ROOT/'hr_attrition_dashboard';df=pd.read_csv(root/'hr_attrition.csv')
        for path in (root/'dashboard_data').glob('by_*.csv'):
            aggregate=pd.read_csv(path)
            self.assertEqual(aggregate.headcount.sum(),len(df),path.name)
            self.assertEqual(aggregate.leavers.sum(),(df.Attrition=='Yes').sum(),path.name)
    def test_offline_dashboard_has_current_source(self):
        root=ROOT/'hr_attrition_dashboard'
        import re
        html=(root/'dashboard.html').read_text()
        rows=json.loads(re.search(r'const DATA = (\[.*?\]);',html,re.S).group(1))
        df=pd.read_csv(root/'hr_attrition.csv')
        pd.testing.assert_frame_equal(pd.DataFrame(rows),df,check_dtype=False)
        self.assertNotIn('<script src=',html)

class ChurnTests(unittest.TestCase):
    def test_disjoint_complete_stratified_splits(self):
        splits=dataset_splits();ids=[set(v.customerID) for v in splits.values()]
        self.assertFalse(ids[0]&ids[1] or ids[0]&ids[2] or ids[1]&ids[2])
        self.assertEqual(len(set.union(*ids)),7043)
        rates=[target(v).mean() for v in splits.values()]
        self.assertLess(max(rates)-min(rates),.005)
    def test_selection_uses_validation_and_scaler_fits_train_only(self):
        import joblib
        root=ROOT/'telco_churn_prediction';splits=dataset_splits()
        model=joblib.load(root/'best_model.joblib')
        self.assertEqual(model.named_steps['pre'].named_transformers_['num'].n_samples_seen_,len(splits['train']))
        metrics=pd.read_csv(root/'metrics.csv')
        self.assertEqual(set(metrics.evaluation_split),{'validation'})
        summary=json.loads((root/'summary.json').read_text())
        self.assertEqual(summary['best_model'],metrics.iloc[0].model)
        self.assertFalse(summary['test_evaluated'])
    def test_frozen_thresholds_are_selected_on_validation(self):
        import joblib
        from threshold_tune import select_thresholds
        root=ROOT/'telco_churn_prediction';splits=dataset_splits()
        model=joblib.load(root/'best_model.joblib');v=splits['validation']
        _,expected,_=select_thresholds(target(v),model.predict_proba(features(v))[:,1])
        summary=json.loads((root/'threshold_summary.json').read_text())
        self.assertEqual(summary['threshold_selection_split'],'validation')
        self.assertAlmostEqual(expected.threshold,summary['validation_best_f1']['threshold'])
        test=pd.read_csv(root/'test_metrics.csv')
        self.assertEqual(set(test.evaluation_split),{'test'})
        self.assertIn('constant_prevalence_baseline',set(test.operating_point))

if __name__=='__main__':unittest.main()
