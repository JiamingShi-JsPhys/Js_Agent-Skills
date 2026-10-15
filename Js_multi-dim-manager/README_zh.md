[English](README.md) · [中文说明](README_zh.md)

# Js_multi-dim-manager

> 一个自包含的多维度计算实验状态管理器。它把参数网格在几百轮里迭代，每轮对声明的
> 关键路径做快照，审计每一轮，并能非破坏性地回滚到任意一轮。算力由你的计算插件提供，
> 本技能只负责管理它周边的状态。

---

## 触发后必须执行的工作流（详见 SKILL.md）

当用户要求运行、检查或恢复一个多维度实验时：

1. 读取配置，确认参数空间、关键路径、插件命令都已就绪。
2. 展开笛卡尔积，先向用户报告总轮数。
3. 优先做一次 dry-run，让用户在产生任何副作用之前看到完整计划。
4. 执行扫描：每轮先快照关键路径，再调用插件，再快照，并追加一条审计记录。
5. 某轮失败时，记录其状态；若开启 `auto_rollback`，则恢复上一轮稳定状态（记入审计），
   不要因此中断整个扫描。
6. 汇总：写出 `results_summary.csv/.md`、`report_draft.md`、`run_metadata.json`。
7. 按需用 `rollback` 恢复（默认新建目录；`--force` 才覆盖）。

### 常见请求形状

- “把这个 2×2×2 网格、200 轮跑完，告诉我哪些组合通过了。”
- “第 47 轮崩了——把它的状态恢复出来，我想检查当时的输入。”
- “全部回滚到第 150 轮，换组参数从那里重跑。”
- “把最近 10 轮的审计轨迹给我看。”

## 本技能如何管理状态

技能把一个实验视为“按轮推进的状态机”，靠三套机制保持可信。

### 快照（内容寻址，只盯关键路径）

只快照你在 `critical_paths` 里声明的文件——绝不对整个工作目录做全量快照。每个文件按
SHA-256 内容寻址只存一份，所以跨轮不变的文件不额外占空间。一次快照只是一份清单：
`相对路径 -> 内容哈希`。

### 审计

每一轮向 `audit_log.jsonl` 追加一行 JSON，记录参数组合、输入哈希、输出哈希、时间戳、
插件退出码，以及前后两次快照（pre/post）。回滚动作同样入审计，事后可完整复现。

### 回滚（非破坏性）

`rollback --round N` 恢复第 N 轮的后置状态。默认落到**新目录**
（`<workdir>.rollback_NNNN`）；只有显式 `--force` 才覆盖当前工作目录。无论哪种，动作都
写入审计日志。

### 保证

- **可追溯**：每条输出都绑定一组参数组合与一份快照。
- **可恢复**：任意已记录轮次都能恢复，且动作留痕。
- **编排层确定性**：相同参数总是得到相同的计划与相同的记录哈希。（插件自身的确定性由
  用户负责——见“已知局限”。）

## 已知局限

- **确定性只保证在编排层**。技能记录哈希、对相同输入重放相同计划，但无法让一个本身不确定
  的插件变确定。若插件触网、用随机种子、或读取系统时钟，相同输入可能产生不同输出。这类
  不确定性请在插件里自行声明。
- **关键路径必须提前声明**。未列入 `critical_paths` 的文件不会被快照，因此也无法回滚。
- **黄金输出校验留到 v0.2**。当前校验器只检查插件契约（退出码 0 + 有结果文件）。与已知预期
  输出的比对尚未实现。
- **YAML 配置需要 PyYAML**。JSON 配置仅靠标准库即可。

## 核心特性

- 参数空间定义（JSON/YAML，笛卡尔展开）。
- 每轮对声明的关键文件做快照（内容寻址存储）。
- 完整、只追加的审计日志（输入/输出哈希 + 时间戳）。
- 非破坏性回滚到任意轮（`--force` 才覆盖）。
- 结果汇总为 CSV / Markdown，并给出报告草稿。
- 统一的插件契约：一条 shell 命令 + JSON 输入输出 + 退出码 0/1/2。
- 默认纯标准库——不依赖任何第三方包。

## 获取与使用

**方式一 —— 下载 Release 包（推荐）**

打开仓库的 Releases 页面，下载最新的 zip 压缩包，解压后运行
`pip install -r requirements.txt` 即可——无需编译构建。

**方式二 —— 让 Agent 代为获取**

把下面这段指令交给你的 Agent，它会自动定位并拉取这个技能：

> Please visit https://github.com/JiamingShi-JsPhys/Js_Agent-Skills/tree/main/Js_multi-dim-manager, read the README.md in that folder, and download or install the skill according to its instructions.

你只需把技能名告诉 Agent，剩下的交给它处理。

**方式三 —— 克隆仓库**

```bash
git clone https://github.com/JiamingShi-JsPhys/Js_Agent-Skills.git
cd Js_Agent-Skills/Js_multi-dim-manager
pip install -r requirements.txt
```

环境要求：Python 3.10+。使用 JSON 配置时无需任何第三方包；YAML 配置需要
`pyyaml`（`pip install pyyaml`）。其余均只用 Python 标准库。

## 快速开始

```bash
cd Js_Agent-Skills/Js_multi-dim-manager

# 0. （可选）先看完整计划，不真正执行
python scripts/run.py dryrun --config config.example.yaml

# 1. 运行扫描（在 ./output 下写出审计、快照、汇总）
python scripts/run.py run --config config.example.yaml

# 2. 把某一轮恢复到新目录
python scripts/run.py rollback --config config.example.yaml --round 12

# 3. 从审计日志重新生成汇总
python scripts/run.py summary --config config.example.yaml

# 4. 检查某一轮的插件契约结果
python scripts/run.py verify --config config.example.yaml --round 12
```

## 测试与覆盖率

测试套件当前覆盖 87 个用例。运行方式：

```bash
python -m pytest -q
```

目标行覆盖率 >= 80%，与仓库的质量基线一致。

## 项目结构

```
Js_multi-dim-manager/
  SKILL.md / README.md / README_zh.md
  config.example.yaml      # 配置模板
  sample_plugin.py         # 示例计算插件（契约演示）
  scripts/
    param_space.py         # 参数空间解析与展开
    config.py              # 实验配置加载
    executor.py            # 插件调用（shell + JSON + 退出码 0/1/2）
    snapshot.py            # 内容寻址的关键路径快照
    audit.py               # 只追加的 JSONL 审计日志
    rollback.py            # 非破坏性回滚
    aggregator.py          # 结果表汇总
    report.py              # Markdown 汇总 / 草稿
    verify.py              # 插件契约校验（黄金比对：v0.2）
    run.py                 # CLI 入口
  tests/                   # 单元测试 + 文档契约测试
```

## 作为 Agent 技能挂载使用

把整个文件夹放进任何支持 Skill 规范的 Agent 环境。当请求命中适用范围（多轮、多维、需要
跟踪状态的实验）时，Agent 读取 `SKILL.md` 并按其 MANDATORY WORKFLOW 执行。本技能自包含：
不 import 任何兄弟技能。

## 开源协议

基于 MIT 协议发布，详见 `LICENSE`。

## 报告问题与反馈

在本仓库的 Issues 页面提交，或邮件至 `jiamingshi_phys@outlook.com`，主题前缀
`agent-skill_report`。
