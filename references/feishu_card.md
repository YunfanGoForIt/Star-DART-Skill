# 飞书卡片消息格式

## 交互卡片（Interactive Card）

飞书支持使用交互卡片发送富文本消息，格式为 JSON。

### 卡片结构

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "GitHub 仓库文档已生成"
      },
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "fields": [
          {
            "is_short": true,
            "text": {
              "tag": "lark_md",
              "content": "**仓库**\nowner/repo-name"
            }
          },
          {
            "is_short": true,
            "text": {
              "tag": "lark_md",
              "content": "**分类**\nAI智能体框架"
            }
          }
        ]
      },
      {
        "tag": "hr"
      },
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**一句话简介**\n项目描述内容..."
        }
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "查看文档"
            },
            "type": "primary",
            "url": "https://feishu.cn/docx/xxx"
          }
        ]
      }
    ]
  }
}
```

### 常用标签

| 标签 | 说明 |
|------|------|
| `div` | 文本块 |
| `hr` | 分隔线 |
| `plain_text` | 纯文本 |
| `lark_md` | 飞书 Markdown |
| `action` | 操作区域 |
| `button` | 按钮 |

### 颜色模板

`header.template` 可选：`blue`, `red`, `yellow`, `green`, `purple`, `orange`, `grey`

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `header.title.content` | string | 卡片标题 |
| `header.template` | string | 主题色 |
| `elements[].tag` | string | 元素类型 |
| `elements[].fields` | array | 字段列表（is_short=true 并排显示） |
| `actions[].url` | string | 点击跳转链接 |

### 发送示例

```bash
lark-cli im +messages-send \
  --chat-id "$FEISHU_CHANNEL_ID" \
  --msg-type interactive \
  --content '{"msg_type":"interactive","card":{"header":{"title":{"tag":"plain_text","content":"GitHub 仓库文档已生成"},"template":"blue"},"elements":[{"tag":"div","fields":[{"is_short":true,"text":{"tag":"lark_md","content":"**仓库**\nowner/repo"}},{"is_short":true,"text":{"tag":"lark_md","content":"**分类**\nAI智能体框架"}}]},{"tag":"hr"},{"tag":"div","text":{"tag":"lark_md","content":"**简介**\n项目描述"}},{"tag":"action","actions":[{"tag":"button","text":{"tag":"plain_text","content":"查看文档"},"type":"primary","url":"https://feishu.cn/docx/xxx"}]}]}}'
```
