#!/usr/bin/env python3
"""Simulated, educational forest-plot example. Not empirical evidence."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
OUT = HERE / "demo_output"
OUT.mkdir(exist_ok=True)

# Use an installed CJK font; fail visibly if none is present rather than producing missing glyphs.
choices = ("Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "PingFang SC", "SimHei", "AR PL SungtiL GB")
# Matplotlib font cache can omit system-installed fonts. Register a simplified-Chinese
# backup by its local file path if discovered (never package or redistribute fonts).
for system_font in font_manager.findSystemFonts():
    if Path(system_font).name == "gbsn00lp.ttf":
        font_manager.fontManager.addfont(system_font)
        break
font = None
for candidate in choices:
    try:
        font_manager.findfont(candidate, fallback_to_default=False)
        font = candidate
        break
    except ValueError:
        pass
if font is None:
    print("WARNING: No recognized CJK font found. Plot uses English-only labels.")
    labels = ["Model A", "Model B", "Model C"]
    watermark = "SIMULATED DEMO DATA / NOT RESEARCH FINDINGS"
else:
    labels = ["模型 A", "模型 B", "模型 C"]
    watermark = "模拟数据 / 非真实实证结果"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [font, "DejaVu Sans"] if font else ["DejaVu Sans"],
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "axes.unicode_minus": False if font == "AR PL SungtiL GB" else True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.facecolor": "white",
})

# Fixed, HAND-AUTHORED mock quantities solely to illustrate uncertainty display.
# They are NOT estimated from any real dataset or model.
mean = [0.21, -0.12, 0.05]
mock_se = [0.07, 0.09, 0.065]
ci_lo = [b - 1.96 * s for b, s in zip(mean, mock_se)]
ci_hi = [b + 1.96 * s for b, s in zip(mean, mock_se)]
y = [2, 1, 0]
fig, ax = plt.subplots(figsize=(6.8, 4.0), layout="constrained")
for i, yi in enumerate(y):
    ax.errorbar(mean[i], yi, xerr=[[mean[i] - ci_lo[i]], [ci_hi[i] - mean[i]]],
                fmt="o", color="#245478", ecolor="#245478", markersize=6,
                elinewidth=1.7, capsize=3)
ax.axvline(0, color="#5e5e5e", lw=1, linestyle="--")
ax.set_yticks(y, labels)
ax.set_xlim(-0.35, 0.43)
ax.set_ylim(-0.55, 2.65)
ax.set_xlabel("Illustrative effect estimate (arbitrary units)")
ax.set_title("模拟系数图 / Synthetic fixture" if font else "Illustrative coefficient plot / Synthetic fixture", loc="left", fontsize=12)
ax.grid(axis="x", linewidth=.5, alpha=.28)
ax.set_axisbelow(True)
ax.text(.02, .02, watermark, transform=ax.transAxes, va="bottom",
        fontsize=9, color="#9b3030", weight="bold")

stem = "fig-01_demo-forest"
for ext in ("png", "svg", "pdf"):
    fig.savefig(OUT / f"{stem}.{ext}", dpi=300)
plt.close(fig)

manifest = {
    "figure_id": "fig-01", "title": "Illustrative coefficient plot (synthetic demo)",
    "status": "demo", "question": "How to show point estimates and uncertainty without implying empirical evidence?",
    "design": "regression-display-demo",
    "data": {
        "source": "Hand-authored synthetic fixture embedded in examples/minimal_workflow.py",
        "source_kind": "synthetic_demo", "unit_of_analysis": "synthetic coefficient (three items)",
        "population": "not applicable: simulation fixture", "time_window": "not applicable",
        "n_observations": 3, "missingness": "none in fixture", "weights": "none",
        "transformations": "Illustrative bounds calculated as coefficient ± 1.96 * hand-authored mock SE",
    },
    "inference": {
        "estimand": "illustrative coefficients only (not fitted)",
        "method": "none; synthetic manually specified estimates",
        "uncertainty": "illustrative ±1.96 × synthetic SE, NOT a valid inferential CI",
        "standard_errors": "manually authored simulation values; no statistical estimation",
        "reference_group": "zero as conceptual no-effect line",
    },
    "chart": {
        "x_label": "Illustrative estimate (arbitrary units)", "y_label": "synthetic models",
        "denominator": "not applicable",
        "caption": "Synthetic demo only. Points are hand-authored mock coefficients, bars illustrative ±1.96×mock SE; no empirical data or inference.",
        "alt_text": "Three mock coefficient estimates with illustrative horizontal intervals and dashed vertical zero line; visibly labeled simulated data.",
    },
    "provenance": {
        "code": "../minimal_workflow.py", "input_files": [],
        "data_restrictions": "public synthetic fixture, not empirical evidence",
    },
    "exports": {ext: f"{stem}.{ext}" for ext in ("png", "svg", "pdf")},
    "review": {
        "numeric_verified": True, "visual_verified": False, "method_verified": True,
        "reviewer": "fixture author", "notes": "Synthetic arithmetic checked; visual review must be done by recipient in target viewer",
    },
}
(OUT / "figure-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote 3 simulated figure formats and manifest to {OUT}")
