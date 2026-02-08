---
name: autodoc-gh-wiki
description: 自动将 GitHub Star仓库转换为高质量中文文档。输入 GitHub 仓库 URL 或 owner/repo 格式，自动获取 DeepWiki 文档和README文档、生成精炼的中文文档并保存到 Obsidian。使用场景："帮我把 https://github.com/owner/repo 转换成中文文档"、"翻译这个 GitHub 项目"。
---

# GitHub 仓库中文文档生成器

## 核心流程

```
获取文档 → 生成初稿 → 补充完善 → 保存输出 → Discord 通知
```

## 强制执行

**生成文档前必须查看**：
- `references/doc_template.md` - 文档结构模板
- `references/deepwiki_mcp.md` - DeepWiki 调用方式（含可工作代码）

## 两阶段工作流程

### 阶段一：生成初稿

**必须读取以下文件**：
1. `{WORK_DIR}/overview.md` - DeepWiki 生成的概述文档
2. `{WORK_DIR}/README.md` - GitHub README 文件

**生成文件**：
- `title.txt` - 中文标题（10字以内）
- `draft.md` - 中文草稿

**初稿要求**：
- 保留技术术语（变量名、函数名、类名）为英文
- 移除冗余的源文件引用列表
- 重点突出架构设计和核心功能

### 阶段二：补充完善

**检查并补充**：
1. 运行 `ls {WORK_DIR}/docs/` 查看所有文档
2. 选择性阅读相关文档补充草稿中的不足
3. 添加缺失的重要细节
4. 修正不准确的技术描述

**输出**：
- `final.md` - 最终文档

## 输出要求

**文档结构**（见 `doc_template.md`）：
- 项目简介（开头一段话）
- 核心特性/亮点
- 架构设计
- 技术亮点
- 使用方式（如适用）
- 关键概念解释

## 分类框架

```
GitWiki/
├── AI智能体框架/
│   ├── 多智能体/
│   ├── 单智能体/
│   └── 编程智能体/
├── 深度研究/
│   ├── 智能体研究/
│   └── 论文分析/
├── 学术论文/
├── 视频媒体/
├── 开发相关/
│   ├── 微信小程序/
│   ├── 安卓开发/
│   └── 网页开发/
├── 知识管理/
├── 学习教程/
├── 效率工具/
├── 桌面应用/
├── 生物医学/
└── 其他/
```

## 输出路径

- **Obsidian**: `{ObsidianVault}/GitWiki/{分类}/{repo}_{标题}.md`
- **Syncthing**: `{SyncthingDir}/{分类}/{repo}_{标题}.md`

## 飞书群聊通知

```
✅ 文档生成成功

仓库: owner/repo
分类: AI智能体框架/多智能体
标题: 项目标题
文件路径: GitWiki/AI智能体框架/多智能体/owner_repo_项目标题.md
```

### 频道配置

通过环境变量配置飞书群聊通知：

- `FEISHU_CHANNEL_ID`：飞书群聊 ID（可选，不填则不发送通知）

## 环境配置

| 变量 | 说明 |
|------|------|
| `GITHUB_TOKEN` | GitHub API Token |
| `OBSIDIAN_VAULT_PATH` | Obsidian 仓库路径 |
| `SYNCTHING_DIR` | Syncthing 同步目录（可选） |
| `DEEPWIKI_BASE_URL` | DeepWiki MCP URL（默认 https://mcp.deepwiki.com/mcp） |

## DeepWiki MCP 调用示例

```python
import json
import urllib.request
import ssl

DEEPWIKI_URL = "https://mcp.deepwiki.com/mcp"

def get_overview(repo_name: str) -> str:
    """获取 Overview 文档"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "read_wiki_contents",
            "arguments": {"repoName": repo_name}
        }
    }
    data = json.dumps(payload).encode('utf-8')
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(DEEPWIKI_URL, data=data, headers={
        "Content-Type": "application/json",
        "Accept": "text/event-stream, application/json"
    })

    with urllib.request.urlopen(req, data=data, timeout=120, context=context) as response:
        content = response.read().decode('utf-8')
        # 解析 SSE 响应，提取 result.content[0].text
        return parse_sse_response(content)
```

## 关键提示

1. **先 overview + README 生成初稿**，再查看详细文档补充
2. **必须用 Write 工具写文件**，不能只在回复中显示
3. **必须生成 title.txt**，用于最终文件名
4. **分类基于星标仓库分析**，用户有 11 个分类偏好
