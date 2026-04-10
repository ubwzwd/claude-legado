# claude-legado

在终端里阅读小说 —— 完美伪装成 Claude AI 的输出。

[English Version](README_EN.md)

`claude-legado` 会精准模拟 LLM 的 Token 生成过程，以字符为单位流式输出小说内容，并带有随机延迟。从外观上看，就像是 Claude 正在“思考”并回答你的问题。它支持使用 [Legado (阅读)](https://github.com/gedoor/legado) 的书源 JSON 文件，让你能够访问数以千计的社区维护书源。

## 功能特性

- **Claude 完美伪装** — 输出流带有虚假的“思考中...”前缀、真实的打字延迟、脉冲式突发输出以及标点符号停顿，视觉效果与真实的 AI 生成文本完全一致。
- **兼容 Legado 书源引擎** — 支持 Legado 书源中的 CSS、JSONPath、XPath、JS 以及正则表达式规则。
- **完整阅读流程** — 搜索 → 添加到书架 → 浏览目录 → 通过 `/novel next` 和 `/novel prev` 自由阅读。
- **进度追踪** — 自动记录每本书的阅读位置。书架显示章节总数，目录会高亮当前正在阅读的章节。
- **优雅的错误处理** — 所有网络或解析错误都会以 Claude 经典的斜体“思考”风格打印，绝不泄露 Python 堆栈追踪。

## 环境要求

- Python 3.12+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (用于 `/novel` 斜杠命令集成)

## 安装设置

```bash
# 克隆仓库
git clone <repo-url> && cd claude_legado

# 创建虚拟环境并安装
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

该项目会自动通过 `.claude/commands/` 注册一系列 Claude Code 斜杠命令。安装完成后，你可以在 Claude Code 会话中直接使用 `/novel-search` 和 `/novel-shelf` 等命令。

## 快速上手

### 1. 添加/加载书源

你可以直接导入 Legado 格式的书源 JSON：

```
/novel-add-source https://example.com/source.json
```

或者直接粘贴 JSON 内容。该命令会自动存储并激活该书源。你可以通过 `/novel-sources` 查看所有已管理书源。

### 2. 搜索小说

```
/novel-search 斗破苍穹
```

### 3. 添加到书架

```
/novel-add 1
```

### 4. 选择书籍阅读

```
/novel-read 1
```

### 5. 浏览目录

```
/novel-toc
```

当前章节会以 `->` 标记。

### 6. 开始阅读

```
/novel          # 阅读当前章节
/novel next     # 下一章
/novel prev     # 上一章
```

内容将以 Claude 风格的延迟和“思考”前缀流式输出。

## 其他命令

| 命令 | 描述 |
|---------|-------------|
| `/novel-shelf` | 列出书架上的书籍及阅读进度 |
| `/novel-info` | 显示当前书籍的详细信息 |
| `/novel-toc <page>` | 显示目录的特定页面 |
| `/novel-sources` | 列出所有已管理的基础书源 |
| `/novel-use <index>` | 通过索引切换当前激活的书源 |

## 工作原理

1. **规则引擎** — 书源文件定义了提取书籍列表、章节 URL 和内容的规则（CSS 选择器、JSONPath、XPath、JS 脚本或正则）。
2. **HTTP 传输** — 根据书源配置发送带自定义 Header/Cookie 的请求，并自动检测 GBK 编码转换为 UTF-8。
3. **渲染引擎** — 以字符为单位流式输出，带有随机延迟（基础 15–40ms，短句停顿 60ms，句末停顿 150ms）以及 8–15 字符的突发块。
4. **状态持久化** — 阅读进度存于 `~/.claude-legado/state.json`，书架存于 `shelf.json`，书源存于 `sources/`。

## 脱离 Claude Code 运行

你也可以在标准终端里直接运行：

```bash
PYTHONPATH=src python3 -m novel novel-sources
PYTHONPATH=src python3 -m novel novel-search "书名"
PYTHONPATH=src python3 -m novel
```

## 开源协议

MIT
