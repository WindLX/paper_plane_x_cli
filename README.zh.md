# Paper Plane X CLI

[English](README.md) | 中文

Paper Plane X 的独立 HTTP CLI 与外部 Agent 技能集。

本仓库包含：

- `ppx`：一个 JSON 优先的 CLI，用于与运行中的 Paper Plane X FastAPI 服务通信。
- `skills/ppx-researcher`：面向 Codex、Claude Code、Pi agent 等 Agent 工具的 Researcher 技能。
- `skills/ppx-pdf-to-markdown`：基于 Paper Plane X API 的 PDF 转 Markdown 工作流技能。

所有命令均调用运行中 Paper Plane X 服务 `/api/v1` 下的 HTTP 端点。

## 安装

CLI 使用 [uv](https://docs.astral.sh/uv/) 安装和升级：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

发布版本推荐从 PyPI 安装：

```bash
uv tool install paper-plane-x-cli
```

升级：

```bash
uv tool upgrade paper-plane-x-cli
```

卸载 CLI：

```bash
uv tool uninstall paper-plane-x-cli
```

本地开发或还没有发布到 PyPI 时，可以在 CLI 目录下从源码安装：

```bash
uv tool install .
```

执行 `uv tool install` 后，即可直接使用 `ppx`。

## 上下文

`ppx` 按以下优先级解析上下文：

1. 命令行选项：`--base-url`、`--project-id`
2. 环境变量：`PPX_BASE_URL`、`PPX_PROJECT_ID`
3. 本地上下文文件：当前工作目录下的 `./.paper-plane-x/context.json`
4. 全局上下文文件：`~/.config/paper-plane-x/context.json`
5. 默认值：base URL 为 `http://127.0.0.1:8000/api/v1`

本地上下文会覆盖全局上下文，因此可以在不修改全局默认配置的情况下为每个项目单独设置。

```bash
# 全局上下文（默认）
ppx context set --base-url http://127.0.0.1:8000/api/v1
ppx context set --project-id prj_x

# 本地上下文（仅当前目录）
ppx context set --local --project-id prj_y

ppx context show
```

## 常用命令

```bash
ppx project global-finder
ppx librarian search --query-expr "(meta.title CONTAINS transformer)" --limit 20
ppx librarian matrix --paper-ids p1,p2 --field-paths quick_scan,synthesis_data.methodology.innovation
ppx librarian deep-dive --paper-id p1 --question "What is the core contribution?"

ppx files list --dir /
ppx files read --path /notes/idea.md
ppx files upload --source ./idea.md --path /notes/idea.md
ppx files find --path /draft.md --query "Related Work"
ppx files patch --path /draft.md --action insert_after --anchor-text "## Related Work" --content "..."

ppx paper-note get --paper-id p1
ppx paper-note write --paper-id p1 --content "..."
ppx paper-note delete --paper-id p1
```

所有命令均以 JSON 格式输出到 stdout。HTTP 与校验失败会以结构化 JSON 输出到 stderr，并以非零状态码退出。

`files upload` 遵循与项目文件相同的沙箱规则：仅允许文本/数据扩展名、禁止路径穿越、单文件大小限制 10MB。

## PDF 解析

当外部 Agent 需要以 Markdown 形式读取或处理本地 PDF 时，使用 PDF 解析命令：

```bash
ppx pdf parse --source ./paper.pdf --save-dir ./paper-pdf
```

该命令将 PDF 上传到 Paper Plane X API，写入 Markdown 及引用的图片，并输出如下 JSON：

```json
{
  "md_path": "paper-pdf/paper.md",
  "image_paths": ["paper-pdf/images/fig1.png"],
  "parser_type": "local_mineru"
}
```

## 技能

自带的技能位于 `skills/` 目录下：

```text
skills/ppx-researcher/SKILL.md
skills/ppx-pdf-to-markdown/SKILL.md
```

当外部 Agent 需要遵循 Paper Plane X 的研究工作流时，使用 `ppx-researcher`：校验项目上下文、通过 `ppx` 搜索并对比论文、将结果写入项目文件或 paper note，并且只引用通过 CLI/API 实际获取到的证据。

当外部 Agent 遇到本地 PDF 需要先转换为 Markdown 再进行阅读、摘要、抽取或上传时，使用 `ppx-pdf-to-markdown`。

面向 Codex 时，默认会安装到 `${CODEX_HOME:-~/.codex}/skills`，这是 Codex 读取用户技能的默认目录：

```bash
ppx skills list
ppx skills install
ppx skills install --force
ppx skills uninstall
```

安装完成后，重启 Codex 或开启新会话即可看到 `ppx-researcher` 和 `ppx-pdf-to-markdown`。

也可以按你使用的 Agent 显式指定目标目录：

| 工具/场景 | 安装命令 | 说明 |
| --- | --- | --- |
| Codex 默认 | `ppx skills install` | 安装到 `${CODEX_HOME:-~/.codex}/skills` |
| 通用 Agent Skills / 兼容目录 | `ppx skills install --target-dir ~/.agents/skills` | 适合已经从 `~/.agents/skills` 读取技能的 Codex/Agent 环境 |
| Pi agent | `ppx skills install --target-dir ~/.pi/agent/skills` | 沿用 Pi agent 的技能目录 |
| Claude Code 用户级 | `ppx skills install --target-dir ~/.claude/skills` | 对当前用户的 Claude Code 会话生效 |
| Claude Code 项目级 | `ppx skills install --target-dir ./.claude/skills` | 随项目仓库分发；提交前请确认团队希望共享这些技能 |

```bash
ppx skills install --target-dir ~/.agents/skills
ppx skills install --target-dir ~/.pi/agent/skills
ppx skills install --target-dir ~/.claude/skills
ppx skills install --target-dir ./.claude/skills
```

`install` 会将所有自带的 `ppx-*` 技能复制到目标目录；已存在的技能目录会被跳过，除非传入 `--force`。`uninstall` 仅删除自带的 `ppx-*` 技能名称，不会动目标目录中的其他技能。

如果要彻底移除 CLI 与已安装技能，先卸载技能，再卸载 CLI：

```bash
ppx skills uninstall
uv tool uninstall paper-plane-x-cli
```

使用自定义目录安装过技能时，卸载时传入同一个目录：

```bash
ppx skills uninstall --target-dir ~/.agents/skills
```

## License

Paper Plane X CLI 使用 [GNU Affero General Public License v3.0 or later](LICENSE)。
