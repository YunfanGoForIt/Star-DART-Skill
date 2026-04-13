# GitHub Stars API

## 获取星标仓库

实际调用的是 GitHub REST API `GET /user/starred`。

### API 端点

```
GET https://api.github.com/user/starred
```

### 请求头

```python
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "token {GITHUB_TOKEN}"
}
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `per_page` | int | 每页数量（最大 100） |
| `page` | int | 页码 |
| `sort` | string | `created`（按星标时间）或 `updated`（按更新时间） |
| `direction` | string | `asc` 或 `desc` |

### 返回数据

```python
[
  {
    "id": 123456,
    "full_name": "owner/repo",
    "description": "项目描述",
    "html_url": "https://github.com/owner/repo",
    "language": "Python",
    "stargazers_count": 1000,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-06-01T00:00:00Z"
  },
  ...
]
```

### 实际代码（webhook_poller.py）

```python
class GitHubMonitor:
    def __init__(self, token: str):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        }
        self.api_url = "https://api.github.com/user/starred"

    async def fetch_recent_stars(self, limit: int = 30):
        """获取最近 star 的仓库"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.api_url,
                headers=self.headers,
                params={"per_page": limit, "sort": "created", "direction": "desc"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def fetch_all_stars(self):
        """获取所有 star 的仓库（分页）"""
        all_stars = []
        page = 1
        per_page = 100

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    self.api_url,
                    headers=self.headers,
                    params={"per_page": per_page, "page": page, "sort": "created", "direction": "desc"},
                    timeout=30.0
                )
                response.raise_for_status()
                stars = response.json()
                if not stars:
                    break
                all_stars.extend(stars)
                if len(stars) < per_page:
                    break
                page += 1
                await asyncio.sleep(1)  # 避免 API 限流
        return all_stars
```

### 调试技巧

**手动测试 API**：
```bash
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     "https://api.github.com/user/starred?per_page=5&sort=created&direction=desc"
```

**常见错误**：
- `401 Unauthorized` — Token 无效或过期
- `403 Forbidden` — Token 缺少 `starring:read` 权限
- `422 Unprocessable Entity` — 参数错误

**API 限流**：
- 未认证：60 请求/小时
- 已认证：5000 请求/小时
- 代码中有 1 秒间隔避免触发限流
