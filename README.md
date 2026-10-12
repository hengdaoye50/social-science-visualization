# Social Science Visualization

**A research-first Agent Skill for reproducible visualization in the social sciences.**  
**社会科学学术可视化：从研究问题、数据口径与推断边界出发，而不止于生成一张漂亮的图。**

Version **2.0.0** · Chinese-first / English-capable · Offline-friendly · MIT

---

## Why this project exists｜为什么开发它？

In empirical social science, a technically valid chart is not necessarily a valid piece of research evidence. The most consequential mistakes often happen *before* rendering: comparing incompatible denominators, silently changing samples, treating a descriptive trend as a causal effect, plotting an omitted event-study reference period as an estimated coefficient, or using mismatched administrative boundaries.

本项目将政治学、公共管理、公共政策及相邻社会科学领域的研究方法要求组织为一套可由 Agent 遵循的 **Skill**。它不是替代 R、Stata、Python 的新统计软件，也不是通用绘图库的再包装；它承担研究问题与制图工具之间的编排工作，帮助研究者审视证据、选图、忠实呈现结果、记录来源，并交付可复现的学术图表。

> **Research question → data and estimand checks → appropriate figure → reproducible rendering → numerical and visual review → publication-ready handoff.**  
> 研究问题 → 数据与估计目标审查 → 选择图形 → 可复现绘图 → 数值及视觉核验 → 正式交付。

**Status:** v2.0 is a working early-stage release, **not** an independently certified research, statistical, or journal-compliance system. Demo values and demo map geometries are synthetic.

## Who it is for｜适用对象

Researchers and research assistants working in political science, public administration, public policy, sociology, economics, education finance, comparative politics, regional governance and related fields; particularly projects requiring Chinese-language academic figures alongside English-language outputs.

Use it for descriptive charts, long-run/panel comparisons, regression coefficient plots, existing DID/event-study estimates, regional policy maps, methodological figure review, journal manuscripts, research presentations and rigorous research communication. It can advise on RD, heterogeneity, robustness and networks, but **v2.0 does not provide executable templates for every one of those methods**.

## What is included｜当前能力

| Component | What it does | Important boundary |
| --- | --- | --- |
| `SKILL.md` | Research-first agent workflow and contextual loading of references | Does not independently decide substantive conclusions |
| `references/` | Integrity, figure selection, causal inference, spatial/network, typography/export, release review and v2 input contract | Guidance is not a substitute for domain expertise |
| `scripts/render_figure.py` | Four executable templates: `trend`, `coefficients`, `event-study`, `policy-map` | Plots supplied values; **does not re-estimate models** |
| `scripts/ssv_data.py` | Normalize/validate input CSV and plotting data | A blank numeric value is not zero |
| `scripts/audit_numeric.py` | Compare source/config hashes and normalized figure-data snapshots; inspect selected integrity constraints | Does not independently reproduce model estimates or inspect image pixels |
| `scripts/audit_release.py` | Check manifest and basic exported-file integrity | Not a certificate of publication readiness |
| `scripts/adapters/` | Examples for existing Python statsmodels results and standardized R/Stata exports | No generic native `.ster` / `.rds` parser |
| `examples/fixtures/`, `tests/` | Explicitly synthetic inputs and tests, including negative cases | Never cite demo data as empirical findings |

The design favors **composability**: use it on its own or alongside K-Dense's `scientific-visualization`, `matplotlib`, and `statistical-analysis` Skills. Those projects are optional external companions, not bundled dependencies or affiliated projects.

## Installation｜安装

Install the root of this repository as an Agent Skill. Check the supported agent identifiers in your installed Skills CLI:

```bash
npx skills add https://github.com/hengdaoye50/social-science-visualization
```

Alternatively, clone the repository and install the local directory:

```bash
git clone https://github.com/hengdaoye50/social-science-visualization.git
npx skills add ./social-science-visualization
```

The CLI installs the **Skill instructions**; it does **not** automatically install Python libraries. Review third-party code before allowing an Agent to run scripts in a research environment. Restart/refresh your Agent session if necessary. Private repositories require the relevant access credentials.

### Runtime dependencies

- Python **3.10+** for scripts and tests.
- `matplotlib` for executable visualization.
- `geopandas` and its supported geospatial stack for `policy-map`.
- Core audit scripts and unit tests use the Python standard library; R/Stata adapters require their respective software to run.

Use your own virtual environment and preferred package manager. Do not upload confidential research data to a public repository.

## Quick start｜快速开始

Run from the repository root. **All supplied fixtures are synthetic**; the map uses deliberately artificial square polygons, not actual administrative geography.

```bash
python -m unittest discover -s tests -v

python scripts/render_figure.py trend \
  --input examples/fixtures/trend.csv \
  --config examples/fixtures/trend.json \
  --out examples/v2_output/trend

python scripts/render_figure.py coefficients \
  --input examples/fixtures/coefficients.csv \
  --config examples/fixtures/coefficients.json \
  --out examples/v2_output/coefficients

python scripts/render_figure.py event-study \
  --input examples/fixtures/event-study.csv \
  --config examples/fixtures/event-study.json \
  --out examples/v2_output/event-study

python scripts/render_figure.py policy-map \
  --input examples/fixtures/policy-map.csv \
  --config examples/fixtures/policy-map.json \
  --boundaries examples/fixtures/synthetic-not-geography.geojson \
  --out examples/v2_output/policy-map

python scripts/audit_numeric.py examples/v2_output/event-study/figure-manifest.json
python scripts/audit_release.py examples/v2_output/event-study/figure-manifest.json
```

Every supported renderer exports PNG, SVG and PDF together with a `figure-data.json` snapshot and `figure-manifest.json` for provenance. Consult [the v2 data contract](references/v2-data-contract.md) before supplying real data.

### Suggested Agent prompts

**Long-run research:** “使用 social-science-visualization，根据我的教育财政面板数据绘制长期趋势。先核对观察单位、缺失年份、财政口径与不变价处理；不要擅自进行因果解释；交付矢量图、代码、图注和 manifest。”

**Event study:** “把我已经估计完成的动态效应系数绘制为事件研究图。明确估计器、标准误与置信区间类型；把 -1 期标记为省略基期，不要把不显著的事前系数称为平行趋势证明，也不要替我重新估计模型。”

**Regional policy study:** “根据我提供、可追溯来源的行政区划边界绘制政策分布图；核对行政编码与边界年份，严格区分缺失地区与零值。无有效边界时改为区域排序图，不得编造地图。”

## Reproducibility and review｜科研诚信与核验边界

The default pipeline preserves the input; checks observational units, denominators, sample selection, reference periods and interval meanings; keeps source/configuration hashes and a normalized plotting snapshot; and distinguishes unverified steps from completed checks. Chart titles, labels, notes, vector exports and readable Chinese text require **actual visual inspection** before publication.

In particular:

- **Descriptive ≠ causal.** Do not invent estimates, uncertainty, provenance or identification strategies.
- **Non-significant pre-trends ≠ proof of parallel trends.**
- **Significant in group A and non-significant in group B ≠ statistically significant between-group difference.**
- Distinguish zero, missing, suppressed and inapplicable values. Do not silently turn blank entries into zeros.
- Respect treatment timing, omitted baseline, actual observation grain, CI type and clustered standard errors.
- Geographic maps require real, provenance-traceable geometry and matching CRS/administrative codes.
- A passing script audit is **not** a validation of the statistical model or the final figure's pixels.

The initial package's automated tests covered normal and deliberately invalid inputs. R/Stata adapters and real-world research pipelines still require testing in their native environments. See [release checklist](references/release-checklist.md) and [changelog](CHANGELOG.md).

## Repository layout｜目录结构

```text
.
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── LICENSE
├── assets/
│   └── figure-manifest.template.json
├── references/
│   ├── research-integrity.md
│   ├── figure-selection.md
│   ├── causal-inference.md
│   ├── spatial-network.md
│   ├── visual-and-export.md
│   ├── release-checklist.md
│   └── v2-data-contract.md
├── scripts/
│   ├── render_figure.py
│   ├── ssv_data.py
│   ├── audit_numeric.py
│   ├── audit_release.py
│   └── adapters/
├── examples/
│   ├── fixtures/
│   └── minimal_workflow.py
└── tests/
```

Generated demo images and results are intentionally treated as artifacts, not as authoritative evidence. Regenerate them from fixtures and code when needed.

## Roadmap｜迭代方向

1. Validate the entire workflow with actual long-run/panel social science data and document failures.
2. Test R and Stata adapters in their native environments; add fixtures for edge cases.
3. Improve consistency checks across numerical data, manifest and rendered figures.
4. Add executable RD, heterogeneous-effect and robustness templates **only after** evidence of need.
5. Keep a single research figure reproducible across journal, PPT and research communication formats without changing its statistical meaning.

This is a practical, research-led project. Contributions should include source information, methodological rationale, runnable examples and negative tests where appropriate. Please do not submit confidential datasets, copyrighted administrative boundaries without permission or fabricated study results.

## License and attribution

Original files in this repository are released under the [MIT License](LICENSE). Optional companion projects and Python/R dependencies retain their own licenses. This repository is independent and is not an official K-Dense, Anthropic or OpenAI project.
