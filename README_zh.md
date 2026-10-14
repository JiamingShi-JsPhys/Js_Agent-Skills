>[English](README.md) · [中文说明](README_zh.md) 
# Js_Agent-Skills：面向 AI Agent 的自包含技能集合

`Js_Agent-Skills` 是施嘉名（Jiaming Shi）开发维护的 Agent 技能仓库。每个子文件夹是一个独立、自包含的 Skill 包，无需安装或构建，即可直接挂载到任意支持 Skill 规范的 AI Agent 环境。

## 技能

| 文件夹 | 技能 | 一句话说明 |
| :--- | :--- | :--- |
| `Js_task-organizer/` | Js_task-organizer | 把杂乱的任务文件夹整理成经过验证的三段式结构。 |
| *（计划中）* | *待定* | *面向科研、数据处理、AI 工作流的独立技能包将陆续加入。* |

## 如何获取与安装

### 方式一：下载 Release 包（推荐）
1. 前往仓库的 **Releases** 页面（右侧边栏或标签列表）。
2. 下载对应技能的最新 Release 压缩包。
3. 解压至任意目录。无需安装步骤。

### 方式二：让 Agent 自行获取

把下面这段指令复制给 Agent，它会自动定位并下载对应技能：

> 请访问仓库 https://github.com/JiamingShi-JsPhys/Js_Agent-Skills，找到我需要的技能文件夹（注明是什么技能名字或者功能），阅读该文件夹下的 `README.md`，并按照其中的说明下载或安装该技能。

每个技能文件夹的 `README.md` 里都写有该技能的获取方式。你只需要告诉 Agent 技能名，剩下的交给它。

### 方式三：克隆仓库

```bash
git clone https://github.com/JiamingShi-JsPhys/Js_Agent-Skills.git
```

克隆完成后，进入你需要的技能目录，把该技能文件夹整体取出，放到你自己的项目或 Agent Harness 中即可：

```bash
cd Js_Agent-Skills/Js_task-organizer
# 这个文件夹就是完整的技能包，复制到任意位置即可使用
```

仓库里同时包含多个技能时，你不需要全部保留，只取出目标技能文件夹即可。

## 如何运行技能

### 1. 通过 Agent 挂载
将解压后的技能文件夹指向你的 Agent Harness。当用户的需求命中本技能适用范围时，Agent 会读取该文件夹下的 `SKILL.md`，按照其 “Execution steps” 指南调用底层脚本。注意：技能是否被加载取决于 Agent 对适用范围的识别，并不保证每次对话都会触发。

### 2. 通过命令行（CLI）直接运行
每个技能均提供基于 Python 的命令行接口。以 `Js_task-organizer` 为例：
```bash
cd Js_Agent-Skills/Js_task-organizer
python -m scripts.run /path/to/task_folder
```

### 3. 作为 Python 库调用（示例）
```python
from pathlib import Path
from scripts import run   # 具体模块名请参考技能内的实际实现

result = run.organize(Path("/path/to/task_folder"))
print(result.summary_lines())
```
> 注：以上为示例，实际接口以技能目录内的文档为准。

## 开发与贡献规范

本仓库遵循严格的开源工程标准。如果你希望提交新的技能或修复现有问题：

1. **独立性原则**：每个 Skill 必须位于独立文件夹中，且包含完整的 `LICENSE`、`README.md` 以及标准的 `SKILL.md` 文件。
2. **质量底线**：提交的 Python 代码必须包含类型提示（Type hints）与 Docstrings，并附带覆盖核心逻辑的单元测试（目标覆盖率 >= 80%）。
3. **版本控制**：遵循 [Semantic Versioning](https://semver.org/) 与 [Keep a Changelog](https://keepachangelog.com/) 规范记录变更。
4. **代码风格**：遵循 PEP 8 规范（建议行宽 <= 88），核心流程要求异常捕获与优雅降级，尽量避免在预期 I/O 错误下直接崩溃。

## 报告问题与反馈

首选：在本仓库的 **Issues** 页面提交问题。

备选：发送邮件至 `jiamingshi_phys@outlook.com`

- **邮件主题**：必须包含前缀 `agent-skill_report`，并注明具体技能与简要问题。
  - 示例：`agent-skill_report Js_task-organizer: dedupe move fails on read-only file`
- **邮件正文**：必须包含复现步骤、预期行为、实际行为以及运行环境（操作系统、Python 版本、相关依赖安装状态）。
- 针对“文件丢失或损坏”的严重报告，请附带前后目录树结构（`tree` 命令输出）与生成的 `verification_report.md`。
- 提交清晰、可复现 Issue 或 Pull Request 的贡献者，将被列入下个版本发布说明的致谢名单。

## 开源协议

本仓库整体采用 [MIT License](LICENSE) 发布，详见根目录下的 `LICENSE` 文件。

每个技能包内均携带独立的 `LICENSE` 文件，以该技能目录下的声明为准。
