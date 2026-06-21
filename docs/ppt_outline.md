# Star-DART OPC 参赛 PPT 大纲

## 1. 封面

标题：Star-DART OPC  
副标题：办公小浣熊驱动的开源项目情报与知识资产工作台

## 2. 痛点：Star 很多，复用很少

- 收藏时觉得有用。
- 真正需要时找不到。
- 找到后还要重新理解。
- 团队无法共享个人收藏中的判断。

## 3. OPC 场景：一个人完成一支团队的工作

原本需要：

- 研究员读项目。
- 文档编辑写档案。
- 数据分析师维护台账。
- PPT 设计师做汇报。
- 知识库运营做沉淀和周报。

现在由一个人使用办公小浣熊完成。

## 4. 方案总览

GitHub Star 定时轮询 -> 办公小浣熊本地 Agent -> 项目研判 -> 文档/表格/看板/PPT -> 知识库 -> 定时周报。

## 5. 为什么是定时轮询

- 默认每 3 小时检查新增 Star。
- 用户可通过 `POLL_INTERVAL` 调整。
- GitHub 个人 Star 更适合 API 轮询。
- 办公小浣熊负责后续完整办公交付。

## 6. 办公小浣熊能力地图

展示：

- 本地 Agent
- Skill
- 专家团
- research-synthesis
- docx/pdf/xlsx/pptx
- data-dashboard
- 云上知识库
- 本地文件索引
- 飞书 / Obsidian
- 定时任务

## 7. Demo 1：新增 Star 自动沉淀

运行：

```bash
python scripts/webhook_poller.py --dry-run --once --sample examples/sample_starred_repo.json
```

展示任务说明如何进入办公小浣熊工作流。

## 8. Demo 2：项目档案

展示 `examples/sample_project_profile.md`。

## 9. Demo 3：资产台账和看板

展示：

- `examples/sample_asset_table.csv`
- `examples/sample_dashboard_data.json`

## 10. Demo 4：每周开源情报简报

展示 `examples/sample_weekly_brief.md`，说明定时任务如何持续输出。

## 11. 成效

- 单项目整理从 20-40 分钟降至 3-5 分钟人工复核。
- Star 从链接变成知识档案。
- 支持团队共享和技术选型。

## 12. 扩展

- 论文库
- AI 工具库
- 竞品库
- 课程资料库
- 团队技术雷达

## 13. 总结

Star-DART OPC 的核心不是收藏，而是把收藏变成能力；不是单点使用 AI，而是用办公小浣熊完成完整办公交付。

