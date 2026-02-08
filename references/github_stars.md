# GitHub Stars API

## 获取星标仓库

```python
from github_stars import GitHubMonitor

monitor = GitHubMonitor(token)

# 最近 10 个
stars = await monitor.fetch_recent_stars(limit=10)

# 所有（自动分页）
all_stars = await monitor.fetch_all_stars()
```

## 返回数据

```python
{
    "id": 123456,
    "full_name": "owner/repo",
    "description": "项目描述",
    "html_url": "https://github.com/owner/repo",
    "language": "Python",
    "stargazers_count": 1000
}
```

## Token 配置

在 `.env` 中设置：
```bash
GITHUB_TOKEN=ghp_xxx
```
