"""Test the Python adapter's fidelity to a labelled precomputed result object."""
from __future__ import annotations
import csv,importlib.util,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('py_adapter',ROOT/'scripts/adapters/python_statsmodels.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
try: import pandas as pd
except ImportError: pd=None
@unittest.skipIf(pd is None,'pandas absent: optional integration test')
class AdapterTest(unittest.TestCase):
    def test_preserve_fitted_values(self):
        class FakeAlreadyFitted:
            params=pd.Series({'x1':.12,'x2':-.07})
            def conf_int(self,alpha=.05):
                assert alpha==.05
                return pd.DataFrame({0:{'x1':.02,'x2':-.14},1:{'x1':.22,'x2':.00}})
        with tempfile.TemporaryDirectory() as d:
            dest=adapter.export_fitted_model(FakeAlreadyFitted(),Path(d)/'out.csv',model_name='Fixture')
            with dest.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
            self.assertEqual(rows[0],{'term':'x1','model':'Fixture','estimate':'0.12','ci_low':'0.02','ci_high':'0.22'})
            self.assertEqual(rows[1]['ci_high'],'0.0')
if __name__=='__main__':unittest.main()
