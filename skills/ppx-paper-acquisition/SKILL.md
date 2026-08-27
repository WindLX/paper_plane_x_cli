---
name: ppx-paper-acquisition
description: 使用 InstSci 或可控浏览器获取原始论文 PDF，并通过 ppx CLI 将本地单篇 PDF 上传到 Paper Plane X；适用于 DOI、出版商页面、主题检索结果或用户指定论文的入盘任务。
---

# Paper Plane X 论文获取与入盘

本 Skill 只编排外部检索、合法 PDF 获取和 PPX 上传。Paper Plane X Backend 不负责访问出版商网页，也不保存学校登录状态。

## 路由

- 已知 DOI、出版商页面或明确论文时，优先使用 InstSci。闭源论文必须使用可见 CloakBrowser 流程，并遵守 InstSci 的机构身份与证据规则。
- 用户只有研究主题，或目标是公开网页、OA 论文时，使用 Browser 检索并获取公开 PDF；找到明确 DOI 或闭源出版商后可转交 InstSci。
- 不把 HTTP 预检、历史 publisher matrix 或页面上出现 PDF 按钮视为下载成功。上传前必须确认本地文件存在且确为 PDF。

## 上传

先检查 PPX 上下文：

```bash
ppx context show
```

用户要求关联项目时，使用已有 `project_id`，或按用户明确提供的 ID 设置/传入上下文。CLI 会依次执行论文上传与项目关联两个操作；没有项目时只上传到全局文献库。关联失败时明确说明 Paper 可能已经上传，不要把两步误报为原子操作。

默认只上传 PDF：

```bash
ppx paper upload --source /absolute/path/paper.pdf
```

不要从文件名、搜索摘要或网页片段猜测标题、作者、年份、刊物或 DOI。只有用户明确提供，或可信结构化来源已经确认时，才使用 `--title`、重复的 `--author`、`--year`、`--publication` 或 `--doi`。Zotero 可以在后续流程中获取并回写元数据。

## 安全边界

- 不读取、代填、记录或转发密码、OTP、CAPTCHA、cookie、浏览器 profile 或学校凭据。
- 需要登录时让用户在可见浏览器窗口中完成；不得绕过出版商访问控制。
- 不把受限 PDF、身份信息或临时下载目录加入 Git。
- 获取失败时报告实际路由和阻塞原因，不用其他论文替代用户指定目标。

## 结果汇报

逐篇报告来源、DOI或标识符、获取路线、本地 PDF 路径、`paper_id`、`task_id`、`project_id`、上传状态和下一步。CLI 返回非零退出码或错误 JSON 时，视为未入盘成功。
