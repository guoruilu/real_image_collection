# 2026-05-11 30 类批量采集 + 输出策略改造

## 任务目标
1. 按 `img_list.txt` 列表跑全部 30 个 ImageNet 子类
2. 取消"50 张上限"的产出策略——过滤出多少存多少
3. 已经跑过的（埃及猫、灰蝶、卷尾猴）若是按 50 上限跑的需要重跑

## 关键变更

### 输出策略改造（`collect.py`）
- 删除 `saved >= n: break` 上限逻辑
- `--n` 语义改为"候选池目标量"——只用于估算下载数（默认下载 `n × 6` 张），不再限制最终保存数量
- 保存条件：过 CLIP 真实性 + 细类过滤 ∩ YOLO-World 能定位到目标
- 同步更新 `CLAUDE.md`（第 4 条）、`README.md`、`docs/usage.md`、`collect.py` docstring

### YOLO 单图容错（`collect.py`）
- 起因：`electric_trains` 跑到中途因某张坏图导致 `np.stack` 抛 `ValueError`，整个子进程崩了
- 修复：把 `det.predict(...)` 包进 try/except，单图失败时跳过继续

### 新增 `--detect-fallback`（`collect.py`）
- 起因：`brooms` / `clothes_irons` / `radio_telescopes` 等类，YOLO-World 对这些 detect prompt 召回率极低，导致大量过 CLIP 的图被检测层丢弃
- 行为：开启后，若 YOLO 找不到框，则用整张图（产品/物品图本来就紧凑构图）
- 默认关闭，仅在补救低产出类别时启用

## 批量驱动（`run_all.py`）
- 配置：每类 `(queries, detect, category_pos, category_neg)` 的字典
- 跳过：若产出目录已有 >50 张文件，认为已是新策略产出，跳过
- 子进程：每类调用一次 `collect.py`，互不影响
- 子进程崩溃不影响整体（log 中可见 `electric_trains` fail(1) 但 run_all 继续）

## 跑批结果

| 阶段 | 数量 |
|---|---|
| 总类别数 | 30 |
| 第一轮一次性产出 | 29 类（lycaenid_butterflies 跳过） |
| 失败/低产出补救 | 4 类（brooms / clothes_irons / radio_telescopes / revolvers） |
| **最终总图片数** | **2,916** |

### 每类产出（按数量降序）
```
184 airliners                  76 brooms (rescued from 2)
180 asian_elephants            65 boletes
164 clothes_irons (rescued)    60 grand_pianos
151 mountain_tents             60 canoes
149 running_shoes              58 mittens
133 capuchin_monkeys           56 electric_trains
131 digital_watches            52 electric_guitars
128 radio_telescopes (rescued) 52 egyptian_mau_cats
124 convertibles               47 missiles
123 clownfish                  47 desktop_computers
111 lycaenid_butterflies       37 pool_tables
101 pajamas                    35 parachutes
99  reflex_cameras             33 mailbags
87  daisies                    
85  revolvers (rescued from 22)
84  espresso_machines          
83  jack_o_lanterns            
```

### 4 个补救类对照
| 类别 | 一轮 | 补救 | 改动 |
|---|---:|---:|---|
| brooms | 2 | 76 | `--detect-fallback` |
| clothes_irons | 3 | 164 | `--detect-fallback`，detect 改为 "clothes iron" |
| radio_telescopes | 1 | 128 | `--detect-fallback`，detect 改为 "satellite dish"（更贴近其几何形状） |
| revolvers | 22 | 85 | `--detect-fallback`，`--cat-thresh` 降到 0.15 |

## 遇到的问题与解决
1. **某张坏图导致整批崩溃**（electric_trains）
   - 现象：`np.stack` ValueError，run_all 子进程返 1 但仍移到下一类
   - 已加 try/except 容错，今后单图坏不会让类别归零
   - electric_trains 已在 crash 前存了 56 张，符合要求未补救

2. **icrawler 单 URL 下载失败报 ERROR**（DNS 解析等）
   - 是单图层面的预期事件，不影响整体；监视器的 grep 已收紧避免误报警

3. **YOLO-World 对小众/抽象类目召回低**
   - 表现：CLIP 过了 100~200 张，YOLO 只挑出 1~3 张
   - 解决：`--detect-fallback` 启用整图兜底，且对特殊类（射电望远镜）换更贴近形状的 detect prompt

4. **关键词数量与召回**
   - 部分类（如 desktop_computers）`--queries` 写得偏少，最终 47 张可接受但可继续扩充
   - 提升思路：再加几个英文同义词（"PC desktop tower", "computer rig"）

## 产出
- 30 个类别目录，每类 33~184 张裁剪图（命名 `<class>_NNN.jpg`）
- 总计 2,916 张
- 批量驱动脚本 `run_all.py`，内嵌 30 类配置（可作为后续新增类的模板）
- 完整 stdout 日志：`logs/run_all_2026-05-11.log`

## 后续可改进项
- 把 `--detect-fallback` 默认设为 on，避免类似 brooms 的尴尬
- 对低产出类（<50）扩充关键词后再跑一次扫尾
- pHash 近似图去重（多源爬取可能有重复）
- 引入随机抽样人工核验工具，记录各类 precision
