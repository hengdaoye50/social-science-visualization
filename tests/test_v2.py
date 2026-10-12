"""Deterministic demo-fixture regression & invalid-input checks; no real data included."""
from __future__ import annotations
import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from ssv_data import prepare,load_csv
from audit_numeric import audit as numerical_audit

FIX=ROOT/'examples'/'fixtures'

def fixture(k):return json.loads((FIX/(k+'.json')).read_text(encoding='utf-8'))

def rows(k):return load_csv(FIX/(k+'.csv'),k)

class DataContractTests(unittest.TestCase):
    def test_trend_gap_not_zero(self):
        out=prepare('trend',rows('trend'),fixture('trend'))
        self.assertIsNone(next(r['value'] for r in out if r['year']==2003 and r['series']=='Group A'))

    def test_reject_duplicate_panel_key(self):
        src=rows('trend');src.append(copy.deepcopy(src[0]))
        with self.assertRaisesRegex(ValueError,'Duplicate'):prepare('trend',src,fixture('trend'))

    def test_reject_invalid_interval(self):
        src=rows('coefficients');src[0]['ci_low']='.30'
        with self.assertRaisesRegex(ValueError,'Invalid interval'):prepare('coefficients',src,fixture('coefficients'))

    def test_ratio_bounds_must_be_positive(self):
        c=fixture('coefficients');c.update(scale='ratio',null_value=1)
        with self.assertRaisesRegex(ValueError,'positive'):prepare('coefficients',rows('coefficients'),c)

    def test_reject_omitted_baseline_as_estimate(self):
        src=rows('event-study');src.append(dict(event_time='-1',estimate='0',ci_low='0',ci_high='0'))
        with self.assertRaisesRegex(ValueError,'Omitted baseline'):prepare('event-study',src,fixture('event-study'))

    def test_reject_duplicate_event_time(self):
        src=rows('event-study');src.append(copy.deepcopy(src[0]))
        with self.assertRaisesRegex(ValueError,'Duplicate'):prepare('event-study',src,fixture('event-study'))

    def test_map_zero_and_missing_distinct(self):
        geo=json.loads((FIX/'synthetic-not-geography.geojson').read_text(encoding='utf-8'))
        out=prepare('policy-map',rows('policy-map'),fixture('policy-map'),geo)
        self.assertEqual(next(r['value'] for r in out if r['region_id']=='A'),0)
        self.assertIsNone(next(r['value'] for r in out if r['region_id']=='C'))

    def test_map_reject_unmatched_boundaries(self):
        geo=json.loads((FIX/'synthetic-not-geography.geojson').read_text(encoding='utf-8'))
        with self.assertRaisesRegex(ValueError,'coverage mismatch'):
            prepare('policy-map',rows('policy-map')[:-1],fixture('policy-map'),geo)

    def test_map_reject_unjustified_crs(self):
        geo=json.loads((FIX/'synthetic-not-geography.geojson').read_text(encoding='utf-8'))
        c=fixture('policy-map');c['crs']='EPSG:3857'
        with self.assertRaisesRegex(ValueError,'EPSG:4326'):prepare('policy-map',rows('policy-map'),c,geo)

    def test_reject_nonfinite(self):
        src=rows('trend');src[0]['value']='inf'
        with self.assertRaisesRegex(ValueError,'finite'):prepare('trend',src,fixture('trend'))

class RenderAudits(unittest.TestCase):
    def test_all_4_render_and_audit(self):
        from render_figure import render
        with tempfile.TemporaryDirectory() as temp:
            for kind in ('trend','coefficients','event-study','policy-map'):
                with self.subTest(kind=kind):
                    geo=FIX/'synthetic-not-geography.geojson' if kind=='policy-map' else None
                    out=render(kind,FIX/(kind+'.csv'),FIX/(kind+'.json'),Path(temp)/kind,geo)
                    errors,warnings=numerical_audit(out/'figure-manifest.json')
                    self.assertFalse(errors,errors)
                    self.assertTrue((out/'figure-data.json').exists())
                    for ext in ('png','svg','pdf'):
                        self.assertTrue((out/('fig-2-'+kind+'.'+ext)).is_file())

    def test_detect_modified_source_and_sidecar(self):
        from render_figure import render
        with tempfile.TemporaryDirectory() as temp:
            # Copy source so tampering cannot affect tracked fixtures.
            source=Path(temp)/'trend.csv';source.write_bytes((FIX/'trend.csv').read_bytes())
            out=render('trend',source,FIX/'trend.json',Path(temp)/'out')
            self.assertFalse(numerical_audit(out/'figure-manifest.json')[0])
            source.write_text(source.read_text(encoding='utf-8')+'2007,Group A,999\n',encoding='utf-8')
            self.assertTrue(any('Checksum mismatch' in x for x in numerical_audit(out/'figure-manifest.json')[0]))
            source.write_bytes((FIX/'trend.csv').read_bytes())
            snap=out/'figure-data.json';s=json.loads(snap.read_text(encoding='utf-8'));s['rows'][0]['value']=999
            snap.write_text(json.dumps(s),encoding='utf-8')
            self.assertTrue(any('Checksum mismatch' in x for x in numerical_audit(out/'figure-manifest.json')[0]))

if __name__=='__main__':unittest.main()
