>[English](README.md) · [中文说明](README_zh.md) 
# Js_task-organizer

> 任务整理助手（Task Organizer）是施嘉名（Jiaming Shi）开发的一个 skill——核心是 **文件夹整理** 与 **全局统筹**。

Js_task-organizer 帮你把杂乱的任务/项目文件夹整理成统一的标准三段式结构，并统筹整个任务的文件生命周期：任务一开始就建好全部结构、全程登记文件来源、用广播中心给出整个文件夹的只读地图、最终交付前再整理一次并重建索引。这样既能让文件夹在任务进行中始终保持整齐，也能在长任务里保护上下文窗口。

整理前后会做完整的目录快照，并强制执行 8 项一致性检查（C1–C8）；任何一项失败都 **自动回滚** 到整理前状态——通常可以避免出现“整理了一半且无法证明无损”的文件夹。

```
task_folder/
+---- _broadcast/            # 只读的上下文压缩索引
|   +---- INDEX.md           #   每个文件一行：摘要 + 关键词 + 分类
|   `---- index.json         #   同一份索引，机器可读
+---- material/
|   +---- initial/           # 你自己的材料——原样保留，绝不改名
|   +---- downloaded/        # 本次对话中由 AI 下载的文件
|   +---- duplicates/        # 查重模式隔离出的完全重复文件
|   +---- Index.md           # 自动生成的 Markdown 索引
|   `---- Index.xlsx         # 自动生成的 Excel 索引（含 Statistics 统计页）
+---- process/               # AI 产出 + 快照 + 日志 + 历史记录
|   +---- YYYYMMDD_HHMMSS_before.json
|   +---- YYYYMMDD_HHMMSS_after.json
|   +---- YYYYMMDD_HHMMSS_OrganizeLog.md
|   +---- sources.json       # 来源清单（用户 / 下载）
|   +---- verification_report.md        # C1-C8 校验结果
|   +---- history/           # 操作历史 + undo / redo
|   `---- logs/              # 按天记录的活动日志
`---- results/               # 最终交付物（文件名含 final / deliverable / 报告 / 综述）
```

**唯一需要记住的规则：`material/initial/` 只属于你。** 工具从不会把自己产生的任何文件写进这个目录，所以它永远不可能和你的文件撞名。你只需要：建好文件夹 → 把材料放进去 → 运行 `init`。你的材料始终原样保留，不会被改名或修改。

---

## 触发后必须执行的工作流（详见 `SKILL.md`）

> 这一节对应 `SKILL.md` 里的 “Execution steps”。README 只提供入口概览；Agent 实际调度时应以 `SKILL.md` 为准。

这个 skill 是一份“立即动手”的指令，不是一份用来总结的说明文档。只要用户的需求命中了本 skill 的适用范围，就必须运行工具并汇报结果——只回复一段“这个 skill 是什么、有什么功能、有哪些命令”的描述，等于任务失败。

**适用范围——工作空间 vs 直接对话。** 本 skill 只在用户**选定了一个工作空间**（任务 / 项目 / 研究文件夹）时才整套触发：建结构、保持整洁、把交付物归档。如果用户只是直接对话、没有选定任何工作空间文件夹，本 skill 不适用。

**标准动作链（摘要）：**

1. **会话开局结构检查——先检查，再动手。** 只要工作区文件夹在对话里被确定（被点名 / 被作为附件引用 / 在对话中给出了路径），第一步就是运行只读检查：
   ```bash
   python -m scripts.run doctor <root>
   ```
   `doctor` 只读：不写、不移动、不读内容，一次纯 stat 扫描、零成本——所以它在用户确认之前就能跑（它只是检查，不是改动）。报告 `incomplete` → 接着跑 `init <root>` 建好结构再开工；报告 `healthy` → 什么都不动，直接继续。这一步幂等：已经整齐的文件夹，检查一次、零改动。
2. **文件夹信号检测——先提议，再动手。** doctor 报告结构缺失、且用户没明确要求整理 → 提议一次 `init`，用户确认前不运行任何会改动文件夹的命令。用户明确要求整理，或请求是“产出内容 + 保持文件夹整洁”的复合请求 → 跳过提议，直接 `init`。
3. **确定目标文件夹路径。** 用户没给路径时，给一个具体默认值并让用户确认。
4. **选择入口。** 新建 / 空文件夹 → `init`；已有内容的乱文件夹 → `organize`。
5. **用 Bash 运行**（在本 skill 目录下）：
   ```bash
   python -m scripts.run init     <root>
   python -m scripts.run organize <root>
   ```
   需要 Python 3.10+；除标准库外无强制依赖（`openpyxl` 只用于生成 Excel 索引）。
6. **先验证再汇报。** 出现 `verification: failed` 时工具已自动回滚，如实汇报，不盲目重跑。
7. **简洁汇报**：三层结构现状、`material/initial/` 中原封不动的材料、校验结论、可用 `undo` 撤销。
8. **会话剩余时间里**：每次往任务文件夹下载文件，立刻 `mark-downloaded <root> <file> --url <URL>` 声明来源。
9. **最终交付前——再整理一次，并重建广播索引。** 这是强制动作：
   ```bash
   python -m scripts.run organize  <root>
   python -m scripts.run broadcast <root>
   ```
   广播索引（`_broadcast/INDEX.md`）在工作空间任务里是强制的、不是可选项。

### 内容产出场景（写综述 / 报告 / 文章 / 总结）

当“产出内容”和“把任务文件夹保持成标准三段式”同时出现时，本 skill 整套触发——**即使一个字都没提“整理”**。典型请求形状：读文件夹里的文件，然后写报告 / 可行性报告 / 综述 / 总结 / 笔记 / 开题报告。注意：触发不看任务“有几步”，也不依赖交付物的具体名称——只要在工作区文件夹里产出了任何交付物，哪怕只是一次性写完一篇，也要跑完整的组织-广播循环。标准动作链：

1. **先搭台。** 文件夹是新的或还没有三段式结构 → 动手写之前先跑 `init <root>`。
2. **产出内容。** 写进任务文件夹（放哪都行，`organize` 会归位）。
3. **随手声明来源。** 自己下载 → `mark-downloaded`；用户放入 → `init` 已登记，或用 `mark-user` 补声明。
4. **给交付物起个认得出来的名字。** 文件名含 `final` / `deliverable` / `report` / `summary` / `定稿` / `最终版` / `终稿` / `综述` / `报告` / `总结` / `小结` 的，自动进 `results/`。
5. **跑 `organize <root>`** 并汇报验证结果。
6. **构建广播索引。** `broadcast <root>` 让 `_broadcast/INDEX.md` + `_broadcast/index.json` 给每个文件写一句话摘要与关键词。

**回迁规则。** 如果第一次盲目 `organize` 把文件倒进了 `process/`，之后补声明来源（`mark-user` / `mark-downloaded`）再跑一次 `organize`，就会把它们搬回家。没有任何声明的文件依旧留在 `process/`（助手产出兜底桶），重跑保持幂等。

---

## 广播中心（`_broadcast/`）——上下文压缩索引

一个文件夹里的文档可能多到一次会话读不完。广播中心就是为此设计的：它对每个支持的文件生成只读摘要——小到每次会话都该先读它，也详细到足以判断下一步该打开哪个原文。

构建：

```bash
python -m scripts.run broadcast <root> [--ai] [--max-files N] [--keywords K]
```

它只往 `<root>/_broadcast/` 写两个文件：

| 文件 | 给谁看 |
|------|--------|
| `INDEX.md` | 你和后续的 AI 会话：每个文件一行（路径、类型、大小、日期、摘要、关键词） |
| `index.json` | 程序消费：同样数据的机器可读版 |

支持格式：`txt` / `md` / `csv` / `json` / `docx` / `pdf` / `pptx` / `xlsx`；其余文件只登记在“跳过”区。文本抽取标准库优先（`openpyxl` / `pdfminer` / `PyPDF2` 只是增强），容错编码：UTF-8（识别 BOM）、UTF-16、GBK/GB18030、Big5；读取有界。

摘要两种模式：

- **AI 模式**——`TASK_ORG_AI=1` 加密钥，或 `--ai`：一次调用同时拿到一句话摘要和关键词。没有密钥时会降级为本地模式，并在索引里标注 `local` 而不是虚标 `ai`。
- **本地模式**（默认）——取抽取文本的前 200 个字符（能落在句子边界就切在句末），关键词用统计法：英文按词频；中文把反复出现的 2–4 字 n-gram 扩展成完整重复短语。离线、确定、零成本。

保证：

- **只读**：原文件只被打开读取，不移动、不改名、不修改；唯一的写入就是 `_broadcast/` 里的两个文件。
- **幂等**：重跑就在原地重建这两个索引文件。
- **有界**：单文件抽取有上限，`--max-files` 限制总文件数，`INDEX.md` 过大只警告不失败。
- **受保护**：`_broadcast` 是工具自有目录，`init` / `organize` 绝不搬走它。

后续会话怎么用：`INDEX.md` 开头是一个目录——每个文件都按它最显著的关键词归类。先扫目录，跳到你需要的主题，只打开那些原文。下一次会话读的是目录，不是原文。

---

## 核心特性

围绕“文件夹整理 + 全局统筹”两条主线：

- **文件夹整理（标准三段式）**：自动建立 `material` / `process` / `results` 三层结构，按来源放置文件（你放的进 `material/initial/`、AI 下载的进 `material/downloaded/`、定稿 / 综述 / 报告进 `results/`、草稿 / 临时进 `process/`），绝不靠猜文件名。你的材料原样保留；撞名则留在原地并报告。
- **全局统筹（任务全生命周期）**：`init` 在任务开始即建好全部结构（含 `_broadcast/`）；随手用 `mark-downloaded` / `mark-user` 登记来源；用广播中心给出整个文件夹的只读地图；最终交付前再 `organize` 一次并重建广播索引。
- **无损与安全**：强制前后 SHA-256 快照 + C1–C8 八项一致性检查，失败自动回滚；`undo` / `redo` 可撤销 / 重做；`--mode` 分档（quick / incremental / full）；`--keep N` 轮转产物。
- **可选增强**：智能查重、YAML 规则 + 领域档案、独立 `index` / `snapshot`、双格式索引（Markdown + Excel）、AI 摘要（默认关闭）、中文交付关键词、按天日志。

---

## 下载与安装

**方式一 —— 下载 Release 包（推荐）**
打开仓库的 Releases 页面，下载最新的 zip 压缩包，解压即可——无需安装步骤。

**方式二 —— 克隆仓库**

```bash
git clone https://github.com/JiamingShi-phys/Js_Agent-Skills.git
cd Js_Agent-Skills/Js_task-organizer
```

环境要求：Python 3.10+。`openpyxl` 为可选依赖（仅用于生成 Excel 索引；不安装也能正常生成 Markdown 索引）。除 `openpyxl` 外的所有特性均仅使用标准库实现，不引入新依赖。

---

## 快速开始

```bash
cd Js_Agent-Skills/Js_task-organizer

# 0. （可选）只读诊断：结构 / 散落文件 / 广播新鲜度
python -m scripts.run doctor /path/to/task_folder

# 1. 先建好任务文件夹，把自己的材料放进去（手动）。
# 2. 轻量 init：搭骨架 + 把你的材料原样搬进 material/initial/。
python -m scripts.run init /path/to/task_folder

# 3. 完整整理 + 校验（失败自动回滚）。
python -m scripts.run organize /path/to/task_folder

# 4. AI 下载了文件 -> 先声明来源，再整理。
python -m scripts.run mark-downloaded /path/to/task_folder fetched.pdf --url https://...
python -m scripts.run organize /path/to/task_folder --mode quick
```

其他命令：

```bash
python -m scripts.run organize /path/to/task_folder --mode incremental --keep 5
python -m scripts.run organize /path/to/task_folder --profile pharma --config rules.yml
python -m scripts.run index    /path/to/task_folder        # 只重新生成索引
python -m scripts.run snapshot /path/to/task_folder        # 危险操作前的安全气囊
python -m scripts.run undo     /path/to/task_folder/process/history/<file>.json
python -m scripts.run redo     /path/to/task_folder/process/history/<file>.json
python -m scripts.run dedupe   /path/to/task_folder --action report
python -m scripts.run doctor   /path/to/task_folder        # 只读诊断：结构/散落文件/广播新鲜度
python -m scripts.run broadcast /path/to/task_folder --ai   # AI 摘要（默认本地模式）
```

输出示例：

```
Root: /path/to/task_folder
mode: full
organize: done
verification: passed
history: wrote 20261012_191444_history.json
```

看到 `verification: passed` 时，三层结构已经可以安全使用；出现 `verification: failed` 时系统已自动回滚，修复问题后重试。

### 稳定状态下的文件流向

```
你建好文件夹，把材料放进去
        |
        v
   +---------+      +-------------------------------------------+
   |  init   |----->| material/initial/<你的文件，原封不动>      |
   +---------+      +-------------------------------------------+
        |
        v  （之后随着工作推进）
   organize --mode=quick|incremental|full
        |
        +--> AI 自己的产出 .................... process/
        +--> 含 final / deliverable ............ results/
        +--> mark-downloaded 后再整理 ......... material/downloaded/
        |
        v
   index     （需要交接报告时）
   snapshot  （任何危险操作之前）
```

目标是让文件夹在整个任务里尽量保持整齐，而不是等到最后才整理一次：骨架只建一次，之后随手把东西放对位置。

### 分步调用（作为 Python 库使用）

```python
from pathlib import Path
from scripts import snapshot, organize, verify, index_md, index_xlsx, rollback, utils

root = Path("/path/to/task_folder").resolve()

before = snapshot.make_snapshot(root, phase="before")
session = utils.OrganizeSession(root=root)
organize.organize_folder(root, session=session)

after = snapshot.make_snapshot(root, phase="after")
vres = verify.verify(root, session=session, before=before, after=after)

if not vres.passed:
    rollback.rollback(root, session=session)   # 校验失败 -> 回滚
else:
    index_md.write_index_md(root)
    index_xlsx.write_index_xlsx(root)
```

---

## 测试与覆盖率

```bash
pytest                                            # 运行全部测试
pytest --cov=scripts --cov-report=term-missing    # 带覆盖率报告
```

当前测试套件共 340 个用例，覆盖率约 88%（目标 >= 80%）。

---

## 项目结构

```
Js_task-organizer/
+---- SKILL.md              # 技能入口（YAML 元数据 + 执行指南）
+---- README.md
+---- LICENSE               # MIT
+---- CHANGELOG.md
+---- CONTRIBUTING.md
+---- .gitignore
+---- .task-organizer.yml.example   # YAML 配置示例（含 pharma 领域档案）
+---- requirements.txt      # openpyxl, pytest, pytest-cov
+---- scripts/
|   +---- __init__.py
|   +---- run.py            # 流水线编排 + CLI（init/material/index/snapshot/undo/redo/dedupe/mark-*）
|   +---- scan.py           # 递归扫描与条目分类
|   +---- snapshot.py       # 前后快照（可选复用哈希缓存）
|   +---- organize.py       # 三层结构 + 基于来源的放置
|   +---- verify.py         # 强制 8 项一致性校验（C1-C8）
|   +---- rollback.py       # 基于日志的回滚
|   +---- dedupe.py         # 精确 + 相似查重
|   +---- history.py        # 操作历史 + Undo/Redo
|   +---- rules.py          # YAML 规则配置 + 领域档案
|   +---- init.py           # 轻量骨架 + 内容搬移
|   +---- sources.py        # 来源清单
|   +---- hashcache.py      # 增量哈希缓存
|   +---- rotate.py         # 产物轮转
|   +---- text_extract.py   # 多格式文本抽取（docx/pdf/pptx/xlsx）
|   +---- broadcast.py      # 广播中心：上下文压缩索引（_broadcast/）
|   +---- doctor.py         # 只读诊断：结构完整性 / 散落文件 / 广播新鲜度
|   +---- index_md.py       # Markdown 索引
|   +---- index_xlsx.py     # Excel 索引 (openpyxl)
|   `---- utils/            # 共享工具（路径/日志/快照/AI摘要/结构）
|       +---- __init__.py
|       `---- logger.py     # 标准库日志
+---- references/
|   +---- naming-conventions.md
|   `---- verification-protocol.md
+---- assets/
|   +---- index-template.md
|   `---- verification-report-template.md
`---- tests/
    +---- __init__.py
    +---- conftest.py
    +---- fixtures/
    +---- test_scan.py
    +---- test_snapshot.py
    +---- test_organize.py
    +---- test_verify.py
    +---- test_rollback.py
    +---- test_index.py
    +---- test_run.py
    +---- test_dedupe.py
    +---- test_history.py
    +---- test_rules.py
    +---- test_logger.py
    +---- test_init.py
    +---- test_sources.py
    +---- test_hashcache.py
    +---- test_rotate.py
    +---- test_doctor.py        # 只读诊断
    +---- test_skill_docs.py    # 文档契约（工作流、触发条件）
    `---- test_broadcast.py     # 广播中心：抽取、只读、幂等
```

---

## 作为 Agent 技能挂载使用

本项目是一个自包含的 Agent Skill 包。`SKILL.md` 包含 YAML 元数据（`name` / `description` / `version` / `author` / `license` / `allowed-tools`），并附带 “Execution steps” 执行指南。只需将本文件夹指向任何 AI Agent Harness。当用户的需求命中本技能适用范围时，Agent 会读取 `SKILL.md` 中的执行步骤并调用底层脚本（技能的加载取决于 Agent 对适用范围的识别，并不保证每次对话都会触发）。

给 Agent 的一条重要约定：只要在本次对话中往任务文件夹里下载或抓取了文件，就立刻调用 `mark-downloaded`（附上来源 URL）。这才是让 `downloaded/` 真正表示“AI 下载的文件”、而不是“文件名里刚好带 download 的文件”的唯一办法。

你也可以直接在 Python 中调用这些模块：

```python
from pathlib import Path
from scripts import run
result = run.run(Path("/path/to/task_folder"))
print(result.summary_lines())
```

---

## 开源协议

MIT License，详见 [LICENSE](LICENSE)。

---

## 报告问题与反馈

请使用仓库统一的入口提交问题：参见仓库根目录 `README.md` 中的 “Report issues” 部分（邮箱 `jiaming_shi_phys@outlook.com`，主题前缀 `agent-skill_report`）。提交清晰、可复现 Issue（或修复代码）的贡献者，将被列入下一个版本发布说明的致谢名单。
、
