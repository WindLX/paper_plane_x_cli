# Paper Plane X CLI

[![PyPI](https://img.shields.io/pypi/v/paper-plane-x-cli)](https://pypi.org/project/paper-plane-x-cli/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)

[English](README.md) | 中文

`ppx` 是 [Paper Plane X](https://github.com/WindLX/paper_plane_x) 的 JSON 优先命令行客户端与外部 Agent 集成包。它通过稳定的 HTTP 命令提供项目发现、文献检索、论文对比、PDF 解析、项目文件编辑和论文备注管理能力。

本包还提供两个 Agent Skills：

- `ppx-researcher`：在 Paper Plane X 项目中执行基于证据的文献研究。
- `ppx-pdf-to-markdown`：使用 Paper Plane X 中配置的解析器将本地 PDF 转换为 Markdown。

所有远程命令都调用运行中 Paper Plane X Backend 的 `/api/v1` 接口；CLI 不会直接读取后端数据库。

## 适用场景

- 希望通过终端和脚本完成研究工作的用户。
- 依赖稳定 JSON 输出和非零失败状态码的自动化任务。
- Codex、Claude Code、Pi agent 及其他兼容 Agent Skills 的工具。
- 将 Paper Plane X 集成到本地研究流水线的开发者。

## 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- 执行远程命令时，需要一个运行中的 Paper Plane X Backend
- 执行项目级命令时，需要一个 Paper Plane X 项目 ID

## 安装

推荐从 PyPI 安装已发布版本：

```bash
uv tool install paper-plane-x-cli
ppx --help
```

升级或卸载：

```bash
uv tool upgrade paper-plane-x-cli
uv tool uninstall paper-plane-x-cli
```

开发时可安装当前源码：

```bash
uv tool install .
```

## 快速开始

配置后端地址和默认项目：

```bash
ppx context set --base-url http://127.0.0.1:8000/api/v1
ppx context set --project-id prj_x
ppx context show
```

检索并对比项目中的论文：

```bash
ppx project global-finder
ppx librarian search \
  --query-expr "(meta.title CONTAINS transformer)" \
  --limit 20
ppx librarian matrix \
  --paper-ids pap_a,pap_b \
  --field-paths meta.title,quick_scan.quick_summary
ppx librarian deep-dive \
  --paper-id pap_a \
  --question "What is the core contribution?"
```

将结果保存到项目工作区：

```bash
ppx files upload --source ./comparison.md --path /notes/comparison.md
```

## 上下文解析

`ppx` 按以下优先级解析配置：

1. 命令行选项：`--base-url`、`--project-id`；
2. 环境变量：`PPX_BASE_URL`、`PPX_PROJECT_ID`；
3. 本地上下文：`./.paper-plane-x/context.json`；
4. 全局上下文：`~/.config/paper-plane-x/context.json`；
5. 默认后端地址：`http://127.0.0.1:8000/api/v1`。

本地上下文覆盖全局上下文，适合让不同工作目录分别关联不同的 Paper Plane X 项目。

```bash
# 全局默认值
ppx context set --base-url http://127.0.0.1:8000/api/v1
ppx context set --project-id prj_default

# 仅当前目录
ppx context set --local --project-id prj_current
```

临时命令或 CI 可使用环境变量：

```bash
PPX_BASE_URL=http://127.0.0.1:8000/api/v1 \
PPX_PROJECT_ID=prj_x \
ppx project global-finder
```

不要在上下文文件中保存密钥。CLI 上下文只包含服务地址和项目标识，不包含 LLM API Key。

## 命令分组

| 分组             | 用途                                           |
| ---------------- | ---------------------------------------------- |
| `ppx context`    | 设置和查看全局或本地上下文                     |
| `ppx project`    | 项目级发现                                     |
| `ppx librarian`  | 检索、矩阵对比和单篇深度分析                   |
| `ppx pdf`        | 将本地 PDF 转换为 Markdown 和图片              |
| `ppx paper`      | 下载已保存的论文 Markdown                      |
| `ppx paper-note` | 读取、写入或删除持久化论文备注                 |
| `ppx files`      | 列出、读取、写入、上传、局部修改和删除项目文件 |
| `ppx skills`     | 安装或移除随包提供的 Agent Skills              |

使用 `ppx <分组> --help` 查看当前版本的完整参数。

## 项目文件

```bash
ppx files list --dir /
ppx files read --path /notes/idea.md
ppx files lines --path /draft.md --start-line 1 --end-line 40
ppx files find --path /draft.md --query "Related Work"
ppx files write --path /notes/idea.md --content "# Idea"
ppx files upload --source ./idea.md --path /notes/idea.md
ppx files patch \
  --path /draft.md \
  --action insert_after \
  --anchor-text "## Related Work" \
  --content "..."
ppx files delete --path /notes/obsolete.md
```

项目文件受后端沙箱保护：禁止路径穿越，仅接受允许的文本或数据扩展名，单个上传文件最大为 10 MB。

Agent 修改已有文档时，优先使用 `find`、`lines`、`replace-*` 或 `patch` 进行局部变更，以减少意外覆盖并获得明确的失败结果。

## 论文 Markdown 与备注

下载某篇论文已解析并保存的 Markdown：

```bash
ppx paper markdown --paper-id pap_x --save-dir ./paper-markdown
```

默认文件名为 `<paper-id>.md`，可通过 `--output-md-name` 修改。

维护持久化论文备注：

```bash
ppx paper-note get --paper-id pap_x
ppx paper-note write --paper-id pap_x --content "Stable research note"
ppx paper-note delete --paper-id pap_x
```

单篇论文的稳定结论适合写入 paper note；跨论文综述、矩阵、计划和草稿适合保存为项目文件。

## PDF 转 Markdown

```bash
ppx pdf parse --source ./paper.pdf --save-dir ./paper-pdf
```

该命令把 PDF 上传至后端配置的解析器，写入 Markdown 及其中引用的图片，清理未引用图片，并输出 JSON 摘要：

```json
{
  "md_path": "paper-pdf/paper.md",
  "image_paths": ["paper-pdf/images/fig1.png"],
  "parser_type": "local_mineru"
}
```

解析器类型与凭据由后端 Settings 管理，不在 CLI 中重复配置。

## Agent Skills

随包提供的技能位于：

```text
skills/ppx-researcher/SKILL.md
skills/ppx-pdf-to-markdown/SKILL.md
```

列出并安装技能：

```bash
ppx skills list
ppx skills install
```

默认安装目录为 `${CODEX_HOME:-~/.codex}/skills`。其他工具可显式指定目录：

| 工具或作用域           | 命令                                                 |
| ---------------------- | ---------------------------------------------------- |
| Codex 默认目录         | `ppx skills install`                                 |
| 通用 Agent Skills 目录 | `ppx skills install --target-dir ~/.agents/skills`   |
| Pi agent               | `ppx skills install --target-dir ~/.pi/agent/skills` |
| Claude Code 用户级     | `ppx skills install --target-dir ~/.claude/skills`   |
| Claude Code 项目级     | `ppx skills install --target-dir ./.claude/skills`   |

已存在的同名技能目录会被跳过，除非使用 `--force`。`uninstall` 只删除随包提供的 `ppx-*` 技能：

```bash
ppx skills uninstall
ppx skills uninstall --target-dir ~/.agents/skills
```

安装完成后，请重启 Agent 应用或开启新会话。

## 输出与自动化契约

- 成功的远程命令将 JSON 输出到 stdout。
- HTTP、上下文和参数校验错误将结构化 JSON 输出到 stderr。
- 失败时返回非零状态码。
- 下载命令只向指定的本地目录写入文件。
- CLI 不记录或持久化后端的 LLM 凭据。

脚本应解析 JSON，不要依赖面向用户的终端排版。

## 开发

```bash
git clone https://github.com/WindLX/paper_plane_x_cli.git
cd paper_plane_x_cli
uv sync
uv run ppx --help
```

质量检查：

```bash
just lint
just format-check
just typecheck
just test
just build
just pre-commit
```

对应的 uv 命令：

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright
uv run pytest
uv build
```

## 贡献与 Pull Request

1. 从最新 `main` 创建范围明确的分支。
2. 除非变更明确引入破坏性契约，否则应保持 JSON 输出兼容。
3. 为命令解析、上下文优先级、请求载荷和文件输出添加测试。
4. 面向用户的变更应同时更新 `README.md` 与 `README.zh.md`。
5. 工作流或 CLI 契约变化时，应同步更新随包提供的 Skill 指令。
6. 提交 PR 前运行 `just pre-commit`。

PR 描述应包含变更动机、受影响命令、兼容性影响和验证命令。不要在 Issue、日志或测试夹具中提交 API Key、私有论文内容或本地上下文文件。

问题与功能建议请提交至 [GitHub Issues](https://github.com/WindLX/paper_plane_x_cli/issues)。

## 发布

CLI 版本由 Paper Plane X monorepo 的 `VERSION` 文件统一管理。顶层 `vX.Y.Z` Release 会构建 wheel 和源码分发包，并通过 GitHub Actions Trusted Publishing 发布到 PyPI。

请勿单独修改 CLI 版本；应使用 monorepo 的统一发布流程。

## License

Paper Plane X CLI 使用 [GNU Affero General Public License v3.0 or later](LICENSE)。
