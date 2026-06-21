---
name: star-dart
description: 将 GitHub Star 仓库列表转化为可检索、可复用的个人知识库。自动生成中文文档并保存到飞书知识库，配合多维表格索引，让"收藏"变成"真正掌握"。使用场景："我刚 Star 了这个项目，帮我生成文档放入知识库"、"我 Star 的 AI 项目有哪些"。
---

# Star-DART Skill

## 核心理念

**Star 不等于掌握。** 我们 Star 大量开源项目，当下觉得"以后用得上"，过段时间只剩模糊记忆。真正需要时，翻遍 Star 列表也找不到，或者找到了也懒得重新看一遍。

本 Skill 的目标：**把"看过"变成"能用"。**

```
你 Star 了一个项目 → 默认 3 小时定时轮询发现 → 自动生成中文文档 → 保存到飞书知识库 → 多维表格索引
                                              ↓
                              未来需要时：搜索关键词 或 浏览分类
                                         快速找到、立刻复用
```

## 工作流程

```
定时轮询 → 获取文档 → 生成初稿 → 补充完善 → 保存文档 → 创建索引记录 → 发送通知
```

默认轮询间隔为 10800 秒（3 小时），用户可通过 `POLL_INTERVAL` 调整。

---

## 第一步：获取素材

**必须读取以下文件**：
- `{WORK_DIR}/overview.md` — DeepWiki 生成的项目概述
- `{WORK_DIR}/README.md` — GitHub README 原文档
- `references/tags.md` — 11 个一级分类
- `references/tags.json` — 每个分类下的详细标签

**DeepWiki 调用方式**：
```python
# 见 references/deepwiki_mcp.md
```

---

## 第二步：生成文档

### 2.1 生成初稿
Star-DART文档的核心不是一个README，它的价值在于把“看过”变成“能用”：你不必每次都从零理解项目，也不必依赖记忆去找回收藏。文档产出具备统一结构（定位、亮点、架构、快速开始、边界等），未来只要搜索关键词或按分类浏览，就能快速回到当初的判断与用法。

必须先读取 `references/doc_template.md` 了解文档结构要求。

**生成文件**：
- `title.txt` — 中文标题（10 字以内）
- `draft.md` — 中文草稿

**要求**：
- 保留技术术语（变量名、函数名、类名）为英文
- 重点突出架构设计和核心功能及亮点
- 不是翻译，是提炼
- 在`overview.md`和`README.md`中尚不明确的重要细节，不要猜测，留下占位符，交由下一阶段补充。

### 2.2 补充完善

1. `ls {WORK_DIR}/docs/` 查看所有文档
2. 选择性阅读，补充草稿中的不明确的部分。
3. 添加缺失细节，修正错误

**输出**：`final.md`

---

## 第三步：保存到飞书知识库

**文档标题格式**：`{中文标题} - {owner}/{repo}`

```bash
# 1. 创建知识库节点
lark-cli wiki +node-create \
  --space-id "$FEISHU_WIKI_SPACE_ID" \
  --title "{中文标题} - {owner}/{repo}" \
  --as user

# 2. 写入文档内容
lark-cli docs +update \
  --wiki-node "{node_token}" \
  --markdown "$(cat {WORK_DIR}/final.md)"
```

---

## 第四步：创建多维表格索引

```bash
lark-cli base +record-create \
  --base-token "$FEISHU_BASE_TOKEN" \
  --table-id "$FEISHU_TABLE_ID" \
  --json '{
    "fields": {
      "仓库名": "{owner}/{repo}",
      "一段话简介": "{一句话描述}",
      "飞书文档链接": "{飞书文档链接}",
      "一级分类": "{从 tags.md 选取}",
      "详细标签": "{从 tags.json 选取，有新内容则创建新标签}"
    }
  }'
```

**分类和标签**：
- 优先使用 `tags.json` 中已有的标签
- 有新内容时大胆创建新标签
- 相同语义的内容使用相同标签

---

## 第五步：发送通知

文档整理完成后，向用户发送飞书交互卡片通知：
**卡片格式模板**（详细格式见 `references/feishu_card.md`）：

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": { "tag": "plain_text", "content": "📚 文档已生成" },
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "fields": [
          { "is_short": true, "text": { "tag": "lark_md", "content": "**仓库**\n{owner}/{repo}" } },
          { "is_short": true, "text": { "tag": "lark_md", "content": "**分类**\n{一级分类}" } }
        ]
      },
      { "tag": "hr" },
      {
        "tag": "div",
        "text": { "tag": "lark_md", "content": "**简介**\n{一句话描述}" }
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": { "tag": "plain_text", "content": "查看文档" },
            "type": "primary",
            "url": "{飞书文档链接}"
          }
        ]
      }
    ]
  }
}
```

通知由 OpenClaw Agent 发送，Agent 应将上述 JSON 作为消息内容发送。

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `GITHUB_TOKEN` | GitHub API Token |
| `FEISHU_WIKI_SPACE_ID` | 飞书知识库 Space ID |
| `FEISHU_BASE_TOKEN` | 飞书多维表格 Token |
| `FEISHU_TABLE_ID` | 飞书多维表格 Table ID |
| `FEISHU_CHANNEL_ID` | 飞书群聊 ID（可选） |

---

## 关键提示

1. **不是翻译，是提炼** — 重点是为什么值得用，不是罗列功能
2. **文档标题要清晰** — `{中文标题} - {owner}/{repo}`，便于搜索
3. **标签要一致** — 参考 `tags.json`，避免重复标签
4. **多维表格是索引** — 通过它快速找到项目，再跳转查看完整文档
