# DeepWiki MCP 调用指南

## 当前状态

**✅ DeepWiki MCP 可正常访问**
- URL: `https://mcp.deepwiki.com/mcp`
- 协议版本: 2024-11-05
- 服务版本: 2.14.3

## 调用方式

### Python 实现（已验证可用）

```python
import json
import urllib.request
import ssl

DEEPWIKI_URL = "https://mcp.deepwiki.com/mcp"

def send_mcp_request(method: str, params: dict):
    """发送 MCP 请求并解析 SSE 响应"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    data = json.dumps(payload).encode('utf-8')
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        DEEPWIKI_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json"
        }
    )
    
    with urllib.request.urlopen(req, data=data, timeout=120, context=context) as response:
        content = response.read().decode('utf-8')
        return parse_sse_response(content)


def parse_sse_response(content: str):
    """解析 SSE 响应"""
    results = []
    for line in content.split('\n'):
        if line.startswith('data: '):
            data = line[6:]
            if data == '[DONE]':
                break
            try:
                chunk = json.loads(data)
                if 'result' in chunk:
                    results.append(chunk['result'])
            except json.JSONDecodeError:
                pass
    return results


# 使用示例
topics = send_mcp_request("tools/call", {
    "name": "read_wiki_structure",
    "arguments": {"repoName": "owner/repo"}
})

content = send_mcp_request("tools/call", {
    "name": "read_wiki_contents",
    "arguments": {"repoName": "owner/repo"}
})

answer = send_mcp_request("tools/call", {
    "name": "ask_question",
    "arguments": {"repoName": "owner/repo", "question": "这个项目的核心功能是什么？"}
})
```

## 可用工具

| 工具 | 说明 | 返回 |
|------|------|------|
| `read_wiki_structure` | 获取文档结构 | 章节列表 |
| `read_wiki_contents` | 获取完整文档 | Markdown 内容 |
| `ask_question` | 向仓库提问 | AI 回答 |

## 输出示例

### 文档结构
```json
[
  {
    "content": "Available pages for owner/repo:\n\n- 1 Overview\n  - 1.1 Key Concepts\n  - 1.2 Quick Start\n- 2 Installation\n..."
  }
]
```

### 文档内容
```markdown
# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

- README.md
- package.json
...
</details>

## 项目概述
...
```

## 重要提示

1. **必须使用 SSE 解析**：服务器返回 SSE 流，需要解析 `data:` 行
2. **处理 `[DONE]` 终止符**：收到后停止解析
3. **SSL 验证**：生产环境需要正确处理证书
4. **超时设置**：建议 120 秒以上，文档可能较大
5. **保存到 workspace**：每次调用后保存结果供 AI 参考
