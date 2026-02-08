# Autodoc-GitHub-StarRepo-Skill
** 主动触发，现在看懂，未来找回，随时可用。让你的Star列表成为你的独家知识库**

# Skill介绍

 Star 了大量开源项目，当下觉得“以后一定用得上”，但过一段时间真正需要时，却只剩一句模糊记忆：好像有个库能做这个。再加上社交媒体介绍往往只讲结论不讲细节，自己从 README、文档到源码完整读一遍又太耗时间，结果就是收藏越来越多、可复用的理解越来越少。

Autodoc-GitHub-StarRepo-Skill 的目标，是把“新增 Star”自动变成一条可检索、可回看、可复用的知识记录：一旦你 Star 了新仓库，它会主动触发 OpenClaw 的 webhook，让后续的“精读与归档”流程自动跑起来，而不是等你哪天想起再去翻历史记录。

工作原理很直接：`scripts/webhook_poller.py` 读取仓库根目录的 `.env`，定期调用 GitHub API（`GET /user/starred`）获取最近星标；再用本地状态文件记录已处理的仓库 ID，避免重复触发；发现新仓库时，向 OpenClaw 的 `hooks/agent` 发送包含仓库名、描述、链接的 webhook 消息。OpenClaw 接到任务后，结合 DeepWiki 概述与 README 生成结构化中文文档，并按分类保存到你的知识库（如 Obsidian/GitWiki）。

它的价值在于把“看过”变成“能用”：你不必每次都从零理解项目，也不必依赖记忆去找回收藏。文档产出具备统一结构（定位、亮点、架构、快速开始、边界等），未来只要搜索关键词或按分类浏览，就能快速回到当初的判断与用法；同时支持作为系统级服务常驻运行，让开源情报流变成持续沉淀的个人/团队资产。


# Skill结构

```text
Autodoc-GitHub-StarRepo-Skill/
├── README.md
├── .env.example
├── SKILL.md
├── scripts/
│   └── webhook_poller.py
└── references/
    ├── classification.md
    ├── deepwiki_mcp.md
    ├── doc_template.md
    └── github_stars.md
```

# 项目介绍

这是一个 GitHub Stars 轮询器：定期检查你的星标仓库列表，发现新仓库后通过 OpenClaw 的 webhook 触发自动文档生成。它面向“收藏多、回头找难”的痛点，把“Star”变成可检索的知识资产。

核心功能：
1. 轮询 GitHub Stars（默认 60 秒，可配置）
2. 发现新仓库后触发 OpenClaw webhook
3. 自动记录已处理仓库，避免重复
4. 支持跨平台作为系统服务常驻运行

工作流程：
1. 脚本读取 `.env` 配置（GitHub Token、Webhook、轮询间隔等）
2. 请求 GitHub `GET /user/starred` 获取最近星标
3. 对比本地状态文件，过滤已处理项
4. 触发 OpenClaw webhook，交由技能执行文档生成

适用场景：
1. 有大量 Star 的个人或团队
2. 需要将开源项目系统化整理进知识库
3. 希望用自动化减少“收藏即遗忘”

# 快速配置

**只需把README.md交给OpenClaw或是Claude Code，让它帮你配置好即可。**

## 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows（PowerShell）：

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Webhook 配置

1. 确认 OpenClaw 网关地址
   - 默认地址：`http://127.0.0.1:18789`
   - 如有变化，请在环境变量里设置 `OPENCLAW_URL`
2. 获取 Webhook Token
   - 在 OpenClaw 的 `openclaw.json` 中配置 `hooks.token`
   - 将其填入环境变量 `WEBHOOK_TOKEN`

`openclaw.json`中的配置示例：
``` json
{
  "hooks": {
    "enabled": true,
    "path": "/hooks",
    "token": "YOUR_WEBHOOK_TOKEN",
    "_comment_webhook_token": "可通过 openssl rand -hex 24 生成",
    "internal": {
      "enabled": true,
      "entries": {
        "boot-md": { "enabled": true },
        "command-logger": { "enabled": true },
        "session-memory": { "enabled": true }
      }
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "YOUR_GATEWAY_TOKEN"
    },
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    }
  }
}
```

说明：`WEBHOOK_TOKEN` 对应 `hooks.token`，与 `gateway.auth.token` 无关。

## 环境变量配置

在仓库根目录创建 `.env`，至少填写以下内容：

GITHUB_TOKEN=你的GitHubToken
OPENCLAW_URL=http://127.0.0.1:18789
WEBHOOK_TOKEN=你的WebHook Token
FEISHU_CHANNEL_ID=你的飞书群ID（可选）

获取 GitHub Token（推荐 Fine-grained PAT）：

1. 打开 GitHub Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens
2. 点击 Generate new token，选择账号与到期时间
3. Permissions 里勾选 User permissions -> Starring: Read
4. 生成并复制 Token，填入 `GITHUB_TOKEN`

说明：`GET /user/starred` 端点需要 “Starring: Read” 权限；如果只访问公开资源可不授权，但本脚本使用用户已登录的星标列表，因此需要 Token。

可选配置：

POLL_INTERVAL=120
STATE_FILE=./workspace/github_stars_state.json
LOG_FILE=./workspace/logs/github_poller.log

说明：
- `GITHUB_TOKEN` 需要有读取星标仓库权限
- `STATE_FILE` 和 `LOG_FILE` 建议使用相对路径，便于跨平台使用
- `FEISHU_CHANNEL_ID` 不填则不发送飞书通知。通过OpenClaw来帮助查找和填写这个变量
- 飞书通知通过环境变量配置，不再使用 `config.json`

环境变量模板：

复制 `.env.example` 为 `.env`，再填入你的实际值。



## 启动系统级服务（macOS / Linux / Windows）

下面三种方式任选其一。路径示例以仓库目录为 `~/Autodoc-GitHub-StarRepo-Skill`。

### Linux（systemd）

模板文件：`services/linux-systemd.service`

1. 复制模板到：`~/.config/systemd/user/autodoc-gh-star.service`
2. 按模板注释替换用户名与路径

```ini
[Unit]
Description=Autodoc GitHub Star Poller
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/youruser/Autodoc-GitHub-StarRepo-Skill
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/env python3 /home/youruser/Autodoc-GitHub-StarRepo-Skill/scripts/webhook_poller.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

3. 启动并设为开机自启：

```bash
systemctl --user daemon-reload
systemctl --user enable --now autodoc-gh-star.service
```

说明：该方式会读取仓库根目录 `.env`（脚本内 `load_dotenv()`）。

### macOS（launchd）

模板文件：`services/macos-launchd.plist`

1. 复制模板到：`~/Library/LaunchAgents/com.autodoc.ghstar.plist`
2. 按模板注释替换用户名与路径

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.autodoc.ghstar</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>/Users/youruser/Autodoc-GitHub-StarRepo-Skill/scripts/webhook_poller.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/youruser/Autodoc-GitHub-StarRepo-Skill</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/youruser/Autodoc-GitHub-StarRepo-Skill/workspace/logs/github_poller.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/youruser/Autodoc-GitHub-StarRepo-Skill/workspace/logs/github_poller.err.log</string>
  </dict>
</plist>
```

3. 加载并启动：

```bash
launchctl load ~/Library/LaunchAgents/com.autodoc.ghstar.plist
launchctl start com.autodoc.ghstar
```

### Windows（任务计划程序）

模板文件：`services/windows-task.xml`
一键脚本：`services/windows-register.ps1`

1. 打开“任务计划程序” -> “创建任务”
2. 常规：勾选“使用最高权限运行”，配置为当前用户
3. 触发器：选择“计算机启动时”或“登录时”
4. 操作：启动程序
   - 程序：`C:\Python39\python.exe`（替换为你的 Python 路径）
   - 参数：`C:\Path\Autodoc-GitHub-StarRepo-Skill\scripts\webhook_poller.py`
   - 起始于：`C:\Path\Autodoc-GitHub-StarRepo-Skill`

说明：Windows 上同样使用仓库根目录 `.env`，确保该文件存在且路径无空格或已正确转义。
