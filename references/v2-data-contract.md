# v2 标准输入、估计结果适配与核验边界

`render_figure.py` **只画已有结果，不拟合或重新估计模型**。CSV UTF-8，可带 BOM；数字为有限值；空白 numeric 单元格只在趋势和地图被解释为缺失。不可填造 CI。CSV 列名必须与下表完全匹配（可有其他未使用列）。数据列留空必须依照该图型约束。

| 类型 | 必选列 | 特别约束 |
|---|---|---|
| `trend` | `year,series,value` | year 整数；每组-年唯一；允许 value 为空，展示为断线 |
| `coefficients` | `term,model,estimate,ci_low,ci_high` | 模型-变量唯一；low ≤ estimate ≤ high；scale `difference`(零线 0) 或 `ratio`(零线 1、正数区间) |
| `event-study` | `event_time,estimate,ci_low,ci_high` | event_time 整数唯一；严禁输入被省略的 baseline 作为估计值；CI 是用户已有估计器的输出 |
| `policy-map` | `region_id,value` | 覆盖所有 GeoJSON 区域；缺失值写显式空单元格；GeoJSON 必须有唯一 region ID 和合法来源 |

`--config` JSON 的基础字段：`figure_id,title,status(demo/research),question,source,unit_of_analysis,population,time_window,unit,caption,alt_text,missingness,weights,transformations,data_restrictions`。推断图另需 `estimand,method,interval_label,se_method,reference_group`；事件研究另需 `baseline_event_time` 和 `intervention_event_time`；系数图另需 `scale` 和 `null_value`；地图另需 `boundary_source,boundary_year,data_year,region_id_field,crs=EPSG:4326`。可选 `n_observations`（样本 N 不等于制图 CSV 行数），`denominator`。不要填写并未核实的样本或模型信息。

命令：

```bash
python scripts/render_figure.py coefficients --input path/to/coefficients.csv --config path/to/config.json --out path/to/output
python scripts/render_figure.py policy-map --input path/to/region.csv --config path/to/config.json --boundaries path/to/authoritative.geojson --out path/to/output
python scripts/audit_numeric.py path/to/output/figure-manifest.json
python scripts/audit_release.py path/to/output/figure-manifest.json
```

## 软件接口范围与原始统计口径

- Python statsmodels：`scripts/adapters/python_statsmodels.py` 的 `export_fitted_model(fitted, csv_path)` 从拟合对象**原样获取** `params` 与 `conf_int()`。适用于带标签的参数。调用者必须明确其拟合结果是否为聚类稳健、小样本或其他区间定义；不自动猜测。
- R：在用户自己的 R 环境中 source `scripts/adapters/r_export.R`；接受已有的整洁数据框。可使用已生成的 `broom::tidy()` 结果，但列名与 CI 计算方法须先人工核对。本包不直接解析任意 `.rds` 或 `fixest` 私有对象。
- Stata：参考 `scripts/adapters/stata_export.do` 中的列名和 `export delimited` 规则，适用于估计结果已存成 Stata 数据集的情况。本包**不直接解析 `.ster`**；不要强行从 p 星号推导 CI。
- `.dta`（标准列结构）可先用 `pandas.read_stata(...).to_csv(...,index=False)` 作格式转换；该步骤不能替换模型结果口径审查。

## 输出与检查

输出 `fig-id.{png,svg,pdf}`、`figure-data.json`、`figure-manifest.json`；`figure-data.json` 是真实被传入绘图函数的归一化数据快照。manifest 的 `pipeline` 记录 CSV/配置/地图文件 SHA-256、快照 SHA-256、有效绘图值计数。`audit_numeric.py` 复读输入并重建快照，检查变更、重复键、数值区间与区域覆盖。**其独立性只限于输入—绘图数据一致性，不代表对估计器本身、像素输出、行政区划权威或因果识别的独立审查**。

如果原始数据敏感，输出侧车 JSON 也可能敏感；不自动上传/发布；不要在公开仓库提交敏感文件与图表元数据。GeoJSON 需要由用户提供，不能凭地图绘图库自动生成边界。模拟地图只能用于代码测试，图上必须明示非真实地理。
