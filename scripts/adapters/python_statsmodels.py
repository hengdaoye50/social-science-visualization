"""Adapt an ALREADY FITTED statsmodels result to normalized coefficient CSV.

Import and call export_fitted_model(result, output_path, model_name='Model 1').
No refitting. Uses the fitted object's own conf_int() method, so CI provenance
must be described accurately by the researcher (robust/clustered, alpha, etc.).
Do not pass a different result object merely to obtain preferred standard errors.
"""
from __future__ import annotations
import csv
from pathlib import Path

def export_fitted_model(fitted, output_path, model_name='Model 1', alpha=.05):
    if not 0<alpha<1:raise ValueError('alpha must be between 0 and 1')
    params=fitted.params
    bounds=fitted.conf_int(alpha=alpha)
    if not hasattr(params,'index'):raise TypeError('Require labelled parameters (e.g. model fit on a pandas DataFrame)')
    output_path=Path(output_path);output_path.parent.mkdir(parents=True,exist_ok=True)
    with output_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['term','model','estimate','ci_low','ci_high'])
        for label in params.index:
            if hasattr(bounds,'loc'):
                ci=bounds.loc[label].tolist()
            else:
                ci=bounds[list(params.index).index(label)]
            w.writerow([str(label),model_name,float(params.loc[label]),float(ci[0]),float(ci[1])])
    return output_path
