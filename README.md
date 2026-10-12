# Social Science Visualization

**Research-first, reproducible figure production for the social sciences.**  
**面向社会科学的学术可视化 Agent Skill：从研究问题、数据口径与推断边界出发，而不止于绘图。**

[![Status](https://img.shields.io/badge/status-research_preview-596579)](#项目状态与验证) [![Skill](https://img.shields.io/badge/Skill-v2.0.0-596579)](SKILL.md) [![DSH](https://img.shields.io/badge/DSH_adapter-v0.1.0-596579)](adapters/deepseek-harness/README.md) [![License](https://img.shields.io/badge/license-MIT-596579)](LICENSE)

---

## 为什么需要它？ / Why it exists

社会科学研究中，技术上能够绘制的图，未必就是可以成立的研究证据。偏差往往发生在绘图之前：把不同分母的指标放在一起比较、悄悄改变样本范围、把描述性趋势解释成政策效果、将事件研究中被省略的基准期画成真实估计值，或者用不匹配的行政区划边界绘制空间分布。

**Social Science Visualization（SSV）** 将政治学、公共管理、公共政策及相邻领域的研究规范组织为 Agent 可遵循的工作流：先理解研究问题，再检查观察单位、统计口径、估计目标及推断边界，随后选择图形、完成可复现绘制、审查数值与视觉表达，并保留来源记录。

> Research question → data/estimand checks → figure selection → reproducible rendering → numerical & visual review → documented delivery.
>
> 研究问题 → 数据和估计目标审查 → 选择图形 → 可复现绘制 → 数值与视觉复核 → 可追溯交付。

它**不是**独立的统计软件，不替代 R、Stata、Python，也不把统计检验结果自动解释为因果结论。可以独立使用，也可以与其他专业统计分析和科学绘图 Skills 配合。中文学术表达为默认，同时支持英文图表与跨语言输出。

## 两种使用方式 / Two distribution paths

| 路径 | 入口 | 适用情境 |
| --- | --- | --- |
| **标准 Agent Skill** | 仓库根目录 [`SKILL.md`](SKILL.md) | Codex、Claude Code 及兼容 Agent Skills 标准的客户端 |
| **DeepSeek Harness 插件** | [`adapters/deepseek-harness/`](adapters/deepseek-harness/) | 需要在 DSH Profile 内通过 Cordis 注册 Skill 的用户 |

两条路径共享根目录的研究规范与绘图源码。**DSH 包通过 `npm pack` 前的 staging 步骤自动生成内嵌的 `skill/` 资源目录**；无需在 Git 中手动维护第二份源码。请选择一种 DSH 安装路径，避免 Skill 重名和加载优先级冲突。

## 主要能力 / Capabilities

| 模块 | 已实现 | 重要边界 |
| --- | --- | --- |
| 研究方法编排 | 从研究问题审查观察单位、分母、样本、比较对象、估计目标和来源 | 不代替研究者的实质判断 |
| 长期/分组趋势 | `trend`：缺失期断线、多组对比、单位一致性 | 不自动将相关性解释为因果 |
| 回归系数图 | `coefficients`：已有估计值、区间、零效应参照线、模型比较 | 不重新拟合模型 |
| DID / 事件研究 | `event-study`：事件时间、已省略基期、现有动态系数与区间 | 事前系数不显著不等于证明平行趋势 |
| 区域政策分布 | `policy-map`：使用用户提供的 GeoJSON 及地区编码 | 不编造地图边界；缺失值不等于零 |
| 数值及交付审查 | 来源/配置哈希、绘图快照、部分结构及文件检查 | 不等于模型独立复算或图形像素审查 |
| 软件衔接 | Python statsmodels 适配与 R / Stata 规范化导出示例 | 不直接解析任意 `.ster` / `.rds` 文件 |

详见 [`references/`](references/) 的研究诚信、图形选择、因果推断、空间网络、排版导出及输入数据契约。当前只有上述四种**可执行图表模板**；RD、异质性和网络分析目前以规范性指导为主。

## 安装 / Installation

### A. 标准 Agent Skill

在支持开放 Agent Skills 的 CLI 中安装根目录（具体 Agent 选项以本机 CLI 为准）：

```bash
npx skills add https://github.com/hengdaoye50/social-science-visualization
```

也可以克隆后安装本地目录：

```bash
git clone https://github.com/hengdaoye50/social-science-visualization.git
npx skills add ./social-science-visualization
```

> 安装 Skill 只会安装说明和随附资源，不等于 Python 库或系统字体已安装。执行 Python 绘图需本机环境及适当权限。

### B. DeepSeek Harness / DSH 插件

该适配器使用 DSH 的 `ctx.skills.register()` 注册运行时 Skill，提供目录型 `resourceBase` 以读取代码及参考文档；它**不注册新的 Shell 工具，不会在插件加载时执行 Python，也不会绕过 Harness 的审批和沙箱机制**。DSH 官方支持 [Skills registry](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md) 和 [bundle packaging](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish)。

在仓库根目录：

```bash
cd adapters/deepseek-harness
npm test          # 阶段化生成 skill/ 并测试注册契约
npm pack          # 自动将根目录的核心源码打包进独立的 DSH 插件
# 将实际生成的 .tgz 文件路径传给 dsh：
dsh plugin --profile research add ./dsh-social-science-visualization-0.1.0.tgz
dsh --profile research --dump-config
```

`research` 只是 Profile 示例名称；可以替换为自己的 Profile。也可以走项目级原生 DSH Skill 方式，将**整份仓库根目录资源**复制到项目 `.dsh/skills/social-science-visualization/`（不是只复制 `SKILL.md`）。两种方式择一。参见 [DSH 专项安装与兼容说明](adapters/deepseek-harness/README.md)。DSH 仍可能更新其插件接口；适配器已做本地注册契约测试，但尚未声称在你的 DSH 安装中通过端到端加载。

## Python 环境与快速体验 / Quick start

建议 Python 3.10+。四种模板需要 `matplotlib`，区域地图还需要 `geopandas` 和其地理空间依赖；使用隔离的虚拟环境并按实际需要安装依赖。

在仓库根目录执行：

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

上述 `examples/fixtures/` **全部是模拟数据**，其中地图只是人工构造的示例多边形，绝非真实行政区地图，不得引用为研究结论。每次正式绘图应保存 `figure-data.json` 和 `figure-manifest.json`，并按 [v2 数据契约](references/v2-data-contract.md) 接入真实数据。

## 推荐的研究使用方法 / Agent prompts

**长期财政面板数据：** “请使用 social-science-visualization，根据我的教育财政数据制作长期趋势图。先核对观察单位、现价与不变价、分母、口径变化与缺失年份；不要擅自推断因果关系。交付矢量图、绘图代码、图注和 manifest。”

**事件研究：** “读取已有回归结果生成事件研究图，说明估计器、置信区间及聚类标准误口径；省略基期只能标记，不得虚构其系数或区间；不要把事前系数不显著表述为平行趋势已经得到证明。”

**区域政策研究：** “用我提供且标明来源的行政区划边界绘制政策分布图，核对边界年份、地区代码与样本范围；缺失与零值必须区分。如果不能验证边界，就改为地区排序图。”

## 可复现与科研诚信 / Research integrity

- **描述 ≠ 因果。** 不制造原始数据、估计值、置信区间、标准误、政策效果或数据出处。
- 不混淆缺失、零值、不可比数据、不同分母或不同观察单位。
- 不以“一组显著、另一组不显著”替代组间差异的统计检验。
- 事件研究明确估计器、处理时间、基准期、置信区间含义及标准误类型。
- 地图必须使用可信边界及 CRS，避免行政区划跨期不匹配。
- 自动审查通过 **不等于** 模型正确、因果识别成立或最终图像满足期刊标准；正式发表前仍需真实渲染检查和研究者复核。

## 项目状态与验证 / Validation status

- **SSV Skill v2.0.0**：四类可执行图表、规范化数据接口和两类审查脚本；已有本地 Python 测试及模拟样例。
- **DSH Adapter v0.1.0**：Cordis bundle、打包时复制资源的流程、插件注册契约测试。没有在用户实际 DSH Profile 中完成端到端执行。
- **仍待验证**：真实社科研究数据、R/Stata 原生环境、跨平台字体、DSH 版本兼容与期刊排版适配。欢迎以可公开的数据和可复现失败案例提出问题。

结构：

```text
.
├── SKILL.md                          # 通用 Agent Skill 唯一权威源
├── references/                       # 社科研究方法、数据与排版规范
├── scripts/                          # 绘图、数值审查及数据接口
├── assets/                           # figure manifest 模板
├── examples/                         # 明确标注的模拟输入
├── tests/                            # Python 测试
└── adapters/deepseek-harness/         # DSH Cordis 插件源
    ├── package.json
    ├── cordis.patch.yml
    ├── index.js
    ├── scripts/stage.mjs              # 打包时从仓库根目录复制 Skill
    └── test.mjs
```

## 发展路线 / Roadmap

优先用真实研究检验 v2.0 的可靠性，修补数据口径、推断、软件互操作和视觉审查方面的缺陷，再决定是否扩展 RD、异质性、稳健性及网络图等模板。遵循单一源码、真实测试、必要时明确拒绝不成立的制图请求的原则。

**License:** [MIT](LICENSE)。这是独立社区项目，与 DeepSeek AI、K-Dense、Anthropic 或 OpenAI 均无官方隶属关系；所有外部项目及依赖仍遵循其自身许可证。
