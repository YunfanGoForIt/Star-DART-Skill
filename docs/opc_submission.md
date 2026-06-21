# Star-DART OPC 项目说明文档

## 作品名称

Star-DART OPC：办公小浣熊驱动的开源项目情报与知识资产工作台

## 300 字作品简介

Star-DART OPC 是一个由办公小浣熊驱动的开源项目情报与知识资产工作台。开发者和 AI 工具重度用户常常在 GitHub 上 Star 大量项目，但真正需要时却找不到、想不起、懒得重新阅读 README，收藏难以转化为可复用能力。Star-DART OPC 将 GitHub Star 作为触发入口，采用默认 3 小时定时轮询发现新增仓库，用户可自行调整轮询间隔；随后结合办公小浣熊本地 Agent、Skill、专家团、文档处理、表格分析、数据看板、PPT 生成、知识库和定时任务能力，自动完成项目资料读取、价值研判、结构化档案生成、资产台账更新、可视化看板构建和每周开源情报简报输出。它不是一次性问答工具，而是一套持续运行的个人知识生产流程：一个人即可完成原本需要研究员、文档编辑、数据分析师、PPT 设计师和知识库运营共同完成的工作，让 GitHub Star 从“收藏夹”变成可检索、可汇报、可沉淀、可复用的开源知识资产。

## 真实问题

GitHub Star 是开发者最常用的“以后可能用得上”收藏方式，但它有三个明显问题：

1. 收藏之后很快遗忘，不记得当时为什么 Star。
2. 真正需要时只能靠关键词翻找，找回成本高。
3. 找到项目后还要重新读 README、文档、Issue 和示例，重复理解成本高。

这个问题不是个人懒惰，而是 AI 时代信息过载下的知识资产运营问题。Star-DART OPC 的目标是把“收藏链接”变成“能被未来复用的结构化知识”。

## 解决方案

Star-DART OPC 采用“定时轮询 + 办公小浣熊工作流”的方案：

1. Star-DART poller 默认每 3 小时轮询 GitHub Star API。
2. 发现新增仓库后生成标准任务说明。
3. 办公小浣熊本地 Agent 接收任务，并读取 README、DeepWiki、Release、Issue 等资料。
4. `research-synthesis` 或行业研究报告专家团完成项目理解、价值判断和风险识别。
5. `docx/pdf` 输出结构化项目档案。
6. `xlsx` 更新开源项目资产台账。
7. `data-dashboard` 生成分类、趋势、复用等级和推荐项目看板。
8. `pptx` 或创意 PPT 专家团生成技术雷达汇报。
9. 云上知识库、本地文件索引、飞书或 Obsidian 持续沉淀资料。
10. 定时任务每周生成开源情报简报。

## 为什么是办公小浣熊核心能力

本作品不是简单调用单个聊天功能，而是组合使用办公小浣熊的完整能力：

| 办公小浣熊能力 | 在作品中的作用 |
|---|---|
| 本地 Agent | 执行 Star-DART 任务，读取本地材料和样例 |
| Skill | 固化开源项目沉淀流程 |
| 专家团 | 模拟研究员、数据分析师、PPT 设计师协作 |
| research-synthesis | 对项目定位、价值、风险和边界进行结构化研判 |
| docx/pdf | 生成项目档案和提交说明文档 |
| xlsx | 维护项目资产台账 |
| data-dashboard | 展示分类分布、复用等级和推荐项目 |
| pptx | 生成技术雷达或参赛汇报 |
| writing-workflow | 生成周报、推荐理由、社群分享文案 |
| 云上知识库 | 存储项目档案和周期简报 |
| 本地文件索引 | 让本地项目资料可被引用 |
| 飞书 / Obsidian 数据源 | 接入已有协作知识库 |
| 定时任务 | 每周输出开源情报简报 |

## 工作流 Demo

### Demo 1：新增 Star 自动沉淀

命令：

```bash
python scripts/webhook_poller.py --dry-run --once --sample examples/sample_starred_repo.json
```

说明：

- 不依赖 GitHub Token、飞书 Token 或外部服务。
- 模拟发现一个新增 Star。
- 输出办公小浣熊任务说明。
- 展示该任务应如何进入研究、文档、表格、看板和 PPT 链路。

### Demo 2：项目资产台账

查看：

```bash
examples/sample_asset_table.csv
```

展示字段：

- 仓库名
- 一级分类
- 详细标签
- 语言
- Star 数
- 复用等级
- 推荐理由
- 适用场景
- 最后更新时间

### Demo 3：开源情报周报

查看：

```bash
examples/sample_weekly_brief.md
```

展示每周新增项目、重点方向、最值得研究项目和下周行动。

## 项目成果

当前已准备：

- `examples/sample_starred_repo.json`：GitHub Star 输入样例。
- `examples/sample_agent_payload.md`：办公小浣熊任务说明样例。
- `examples/sample_project_profile.md`：结构化项目档案样例。
- `examples/sample_asset_table.csv`：开源项目资产台账样例。
- `examples/sample_dashboard_data.json`：看板数据样例。
- `examples/sample_weekly_brief.md`：每周开源情报简报样例。
- `examples/sample_ppt_outline.md`：汇报 PPT 大纲样例。
- `docs/office_raccoon_workflow.md`：办公小浣熊能力链路说明。
- `docs/scoring_alignment.md`：评分维度对齐说明。
- `docs/ppt_outline.md`：参赛 PPT 结构。

## 成效预估

| 指标 | 原流程 | Star-DART OPC |
|---|---|---|
| 单个项目初步理解 | 20-40 分钟 | 3-5 分钟人工复核 |
| 项目找回方式 | GitHub 搜索 / 记忆 | 标签、场景、台账、知识库 |
| 输出形式 | 链接或零散笔记 | 文档、表格、看板、PPT、周报 |
| 周期沉淀 | 依赖人工自觉 | 定时任务自动触发 |
| 团队复用 | 难共享 | 可放入飞书 / Obsidian / 云上知识库 |

## 边界与风险

1. GitHub Star 没有稳定的个人 webhook 入口，因此采用定时轮询，默认 3 小时。
2. 高质量项目研判仍需人工复核，尤其是安全、许可证和商业使用边界。
3. 私有仓库和受限资料需要用户自行配置权限。
4. 参赛演示使用 dry-run 保证稳定，真实运行需要配置 GitHub Token、Agent 服务和知识库权限。

## 可扩展场景

- 论文收藏沉淀为研究库。
- AI 工具收藏沉淀为工具雷达。
- 竞品资料沉淀为产品情报库。
- 课程资料沉淀为学习路径。
- 团队 Star 汇总沉淀为技术选型资产。

