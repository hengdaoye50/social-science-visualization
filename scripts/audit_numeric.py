#!/usr/bin/env python3
"""Source-to-plotted-data consistency audit for v2 renderer (stdlib-only).

Checks byte hashes, recomputes normalized CSV rows, checks explicit source/geometry
coverage and interval arithmetic. Does NOT independently validate model estimates,
plot pixels, source legitimacy, CRSs/projections, or statistical identification.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from ssv_data import digest, load_csv, prepare, KINDS


def local_path(base, rel):
    if not isinstance(rel, str) or not rel.strip(): raise ValueError('Missing referenced path')
    return (base / rel).resolve()

def audit(manifest):
    errors=[];warnings=[]
    try:
        manifest=Path(manifest).resolve();m=json.loads(manifest.read_text(encoding='utf-8'))
        p=m['pipeline']
        if p['version']!=2 or p['kind'] not in KINDS: raise ValueError('Not a supported v2 manifest')
        base=manifest.parent
        for pathkey, hashkey in [('input_csv','input_sha256'),('config_json','config_sha256'),
                                  ('figure_data','figure_data_sha256'),('boundaries_geojson','boundaries_sha256')]:
            if pathkey=='boundaries_geojson' and pathkey not in p: continue
            file=local_path(base,p[pathkey])
            if not file.is_file(): errors.append(f'Missing {pathkey}: {file}');continue
            if digest(file)!=p[hashkey]: errors.append(f'Checksum mismatch: {pathkey} (file changed since render)')
        if errors: return errors,warnings
        kind=p['kind'];cfg=json.loads(local_path(base,p['config_json']).read_text(encoding='utf-8'))
        source=load_csv(local_path(base,p['input_csv']),kind)
        geo=(json.loads(local_path(base,p['boundaries_geojson']).read_text(encoding='utf-8'))
             if 'boundaries_geojson' in p else None)
        rebuilt=prepare(kind,source,cfg,geo)
        snap=json.loads(local_path(base,p['figure_data']).read_text(encoding='utf-8'))
        if snap!={'kind':kind,'rows':rebuilt}: errors.append('Plotted-data snapshot differs from normalized source CSV')
        visible=sum(r.get('value',r.get('estimate')) is not None for r in rebuilt)
        if type(p.get('n_plotted')) is not int or p['n_plotted']!=visible:
            errors.append(f'n_plotted mismatch: expected {visible}')
        if m['design']!=kind: errors.append('Manifest design/pipeline kind disagree')
        if kind=='event-study':
            if cfg['baseline_event_time'] in {r['event_time'] for r in rebuilt}:
                errors.append('Omitted baseline is incorrectly treated as an estimate')
            warnings.append('Event-study pointwise CIs and identifying assumptions were NOT independently evaluated')
        if kind=='coefficients':
            warnings.append('Coefficient/CI provenance and comparability require independent model review')
        if kind=='policy-map':
            warnings.append('Boundary authority, administrative changes and map compliance require separate review')
        if m['status']=='demo': warnings.append('Synthetic fixture only, not empirical findings')
        warnings.append('Source-to-sidecar audit cannot verify rendered pixels, independent model estimation or visual quality')
    except (OSError,ValueError,TypeError,KeyError,UnicodeDecodeError) as ex:
        errors.append(f'Cannot complete numerical consistency audit: {ex}')
    return errors,warnings

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('manifest',type=Path)
    ap.add_argument('--strict',action='store_true',help='Warnings also produce nonzero exit')
    args=ap.parse_args();errors,warns=audit(args.manifest)
    for e in errors:print('ERROR:',e)
    for w in warns:print('WARN:',w)
    print(f'Source-to-sidecar audit: {len(errors)} error(s), {len(warns)} warning(s)')
    return int(bool(errors or (args.strict and warns)))
if __name__=='__main__':sys.exit(main())
