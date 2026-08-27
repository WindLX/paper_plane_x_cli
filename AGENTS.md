# Paper Plane X CLI 开发指南

## 作用域与工具链

- 本文件适用于 CLI 独立仓库。若在 monorepo 中开发，同时遵循上级 `AGENTS.md`；冲突时以本文件的项目级规则为准。
- 本项目是 Python 3.12+ 独立 uv package。以 `pyproject.toml`、`uv.lock`、本目录 `justfile` 和 `tests/` 为事实源，不直接导入 sibling backend 的环境或内部代码。
- 常用命令：`just setup`、`just test [ARGS]`、`just lint`、`just format-check`、`just typecheck`、`just build`、`just pre-commit`。命令行为或打包内容变化时额外用 `uv run ppx --help` 或 `uvx --from . ppx --help` 做 smoke test。
- `skills/` 是随 wheel / sdist 发布的产品内容，不是随意复制的文档目录；修改后必须同时验证安装路径、资源包含和引用有效性。

## CLI 契约

- CLI 是 backend HTTP API 的独立客户端。保持 HTTP 边界，不导入 backend service、schema 或数据库实现来复用逻辑；共享契约通过稳定请求/响应和显式本地类型表达。
- stdout 只输出适合程序消费的结果；诊断和错误输出到 stderr；失败使用稳定的非零退出码。不得把进度日志、调试文本或富格式混入 JSON 输出。
- 新增或修改命令时保持选项命名、上下文优先级、帮助文本和错误结构一致，并覆盖成功、HTTP 错误、无效输入与缺失上下文。
- 文件写入、skill 安装和卸载必须限制在用户明确指定或已解析的目标目录；删除前解析并验证精确路径，不递归删除未知目录，不影响非本项目管理的 skill。
- 网络请求必须有明确超时、可定位的错误和受控的响应解析；不要静默重试非幂等请求，不在错误信息中输出凭据、私有正文或完整敏感响应。

## Python 与实现规则

- 使用 Python 3.12+ 类型语法，以 `T | None` 和内建泛型代替旧式 typing 别名。
- 核心命令和上下文解析不使用 `Any`、动态属性探测、无类型 duck typing、monkey patch 或无说明的 `type: ignore`；第三方边界以 `Protocol`、`TypedDict`、dataclass、Pydantic-free 的明确解析函数或显式 `cast` 隔离。
- 命令层保持薄：负责参数、上下文、输出和退出语义；可测试的请求构造、文件操作与转换逻辑放在职责明确的模块中。不要为单次直线调用额外制造抽象层。
- 不捕获宽泛异常并转成笼统成功或空结果。只在 CLI、HTTP、JSON、文件系统和子进程边界转换已知异常，并保留可行动信息。
- 修改 bundled Skills 时保持 `SKILL.md`、references、实际 CLI `--help` 与 backend 契约一致；不要记录不存在的命令、参数或能力。

## 测试与交付

- 命令行为使用 `CliRunner` 或现有测试工具验证 stdout、stderr、exit code 和请求参数；HTTP、文件系统和上下文路径使用确定性 fake / `tmp_path`，不得访问真实服务或用户配置。
- 缺陷修复添加回归测试；公共命令、JSON 字段或错误语义变化视为兼容性变更，必须明确检查现有 Skills、脚本调用者和文档。
- 小改动至少运行相关 `just test ...`、`just lint` 和 `just typecheck`；格式变化运行 `just format-check`；entry point、资源打包或依赖变化运行 `just build` 并检查构建产物内容。高风险改动运行 `just pre-commit`。
- 不手改 `dist/`、缓存和已生成产物。锁文件只由 uv 更新。不得声称未运行的验证已通过；失败需报告命令、失败项和与本次改动的关系。
- Markdown 无新段落时不因行宽机械换行；涉及检索语法、排序或其他非直观算法时，在代码注释中解释假设，并在相应 Skill reference 或项目文档中记录可审查的规则与限制。
