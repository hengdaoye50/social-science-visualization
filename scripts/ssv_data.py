"""Normalized CSV contract and deterministic series preparation; no model estimation.

This module does not fetch external data or change the input. Blank numeric cells mean
missing, never zero. The returned values are used for plotting and a JSON sidecar.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

KINDS = ('trend', 'coefficients', 'event-study', 'policy-map')
REQUIRED = {
 'trend': ('year', 'series', 'value'),
 'coefficients': ('term', 'model', 'estimate', 'ci_low', 'ci_high'),
 'event-study': ('event_time', 'estimate', 'ci_low', 'ci_high'),
 'policy-map': ('region_id', 'value'),
}

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_csv(p, kind):
    if kind not in KINDS: raise ValueError(f'Unknown figure type: {kind}')
    with Path(p).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('CSV header missing or duplicate')
        missing = set(REQUIRED[kind]) - set(reader.fieldnames)
        if missing: raise ValueError(f'Missing CSV columns: {sorted(missing)}')
        rows = list(reader)
        if any(None in row or any(row.get(k) is None for k in REQUIRED[kind]) for row in rows):
            raise ValueError('Malformed CSV row / inconsistent column count')
    if not rows: raise ValueError('Empty CSV')
    return rows

def number(s, field, *, missing=False):
    if s is None or str(s).strip() == '':
        if missing: return None
        raise ValueError(f'{field} cannot be blank')
    try: n = float(s)
    except (TypeError, ValueError): raise ValueError(f'{field} is not numeric: {s!r}') from None
    if not math.isfinite(n): raise ValueError(f'{field} must be finite')
    return n

def integer(s, field):
    n = number(s, field)
    if n != int(n): raise ValueError(f'{field} must be integer')
    return int(n)

def nonempty(s, field):
    if not isinstance(s, str) or not s.strip(): raise ValueError(f'{field} required')
    return s.strip()

def validate_config(kind, cfg):
    for k in ('figure_id','title','question','source','unit_of_analysis','population','time_window','unit','caption','alt_text','missingness','weights','transformations','data_restrictions'):
        nonempty(cfg.get(k), f'config.{k}')
    if cfg.get('status') not in ('demo','research'):
        raise ValueError('config.status must be demo or research')
    if kind in ('coefficients','event-study'):
        for k in ('estimand','method','interval_label','se_method','reference_group'):
            nonempty(cfg.get(k), f'config.{k}')
    if kind == 'coefficients':
        if cfg.get('scale') not in ('difference','ratio'): raise ValueError('config.scale difference/ratio required')
        null = cfg.get('null_value')
        if type(null) not in (int,float) or not math.isfinite(null): raise ValueError('config.null_value finite number required')
        if cfg['scale']=='ratio' and null!=1: raise ValueError('Ratio scale requires null_value=1')
    if kind == 'event-study':
        for k in ('baseline_event_time','intervention_event_time'):
            v=cfg.get(k)
            if type(v) is not int: raise ValueError(f'config.{k} must be integer')
        if cfg['baseline_event_time']>=cfg['intervention_event_time']:
            raise ValueError('Omitted baseline must precede intervention')
    if kind == 'policy-map':
        for k in ('boundary_source','boundary_year','data_year','region_id_field','crs'):
            nonempty(cfg.get(k), f'config.{k}')
        if cfg['crs'] != 'EPSG:4326':
            raise ValueError('GeoJSON input must explicitly declare EPSG:4326; reproject externally and document the transformation')

def prepare(kind, csv_rows, cfg, boundaries=None):
    validate_config(kind, cfg)
    out=[]; seen=set()
    if kind=='trend':
        for r in csv_rows:
            year=integer(r['year'],'year'); series=nonempty(r['series'],'series'); v=number(r['value'],'value',missing=True)
            key=(year,series)
            if key in seen: raise ValueError(f'Duplicate panel/year group: {key}')
            seen.add(key); out.append(dict(year=year,series=series,value=v))
        out.sort(key=lambda r:(r['series'],r['year']))
    elif kind=='coefficients':
        ratio=cfg['scale']=='ratio'
        if cfg['null_value'] != (1 if ratio else 0):
            raise ValueError('For differences null_value must be 0; ratio null_value must be 1')
        for r in csv_rows:
            term=nonempty(r['term'],'term'); model=nonempty(r['model'],'model')
            vals=[number(r[x],x) for x in ('estimate','ci_low','ci_high')]
            v,lo,hi=vals
            if lo>v or v>hi: raise ValueError(f'Invalid interval for {term}, {model}')
            if ratio and lo<=0: raise ValueError('Ratio CI and estimate must all be positive')
            key=(model,term)
            if key in seen: raise ValueError(f'Duplicate coefficient: {key}')
            seen.add(key);out.append(dict(model=model,term=term,estimate=v,ci_low=lo,ci_high=hi))
        out.sort(key=lambda r:(r['model'],r['term']))
    elif kind=='event-study':
        for r in csv_rows:
            t=integer(r['event_time'],'event_time');v,lo,hi=[number(r[x],x) for x in ('estimate','ci_low','ci_high')]
            if t==cfg['baseline_event_time']:
                raise ValueError('Omitted baseline must NOT be a supplied estimate; label it in caption only')
            if t in seen: raise ValueError(f'Duplicate event time {t}')
            if lo>v or v>hi: raise ValueError(f'Invalid interval at event time {t}')
            seen.add(t);out.append(dict(event_time=t,estimate=v,ci_low=lo,ci_high=hi))
        out.sort(key=lambda r:r['event_time'])
    else:
        if boundaries is None: raise ValueError('Actual, documented GeoJSON boundaries required for a map')
        ids=set()
        if boundaries.get('type')!='FeatureCollection' or not isinstance(boundaries.get('features'), list):
            raise ValueError('Boundaries must be GeoJSON FeatureCollection')
        if not boundaries['features']: raise ValueError('Empty boundaries')
        if boundaries.get('crs') and '4326' not in json.dumps(boundaries['crs']):
            raise ValueError('GeoJSON CRS conflicts with EPSG:4326 config')
        for f in boundaries['features']:
            if not isinstance(f,dict) or not isinstance(f.get('properties'),dict) or not isinstance(f.get('geometry'),dict):
                raise ValueError('GeoJSON feature missing geometry/properties')
            geom=f['geometry']
            if geom.get('type') not in ('Polygon','MultiPolygon') or not geom.get('coordinates'):
                raise ValueError('Polygon/MultiPolygon with coordinates required')
            raw_id=f['properties'].get(cfg['region_id_field'])
            if raw_id is None: raise ValueError('GeoJSON feature missing region ID')
            k=nonempty(str(raw_id).strip(), 'feature region_id')
            if k in ids: raise ValueError(f'Duplicate GeoJSON region ID {k}')
            ids.add(k)
        for r in csv_rows:
            k=nonempty(r['region_id'],'region_id');v=number(r['value'],'value',missing=True)
            if k in seen: raise ValueError(f'Duplicate region ID {k}')
            seen.add(k);out.append(dict(region_id=k,value=v))
        if seen!=ids:
            raise ValueError(f'CSV / boundary coverage mismatch (missing: {sorted(ids-seen)}, extraneous: {sorted(seen-ids)}); list missing values explicitly as blank rows')
        out.sort(key=lambda r:r['region_id'])
    return out
