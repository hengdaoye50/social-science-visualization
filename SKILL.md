---
name: social-science-visualization
description: Design, produce, audit, and deliver reproducible social-science research figures for political science, public administration, public policy, sociology, and economics. Use for descriptive statistics, panel and comparative charts, regression coefficients, uncertainty, DID/event-study/RD diagnostics, heterogeneity, robustness, regional maps, diffusion, and policy or organizational networks; also use when converting empirical results into journal figures, academic presentations, or research communication. Protect observational units, samples, inferential meaning, and provenance before styling.
license: MIT
compatibility: >-
  Works offline with file-reading and Python execution; Matplotlib is needed for executable examples; GeoPandas for real-region maps. Supports Chinese and English outputs.
  Optional companion skills: scientific-visualization, matplotlib, statistical-analysis.
metadata:
  version: "2.0.0"
  language: zh-CN
---

# Social Science Visualization / 社会科学学术可视化

## 定位

把研究问题、数据结构与识别策略翻译成**诚实、可复现、适合发表的图表**。首先保证推断意义，其次保证可读性，最后才是美观。你是研究者的制图合作者，而非独立决定结论的作者。兼容政治学、公共管理、公共政策及相邻领域；中文论文为默认，按用户要求切换英文和具体期刊样式。

本 Skill 是领域编排层，不复制通用绘图库手册。若已安装 `scientific-visualization`、`matplotlib`、`statistical-analysis`，按任务调用其通用能力；没有这些 Skill 时，仍可独立按本文和参考文件工作。不要把 Skill 存在等同于 Python 依赖已安装。

## 激活范围

- 用户要求研究数据的图形探索、统计结果呈现、论文插图、研究型 PPT 图表或公众号科研图解。
- 需要从模型结果（表格或保存的估计对象）制作系数图、区间图、事件研究图、异质性/稳健性图。
- 需要绘制政策时空分布、区域对比或组织/政策网络。
- 用户只要求装饰性插画或没有实证数据的概念机制图时，不把它伪装成数据图；可以协助规划示意图，但明确其非实证性质。

## 不可妥协的六条原则

1. **研究问题先行**：明确图要回答的命题与读者需要比较的量；不存在通用的“最好看图形”。
2. **单位与分母可追溯**：审视观察单位、分析层次、时间窗口、样本筛选、加权方式、缺失值、聚合与标准化。计数、率、占比、均值不可混用。
3. **描述与推断分开**：相关不等于因果；没有可靠识别设计时不擅自采用处理效应语言。不得替用户虚构估计结果、显著性、置信区间、地图边界或资料来源。
4. **不确定性如实呈现**：置信区间、可信区间、标准误、预测区间和离散程度不能混称；保留零效应线、基准组、聚类层级与必要的样本信息。
5. **视觉不篡改证据**：不通过截断坐标轴、双轴暗示、选择性标签、不等比例符号、误导性着色、删去不利组别制造“发现”。
6. **交付可复现**：源数据与变换记录、绘图代码、图注/替代文本、导出文件及审查状态应可追查；没有核验过的事项必须标注未核验。

## 工作流（按实际任务裁剪，不机械扩展分析）

1. **界定用途**：确定期刊 / 论文 / 答辩 PPT / 研究传播；图意、语言、目标尺寸和必要交付格式。已有明确条件不要重复询问。若资料不足，先完成可支持的部分，并标明缺口。
2. **数据体检**：读取数据字典与原始输出，确认单位、N、时间、地区编码、缺失、重复、筛选、权重和分母；核对聚合后是否出现生态谬误或辛普森悖论风险。参阅 [research-integrity](references/research-integrity.md)。未经允许不覆写输入。
3. **匹配图形**：优先选择可直接比较位置、长度和区间的编码，避免只为“丰富”而制造多种图型。参阅 [figure-selection](references/figure-selection.md)。
4. **确定统计口径**：核对估计量、模型、误差计算、样本和参考组。DID / 事件研究 / RD / 多模型的专门防误导规则见 [causal-inference](references/causal-inference.md)。区域地图与网络见 [spatial-network](references/spatial-network.md)。若用户只需可视化既有结果，不擅自重新估计模型；需要重算时说明并保留原值供比对。
5. **绘图与迭代**：先形成信息清楚的第一版，再检查图例、单位、文字碰撞、置信区间、图注、色盲与黑白阅读。主次分明、少装饰；不得为了视觉而修改统计对象。
6. **出图与实测检查**：按交付目标生成可用的 PDF/SVG（视期刊兼容性而定）与 PNG，检查字形、裁切、坐标、分辨率。参考 [visual-and-export](references/visual-and-export.md) 与 [release-checklist](references/release-checklist.md)。如果环境无法渲染，说明无法完成的检查，不能宣称通过。
7. **交付**：图表文件、代码、必要数据或合法数据取得说明、`figure-manifest.json`（模板见 `assets/figure-manifest.template.json`）、一两句解释及重要边界。可运行 `python scripts/audit_release.py <manifest.json>` 做**结构性**检查；它不能替代人工核验统计含义和最终视觉。

## v2 可执行模板：已有结果优先（不可擅自重估）

当用户要求实际交付图表，先按研究任务检查原始字段与指标口径。仅在数据与方法足够明确且确实有授权的情况下调用以下工具；**默认不重算模型、不假设标准误、不制造区间、未经核实不填写图注**。列合同和配置详见 [v2-data-contract](references/v2-data-contract.md)。

- `python scripts/render_figure.py trend --input panel.csv --config config.json --out out/`：分组/长期趋势。跨年值缺失画断线。
- `python scripts/render_figure.py coefficients --input coefficients.csv --config config.json --out out/`：既有模型系数与原有 CI。比值尺度必须使用正确的 1 参考线与正数对数轴。
- `python scripts/render_figure.py event-study --input dynamics.csv --config config.json --out out/`：既有事件研究估计。省略基期只在轴/注记中出现，不能伪造估计点。
- `python scripts/render_figure.py policy-map --input region.csv --config config.json --boundaries approved.geojson --out out/`：来自用户提供且可追溯边界的区域分布。缺失与零分开；无合法边界时改用地区排序图而不是编造地图。
- 输入适配器：`scripts/adapters/python_statsmodels.py`、`r_export.R`、`stata_export.do`；它们要求已有估计结果。未经用户同意不将敏感数据复制到公开包中。
- 每次生成后运行 `python scripts/audit_numeric.py out/figure-manifest.json`（CSV/配置哈希与绘图快照一致性）和 `python scripts/audit_release.py out/figure-manifest.json`（文件结构）；两者**均不能证明模型或像素正确**。仍须按 `release-checklist` 独立审图、复核模型。

## 分情境加载（需要时读，不一次性读完）

| 场景 | 参考文件 |
|---|---|
| 数据/指标/单位与整体诚实性 | `references/research-integrity.md` |
| 描述统计、比较、面板和图型选择 | `references/figure-selection.md` |
| 回归、DID、事件研究、RD、稳健性 | `references/causal-inference.md` |
| 地图、区域政策与网络分析 | `references/spatial-network.md` |
| 中文字体、布局、格式、导出 | `references/visual-and-export.md` |
| 发布前复核 | `references/release-checklist.md` |
| v2 输入格式、R / Stata / Python 输出适配 | `references/v2-data-contract.md` |

## 默认交付约定

- 一图一问题，标题描述比较对象，图注写明来源、时间、单位、N（相关时）、关键模型/不确定性与读图边界。显著性星号不得代替效应量和区间。
- 同系列图保持颜色、单位、基线、分组顺序一致；区分“无数据”和数值零。
- 默认论文风格：白底、深灰字、少量低对比网格、强调色克制、直接标注优先；中文字体必须在目标设备可用并检查导出，绝不把缺字的图视为完成。
- 对有保密限制的数据优先本地执行；不得擅自上传外部服务，也不把敏感原始数据嵌进公开 SVG、HTML 或交付示例。
- 明确输出状态：`已完成并检查` / `已导出但未视觉核验` / `仅代码，未执行`；不得混用。
- **禁止**把 bundled demo 数据或图误写为真实研究发现；示例均应保留“模拟数据/非真实实证结果”标识。

## 可运行起点

- `python examples/minimal_workflow.py`：用明确标注的模拟系数构造中英兼容示范图、三格式文件与 manifest；使用 Matplotlib（仅为示范，并非真实实证分析）。
- `python scripts/audit_release.py examples/demo_output/figure-manifest.json`：审查元数据与文件的基本完整性；可选 `--strict` 将警告也视为未通过。
- `python -m unittest discover -s tests -v`：执行 v1 结构与 v2 数据/渲染/篡改测试（渲染部分需要 Matplotlib、GeoPandas）。

遇到现成期刊模板或用户指定设计时，遵守明确要求；其他情况下不得凭空宣称某期刊当前规定。详细资料见 README.md。
