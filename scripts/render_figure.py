#!/usr/bin/env python3
"""Render normalized, already-computed results. No re-estimation or internet use.
Usage: python scripts/render_figure.py trend|coefficients|event-study|policy-map --input file.csv --config config.json --out DIR [--boundaries file.geojson]
Requires matplotlib; policy-map additionally requires geopandas and shapely/fiona/pyogrio as its installed backends.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, colors, cm
from matplotlib.patches import Patch
from ssv_data import KINDS, load_csv, prepare, digest, validate_config

BLUE='#28577C'; ORANGE='#AC693A'; TEXT='#28323A'; GRID='#D6DDE1'

def setup_font(cfg):
    non_ascii=any(ord(c)>127 for v in cfg.values() if isinstance(v,str) for c in v)
    cjk=['Noto Sans CJK SC','Source Han Sans SC','Microsoft YaHei','PingFang SC','SimHei','WenQuanYi Zen Hei','AR PL SungtiL GB']
    candidates=cjk+['DejaVu Sans'] if non_ascii else ['DejaVu Sans']+cjk
    # Never bundle system font files in the skill.
    for path in font_manager.findSystemFonts():
        if Path(path).name == 'gbsn00lp.ttf':
            font_manager.fontManager.addfont(path)
            break
    font='DejaVu Sans'
    for x in candidates:
        try: font_manager.findfont(x,fallback_to_default=False);font=x;break
        except ValueError: continue
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':[font,'DejaVu Sans'],
        'svg.fonttype':'none','pdf.fonttype':42,'axes.unicode_minus':False,
        'axes.spines.top':False,'axes.spines.right':False,
        'text.color':TEXT,'axes.labelcolor':TEXT,'xtick.color':TEXT,'ytick.color':TEXT,
        'savefig.facecolor':'white'})
    return font

def marker(ax,cfg):
    if cfg['status']=='demo':
        ax.text(.98,.98,'SYNTHETIC DEMO — NOT EVIDENCE',transform=ax.transAxes,
                ha='right',va='top',fontsize=8,color='#963939',weight='bold',
                bbox=dict(facecolor='white',edgecolor='none',alpha=.82,pad=2))

def line_trend(ax,rows,cfg):
    by=defaultdict(dict)
    for r in rows: by[r['series']][r['year']]=r['value']
    palette=[BLUE,ORANGE,'#58856A','#83649A','#535B64']
    for j,(name,series) in enumerate(sorted(by.items())):
        years=list(range(min(series),max(series)+1))
        vals=[float('nan') if series.get(y) is None else series[y] for y in years]
        ax.plot(years,vals,marker=['o','s','^','D','x'][j%5],linestyle=['-','--','-.',':'][j%4],
                ms=3.5,lw=1.8,label=name,color=palette[j%len(palette)])
    ax.set_xlabel('Year');ax.set_ylabel(cfg['unit']);ax.grid(axis='y',color=GRID,lw=.6)
    if len(by)>1: ax.legend(frameon=False,ncol=min(3,len(by)))
    ax.set_xlim(min(r['year'] for r in rows)-.3,max(r['year'] for r in rows)+.3)

def line_coeff(ax,rows,cfg):
    models=sorted({r['model'] for r in rows});terms=sorted({r['term'] for r in rows});n=len(models)
    pal=[BLUE,ORANGE,'#58856A','#83649A','#535B64']
    for j,m in enumerate(models):
        sub={r['term']:r for r in rows if r['model']==m}
        for i,t in enumerate(terms):
            if t not in sub: continue
            r=sub[t];y=i+(j-(n-1)/2)*.7/max(1,n)
            ax.errorbar(r['estimate'],y,xerr=[[r['estimate']-r['ci_low']],[r['ci_high']-r['estimate']]],
                fmt=['o','s','^','D'][j%4],ms=5,lw=1.4,capsize=2.5,color=pal[j%len(pal)],
                label=m if i==0 else None)
    ax.axvline(cfg['null_value'],color='#60666A',lw=1,ls='--')
    ax.set_yticks(range(len(terms)),terms);ax.set_ylim(-.65,len(terms)-.35)
    ax.set_xlabel(cfg['unit']);ax.grid(axis='x',color=GRID,lw=.6)
    if cfg['scale']=='ratio': ax.set_xscale('log')
    if len(models)>1:
        # Plot one legend entry per model even when model lacks first term.
        from matplotlib.lines import Line2D
        ax.legend([Line2D([],[],marker=['o','s','^','D'][j%4],color=pal[j%len(pal)],linestyle='') for j in range(n)],models,frameon=False)

def line_event(ax,rows,cfg):
    x=[r['event_time'] for r in rows];y=[r['estimate'] for r in rows]
    down=[r['estimate']-r['ci_low'] for r in rows];up=[r['ci_high']-r['estimate'] for r in rows]
    ax.errorbar(x,y,yerr=[down,up],fmt='o',color=BLUE,ecolor=BLUE,capsize=3,lw=1.35,ms=4.5)
    ax.axhline(0,color='#60666A',ls='--',lw=1)
    ax.axvline(cfg['intervention_event_time']-.5,color=ORANGE,ls=':',lw=1.2,label='Intervention boundary')
    # DO NOT draw an invented estimate or CI at omitted baseline.
    ax.set_xticks(sorted(set(x+[cfg['baseline_event_time'],cfg['intervention_event_time']])))
    ax.set_xlabel('Event time (omitted reference period: '+str(cfg['baseline_event_time'])+')')
    ax.set_ylabel(cfg['unit']);ax.grid(axis='y',color=GRID,lw=.6)
    ax.legend(frameon=False,loc='best')

def line_map(ax,rows,cfg,boundary_path):
    try: import geopandas as gpd
    except ImportError as exc: raise RuntimeError('policy-map requires geopandas; install it in your own environment') from exc
    gdf=gpd.read_file(boundary_path)
    if gdf.crs is None or gdf.crs.to_epsg()!=4326:
        raise ValueError('GeoJSON must have EPSG:4326 CRS; do not assume missing or different CRS')
    key=cfg['region_id_field']
    if key not in gdf.columns: raise ValueError('GeoJSON lacks region ID field')
    if not gdf.geometry.is_valid.all(): raise ValueError('Invalid geometry detected; repair and document externally')
    if gdf.geometry.is_empty.any(): raise ValueError('Empty geometry detected')
    values={r['region_id']:r['value'] for r in rows}
    gdf['_metric']=gdf[key].astype(str).map(values)
    valid=gdf[gdf['_metric'].notna()];na=gdf[gdf['_metric'].isna()]
    if not valid.empty:
        lo=float(valid['_metric'].min());hi=float(valid['_metric'].max())
        if lo==hi: hi=lo+1
        vmin=min(0,lo) if lo>=0 else lo
        valid.plot(ax=ax,column='_metric',cmap='Blues',vmin=vmin,vmax=hi,linewidth=.45,edgecolor='#58626B')
        norm=colors.Normalize(vmin=vmin,vmax=hi)
        cbar=ax.figure.colorbar(cm.ScalarMappable(norm=norm,cmap='Blues'),ax=ax,shrink=.77,pad=.015)
        cbar.set_label(cfg['unit'])
    if not na.empty:
        na.plot(ax=ax,facecolor='#E7E7E7',edgecolor='#69717B',hatch='///',linewidth=.45,
                label='Missing / not reported')
        ax.legend(handles=[Patch(facecolor='#E7E7E7',edgecolor='#69717B',hatch='///',label='Missing / not reported')],
                  frameon=False,loc='upper left',bbox_to_anchor=(0,1.11),fontsize=9)
    ax.set_axis_off(); ax.set_aspect('equal')
    # Boundary-source/CRS legitimacy cannot be independently confirmed by this renderer.

def render(kind,input_csv,config_path,out,boundaries=None):
    cfg=json.loads(Path(config_path).read_text(encoding='utf-8'))
    validate_config(kind,cfg)
    if kind=='policy-map' and not boundaries: raise ValueError('--boundaries required for policy-map')
    geo=json.loads(Path(boundaries).read_text(encoding='utf-8')) if boundaries else None
    rows=prepare(kind,load_csv(input_csv,kind),cfg,geo)
    if kind=='policy-map' and cfg['status']=='research' and 'synthetic' in cfg['boundary_source'].lower():
        raise ValueError('Cannot use synthetic boundaries for research status')
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    setup_font(cfg);fig,ax=plt.subplots(figsize=(7.4,4.5),layout='constrained')
    fig.suptitle(cfg['title'],fontsize=13,weight='semibold')
    {'trend':lambda:line_trend(ax,rows,cfg),'coefficients':lambda:line_coeff(ax,rows,cfg),
      'event-study':lambda:line_event(ax,rows,cfg),
      'policy-map':lambda:line_map(ax,rows,cfg,boundaries)}[kind]()
    marker(ax,cfg)
    stem=cfg['figure_id'];exports={ext:stem+'.'+ext for ext in ('png','svg','pdf')}
    for ext,name in exports.items(): fig.savefig(out/name,dpi=300)
    plt.close(fig)
    snapshot={'kind':kind,'rows':rows}
    snapshot_path=out/'figure-data.json'
    snapshot_path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    relative=lambda path:os.path.relpath(Path(path).resolve(),out)
    pipeline={'version':2,'kind':kind,'input_csv':relative(input_csv),'input_sha256':digest(input_csv),
        'config_json':relative(config_path),'config_sha256':digest(config_path),
        'figure_data':'figure-data.json','figure_data_sha256':digest(snapshot_path),
        'n_plotted':sum(1 for r in rows if r.get('value',r.get('estimate')) is not None)}
    if boundaries: pipeline.update(boundaries_geojson=relative(boundaries),boundaries_sha256=digest(boundaries))
    inferred=kind in ('coefficients','event-study')
    m={'figure_id':stem,'title':cfg['title'],'status':cfg['status'],'question':cfg['question'],'design':kind,
       'data':{'source':cfg['source'],'source_kind':'synthetic_demo' if cfg['status']=='demo' else 'observed',
       'unit_of_analysis':cfg['unit_of_analysis'],'population':cfg['population'],'time_window':cfg['time_window'],
       'n_observations':cfg.get('n_observations'),'missingness':cfg['missingness'],'weights':cfg['weights'],
       'transformations':cfg['transformations']},
       'inference':{'estimand':cfg.get('estimand','descriptive measurement only'),
       'method':cfg.get('method','none; descriptive graph'),
       'uncertainty':cfg.get('interval_label','not applicable; no intervals'),
       'standard_errors':cfg.get('se_method','not applicable; no estimated standard errors'),
       'reference_group':cfg.get('reference_group','not applicable')},
       'chart':{'x_label':cfg['unit'] if kind=='coefficients' else 'year / event time / geography',
       'y_label':cfg['unit'],'denominator':cfg.get('denominator','not applicable'),
       'caption':cfg['caption'],'alt_text':cfg['alt_text']},
       'provenance':{'code':relative(Path(__file__)), 'input_files':[relative(input_csv)] + ([relative(boundaries)] if boundaries else []),
       'data_restrictions':cfg['data_restrictions']},'exports':exports,
       'review':{'numeric_verified':False,'visual_verified':False,'method_verified':False,'reviewer':'',
           'notes':'Generated and source-to-sidecar cross-check is available; independent model and visual review still required.'},
       'pipeline':pipeline}
    (out/'figure-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('kind',choices=KINDS);ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--boundaries',type=Path)
    args=ap.parse_args()
    try: out=render(args.kind,args.input,args.config,args.out,args.boundaries)
    except (OSError,ValueError,RuntimeError,KeyError) as ex:
        ap.exit(2,f'ERROR: {ex}\n')
    print('Rendered',out,'(source values unchanged; independent visual/method review pending)')
if __name__=='__main__':main()
