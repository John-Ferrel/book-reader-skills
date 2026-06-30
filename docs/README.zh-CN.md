# Book Reader Skills v2 中文说明

Book Reader Skills 是给 agent 用的、可审计的整书阅读工作流。它的目标不是快速给一本书写摘要，而是把阅读过程组织成一个可以追踪证据、复查推理、修订结论的 reconstruction workspace。

## 它是什么

Book Reader 把阅读拆成几个可检查的环节：

```text
source evidence -> claim cards / note items -> reconstruction model -> independent review -> revision -> verification review
```

也就是说，agent 先准备 source evidence，再写 note items / claim cards，然后重建作者问题、概念系统、论证结构或书的设计。之后还要做独立 review、按 review plan 修订，再做 verification review。

默认产物是一个 evidence-linked workspace，不是聊天窗口里的一段总结。

## 它不是什么

- 不是普通 summary 工具。
- 不是把一本书转换成 reusable skill 的工具。
- 不是 RAG ingestion pipeline。
- 不是只靠 Python 脚本自动理解一本书的系统。

Python runtime 只做机械工作：抽取、规范化、建 source map、生成 workspace skeleton 和结构验证。真正的语义阅读由 agent 通过 skills、references、templates 和判断完成。

## 适合谁

适合想让 agent 深读一本书，并且希望过程可检查的人：

- 想保留 source block 到 note item 再到 model inference 的证据链。
- 想区分“作者原文支持的结论”和“agent 的推断”。
- 想让另一个 review pass 查推理漏洞、偷懒总结、空洞模型文件。
- 想把读书工作持续推进，而不是一次性生成摘要。

如果你只想要一段很短的内容摘要，这个项目会显得偏重。

## 最小安装

```bash
git clone https://github.com/John-Ferrel/book-reader-skills.git
cd book-reader-skills

python3 -m venv .venv
. .venv/bin/activate
pip install -e .

python3 -m unittest tests/test_helpers.py -v
python3 -m py_compile scripts/install_skills.py skills/book-intake/scripts/*.py
```

安装到 OpenCode 全局 skills 目录：

```bash
python3 scripts/install_skills.py --target opencode-global
```

安装到某个 OpenCode 项目：

```bash
python3 scripts/install_skills.py --target opencode-project --project /path/to/project
```

安装后请新开或重启 OpenCode session。文件出现在 `.opencode/skills/` 只说明复制成功；真正可用要看 OpenCode native `available_skills` 里是否出现 `book-reader`、`book-intake`、`technical-book` 等 skill。

## 最小使用示例

在 OpenCode 中可以这样要求 agent：

```text
Use book-reader to read examples/sample-nonfiction.txt.
```

也可以只让 agent 先做 intake：

```text
Use book-intake to ingest examples/sample-nonfiction.txt into a source-ready workspace.
```

正常完整阅读会经过：

```text
book-intake -> book-reconstruct -> book-reviewer -> book-revise -> book-reviewer verification
```

不同类型的书可以加 lens，例如 `technical-book`、`fiction-narrative`、`nonfiction-argument`、`source-limited`。

## 更新方式

已经 clone 过仓库时：

```bash
git pull
. .venv/bin/activate
pip install -e .
```

覆盖更新 OpenCode 全局安装：

```bash
python3 scripts/install_skills.py --target opencode-global --force
```

覆盖更新某个 OpenCode 项目安装：

```bash
python3 scripts/install_skills.py --target opencode-project --project /path/to/project --force
```

更新 skills 后，已有 workspace 不会自动重跑。需要你明确让 agent 重新执行相关 workflow，例如重新 intake、reconstruct、review、revise 或 verification review。

## 当前 beta 限制

- Intake 支持 `.txt`、`.md`、`.epub` 和 text-based `.pdf`，不支持 OCR。
- PDF 版式、图片、表格可能丢失或退化。
- EPUB 图片、样式、部分注释可能被 flatten。
- Python validator 只检查机械结构，不判断阅读质量。
- Reviewer 默认只写 review 输出，不自动修复 workspace。
- 这个项目依赖 agent 认真执行 evidence discipline；它不是一键自动读懂整本书的程序。
