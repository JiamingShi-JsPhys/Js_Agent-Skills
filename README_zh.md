> [English](README.md) · [中文说明](README_zh.md)

# Js_Agent-Skills：面向 AI Agent 的自包含技能集合

`Js_Agent-Skills` 是 **Jiaming Shi（施嘉名）** 开发并维护的 Agent 技能仓库。它面向各种 AI Agent 工具，提供标准化、可审计、可靠的本地执行能力。

仓库中的每个技能都是一个独立、自包含的包。运行技能无需复杂的安装或构建步骤——只要环境支持 Skill 规范，即可直接挂载使用。

- [设计原则与核心特征](#设计原则与核心特征)
- [下载与安装](#下载与安装)
- [快速开始](#快速开始)
- [发布范围](#发布范围)
- [仓库布局](#仓库布局)
- [开发与贡献](#开发与贡献)
- [报告问题](#报告问题)
- [开源协议](#开源协议)

## 设计原则与核心特征

1. **Agent 原生**：每个技能都附带一份带标准元数据的 `SKILL.md`。Agent 可以自行读取该文件、理解技能适用范围与执行步骤，并自主调用底层脚本。
2. **零依赖部署**：技能尽量只用 Python 标准库，避免复杂的依赖链，保证跨平台即插即用（Windows / macOS / Linux）。
3. **确定性安全**：为防止 AI 执行幻觉，每个技能都强制可验证、可回滚的操作与完整的审计日志。
4. **触发即执行**：每个技能的 `SKILL.md` 以强制工作流开篇——命中适用范围的请求会让 Agent 直接运行工具并汇报结果，而不是只描述这个工具能做什么。

### 六个技能

目前有 6 个可安装技能，按功能分组如下。每一行链接到该技能的 `README.md`（本表是唯一总览；点进去是各技能的详细文档）。

| | 功能类别 | 技能 | 一句话说明 | 依赖库 |
| :--- | :--- | :---: | :--- | :--- |
| | **文件与项目管理** | [`Js_task-organizer`](Js_task-organizer/README_zh.md) v1.1.0 | 把杂乱的任务文件夹整理成三段式结构，提供广播中心作为上下文压缩索引 | 标准库 |
| | | [`Js_document-evolution-tracker`](Js_document-evolution-tracker/README_zh.md) v1.0.0 | 追踪文档家族的版本对齐与概念谱系，自动发现版本、做块级 diff 并渲染时间线 | 标准库 |
| | **实验运行与调度** | [`Js_multi-dim-manager`](Js_multi-dim-manager/README_zh.md) v1.1.0 | 把参数空间笛卡尔展开成多轮独立任务，用于多个同类型任务的自动运行 | 标准库 + PyYAML（可选，用于 YAML 配置） |
| | **数据分析与提取** | [`Js_longitudinal-analysis`](Js_longitudinal-analysis/README_zh.md) v1.0.0 | 纵向统计分析流水线：描述性统计、操纵检验、线性混合模型、滞后中介与敏感性分析 | `pandas`、`numpy`、`scipy`、`statsmodels`、`openpyxl`；可选 `Rscript` + `lme4`/`lavaan` |
| | **质量验证与检测** | [`Js_formula-validator`](Js_formula-validator/README_zh.md) v1.0.1 | 物理 / 数学公式的确定性校验器，对多层独立检查并输出报告 | 标准库 |
| | | [`Js_conflict-detector`](Js_conflict-detector/README_zh.md) v1.0.0 | 跨文档冲突检测器，提取数值 / 布尔断言与条款做分类，输出冲突报告 | 标准库 |

## 下载与安装

获取技能共有**四种**标准方式：

### 方式一：跨平台安装器（推荐）
**Releases** 页发布**每个技能一个安装器**（本发版共 6 个，每个技能一个）。下载你要的那个技能的安装器并运行——会弹出一个原生安装窗口（和标准安装程序一样）：顶部固定显示该技能的标题与描述，随后勾选一个或多个目标 harness 框架（全称清单：Claude Code、DeepSeek Harness、OpenAI Codex、WorkBuddy）并选择安装作用域（用户或项目），点「安装」后，确定性进度条会逐个文件跟踪拷贝过程——和标准下载器一样，显示当前正在拷贝哪个文件、还剩多少个。窗口打开时**不预设任何选择**。选择项目作用域时，安装器会先扫描本机上的任务文件夹（依据 `.git`、`.workbuddy`、`.claude`、`.codex`、`.dsh`、`.agents`、`.task-organizer.yml` 等标记识别），并在下拉框中列出供你挑选，无需手动输入：
- **Windows**：`Js_<skill>-installer.exe`（每个技能一个，例如 `Js_task-organizer-installer.exe`）。每个二进制各自捆绑它的那个技能，双击只安装那一个。
- **macOS / Linux**：双击即用的 `.app` **暂未提供**（计划中）。在此之前，macOS 与 Linux 用户请走下面的源码包方式（方式二），或从仓库检出后用 CLI 入口。

若要改用 CLI（从仓库检出，或用二进制）：

```bash
# 列出可安装的技能。
python install.py --list

# 把所有技能装到用户作用域的 WorkBuddy、Claude Code、OpenAI Codex 与 DeepSeek Harness。
python install.py --platform all --scope user

# 只装一个技能到项目作用域（相对当前目录）。
python install.py --skill Js_task-organizer --scope project

# 强制覆盖已存在的安装。
python install.py --platform workbuddy --scope user --force
```

对应入口还有 `uninstall.py`（移除已安装技能）与 `verify.py`（校验安装完整性）。偏好 shell 的用户可用 `install.sh` / `install.ps1` 转发脚本。Windows 安装器由 `installer/installer_gui.py`（自包含、纯标准库的 tkinter 前端）按每个技能各构建一份；重建 6 个：

```bash
# Windows：一次构建 6 个 per-skill 安装器（需 PyInstaller）
python build_installers.py
```

macOS 的双击 `.app`（以及 Linux 的 `.sh`）**计划中、尚未提供**——待有 macOS 构建环境后再放到 Releases 页面。

#### 一行安装 —— 无需下载（Windows PowerShell）

不想下载任何文件？在 PowerShell 里跑这一条命令即可——它从 GitHub 直接取安装脚本、完成安装并自行清理临时文件：

```powershell
irm https://raw.githubusercontent.com/JiamingShi-JsPhys/Js_Agent-Skills/main/install-web.ps1 | iex
```

默认把**所有技能**装到用户作用域的 **WorkBuddy**。要指定技能、框架或作用域，用 scriptblock 形式传参（`| iex` 形式无法带参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/JiamingShi-JsPhys/Js_Agent-Skills/main/install-web.ps1))) -Skill Js_task-organizer -Frameworks workbuddy,claude -Scope user
```

参数：`-Skill`（技能名、逗号分隔多个，或 `*` 全部）、`-Frameworks`（`workbuddy`、`claude`、`codex`、`dsh`）、`-Scope`（`user` 或 `project`）、`-Dir`（项目作用域的任务文件夹）、`-Repo` / `-Branch`（默认本仓库、`main`）、`-Force`（覆盖已存在的安装）。需要 Windows PowerShell 5.1+，无需 Python。

> **为什么不能像浏览器那样直接"打开"？** 浏览器的下载弹窗（"打开 / 保存 / 保存为"）不可能不落盘直接运行网页上的 `.exe`——即使选"打开"，也是先存到临时目录再执行那份拷贝。这是浏览器安全边界，无法绕过。上面的一行命令是标准等效方案：在线运行，除已安装的技能外不在磁盘留下任何文件。

### 方式二：源码包
从 **Releases** 页（或「Generate ZIP / Generate Tarball」）下载源码包，解压即用，无需安装器：
```bash
# 来自 Releases 页的 .zip 或 .tar.gz
unzip js_agent_skills-<version>.zip        # 或: tar xzf js_agent_skills-<version>.tar.gz
cd js_agent_skills   # 每个技能就是顶层各自一个文件夹
```

### 方式三：让 Agent 自行获取

把下面这段指令复制给 Agent，它会自动定位对应技能并替你装好：

> 请访问仓库 https://github.com/JiamingShi-JsPhys/Js_Agent-Skills ，找到我需要的技能文件夹（注明是什么技能名字或者功能），阅读该文件夹下的 `README.md`，并按照其中的说明下载或安装该技能。

你只需要告诉 Agent 技能名，剩下的交给它。

### 方式四：克隆仓库

```bash
git clone https://github.com/JiamingShi-JsPhys/Js_Agent-Skills.git
cd Js_Agent-Skills   # 每个技能就是顶层各自一个文件夹
```

## 快速开始

### 1. 通过 Agent 挂载
将解压后的技能文件夹指向你的 Agent Harness。当用户的需求命中本技能适用范围时，Agent 会读取该文件夹下的 `SKILL.md`，按照其中的强制工作流调用底层脚本。注意：技能是否被加载取决于 Agent 对适用范围的识别，并不保证每次对话都会触发。

### 2. 通过命令行（CLI）直接运行
每个技能均提供基于 Python 的命令行接口。以 `Js_task-organizer` 为例：
```bash
cd Js_Agent-Skills/Js_task-organizer
python -m scripts.run /path/to/task_folder
```

以 `Js_conflict-detector` 为例：
```bash
cd Js_Agent-Skills/Js_conflict-detector
python -m src.cli --help
```

### 3. 作为 Python 库调用（示例）
```python
from pathlib import Path
from scripts import run   # 具体模块名请参考技能内的实际实现

result = run.organize(Path("/path/to/task_folder"))
print(result.summary_lines())
```
> 注：以上为示例，实际接口以技能目录内的文档为准。

## 发布范围

本轮发布包含以下 **6 个可安装技能**：

- `Js_task-organizer`、`Js_formula-validator`、`Js_multi-dim-manager`、`Js_longitudinal-analysis`、`Js_conflict-detector`、`Js_document-evolution-tracker`。

此外，**6 个 per-skill 安装器二进制**（Windows 每个技能各一个双击 `.exe`，由 `installer/` 经 PyInstaller 构建）会作为发布资产挂在 **Releases** 页面上，用户无需克隆仓库即可安装单个技能。macOS 的 `.app` 与 Linux 的 `.sh` 为计划中、尚未提供；这两个平台请走上面的源码包方式。

## 仓库布局

所有已发布技能都平铺在**仓库根目录**，作为相互独立的顶层文件夹。下方的树与磁盘实际布局一一对应：先目录后文件，各组内按**字母序**排列。各技能的内部结构见其自带 README 的「项目结构」一节。

```
Js_Agent-Skills/
├── Js_conflict-detector/                     # 跨文档冲突检测器
├── Js_document-evolution-tracker/            # 版本对齐 + 概念谱系
├── Js_formula-validator/                     # 物理 / 数学公式确定性校验器
├── Js_longitudinal-analysis/                 # 纵向统计分析流水线
├── Js_multi-dim-manager/                     # 多维度实验状态管理器
├── Js_task-organizer/                        # 任务文件夹整理 + 广播中心
├── installer/                                # 跨平台安装器（原生 tkinter 窗口 + 内核）
│   ├── __init__.py
│   ├── assets/
│   │   └── README.md                         #   图标资产（打包前放入各平台图标）
│   ├── installer_core.py                     #   与 GUI 解耦的安装/卸载/校验逻辑
│   ├── installer_gui.py                      #   双击目标（用 PyInstaller 打包成 .exe/.app）
│   ├── platform_paths.py                     #   (平台, 作用域) -> 目标目录
│   ├── requirements.txt
│   └── skill_loader.py                       #   自适应技能发现
├── tests/                                    # 安装器单元测试
├── .gitignore
├── AUTHORS.md
├── audit_pre_publish.py                      # 发布前一致性审计
├── build_installers.py                       # 各技能 .exe 构建器（PyInstaller）
├── build_release.py                          # 各技能源码包构建器
├── CITATION.cff
├── install-web.ps1                           # 一行式网络安装器（PowerShell）
├── LICENSE
├── README.md
├── README_zh.md
├── VERSION
├── conftest.py
├── install.ps1
├── install.py
├── install.sh
├── uninstall.py
└── verify.py
```

一个技能即一个含 `SKILL.md` 的目录；`skill.json` 携带更完整的元数据。每个已发布技能至少携带 `SKILL.md`、中英双语文档、`LICENSE`、`CHANGELOG.md`、`skill.json`、`requirements.txt` 与 `tests/` 测试目录；多数还携带 `pyproject.toml`、`CITATION.cff` 与 `AUTHORS.md`（公式校验器除外），以及各技能特有的 `CONTRIBUTING.md`、配置示例或 `src/` / `scripts/` / `mcp_server/` 代码树。

## 开发与贡献

本仓库遵循严格的开源工程标准。如果你希望提交新的技能或修复现有问题：

1. **独立性原则**：每个 Skill 必须位于独立文件夹中，且包含完整的 `LICENSE`、`README.md` 以及标准的 `SKILL.md` 文件。
2. **质量底线**：提交的 Python 代码必须包含类型提示（Type hints）与 Docstrings，并附带覆盖核心逻辑的单元测试（目标覆盖率 >= 80%）。
3. **版本控制**：遵循 [Semantic Versioning](https://semver.org/) 与 [Keep a Changelog](https://keepachangelog.com/) 规范记录变更。
4. **代码风格**：遵循 PEP 8 规范（建议行宽 <= 88），核心流程要求异常捕获与优雅降级，尽量避免在预期 I/O 错误下直接崩溃。

## 报告问题

首选：在本仓库的 **Issues** 页面提交问题（对于安全漏洞问题的报告，使用备选方案）。

备选（仅供报告安全漏洞问题）：发送邮件至 `jiamingshi_phys@outlook.com`

- **邮件主题**：必须包含前缀 `agent-skill_report`，并注明具体技能与简要问题。
  - 示例：`agent-skill_report Js_task-organizer: path traversal 可读取任务文件夹之外的路径`
- **邮件正文**：必须包含复现步骤、预期行为、实际行为以及运行环境（操作系统、Python 版本、相关依赖安装状态）。
- 针对「文件丢失或损坏」的严重报告，请附带前后目录树结构（`tree` 输出）与生成的 `verification_report.md`。
- 提交清晰、可复现 Issue 或 Pull Request 的贡献者，将被列入下个版本发布说明的致谢名单。

## 开源协议

本仓库整体采用 [MIT License](LICENSE) 发布，详见根目录下的 `LICENSE` 文件。

每个技能包内均携带独立的 `LICENSE` 文件，以该技能目录下的声明为准。
