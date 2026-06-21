#!/usr/bin/env python3
"""
GitHub Stars Webhook Poller for OpenClaw

功能：
- 默认每 3 小时检查 GitHub 星标仓库，用户可通过 POLL_INTERVAL 自行调整
- 发现新仓库时通过 webhook 唤醒 Agent，或在 dry-run 中生成办公小浣熊任务说明
- 自动记录已处理仓库，避免重复

使用方式：
1. 复制 .env.example 为 .env 并填写配置
2. python3 scripts/webhook_poller.py
3. 演示模式：python3 scripts/webhook_poller.py --dry-run --once --sample examples/sample_starred_repo.json
"""

import argparse
import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False

# ========== 配置 ==========
load_dotenv()  # 加载 .env 文件

DEFAULT_POLL_INTERVAL = 3 * 60 * 60

# OpenClaw Webhook 配置
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://127.0.0.1:18789")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")  # OpenClaw webhook token
WEBHOOK_PATH = "/hooks/agent"
OPENCLAW_AGENT_ID = os.getenv("OPENCLAW_AGENT_ID", "")  # 留空使用默认 agent

# 可选通知配置（飞书群聊）
FEISHU_CHANNEL_ID = os.getenv("FEISHU_CHANNEL_ID")

# 轮询间隔（秒）
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", str(DEFAULT_POLL_INTERVAL)))

# 默认工作目录（仓库根目录/workspace）
REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = REPO_ROOT / "workspace"

# 状态文件
STATE_FILE = os.getenv("STATE_FILE", str(WORKSPACE_DIR / "github_stars_state.json"))

# 日志配置
LOG_FILE = os.getenv("LOG_FILE", str(WORKSPACE_DIR / "logs" / "github_poller.log"))

# ========== 日志设置 ==========
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8', delay=True)
    ]
)
logger = logging.getLogger(__name__)


def require_httpx():
    try:
        import httpx
        return httpx
    except ModuleNotFoundError as exc:
        raise RuntimeError("缺少依赖 httpx，请先运行 pip install -r requirements.txt") from exc


def build_agent_payload(repo_info: dict, target: str = "openclaw") -> dict:
    repo_name = repo_info["full_name"]
    repo_url = repo_info.get("html_url", f"https://github.com/{repo_name}")
    description = repo_info.get("description", "")

    if target == "office-raccoon":
        message = f"""检测到新的 GitHub 星标仓库，需要进入 Star-DART OPC 办公小浣熊工作流。

**仓库**: {repo_name}
**描述**: {description}
**链接**: {repo_url}

本项目采用定时轮询机制发现新增 Star，默认轮询间隔为 3 小时，用户可通过 POLL_INTERVAL 自行调整。

请使用办公小浣熊能力完成完整沉淀，而不是单点摘要：
1. 使用本地 Agent / 本地文件索引读取 README、DeepWiki、Release、Issue 等资料。
2. 使用 research-synthesis 或行业研究报告专家团完成项目定位、亮点、风险和适用场景判断。
3. 使用 docx/pdf 生成结构化项目档案。
4. 使用 xlsx 更新开源项目资产台账。
5. 使用 data-dashboard 生成项目分类、趋势和复用等级看板。
6. 使用 writing-workflow 生成周报、推荐理由或社群分享文案。
7. 必要时使用 pptx / 创意 PPT 专家团生成技术选型汇报材料。

请输出可沉淀到云上知识库、飞书或 Obsidian 的项目资料。"""
    else:
        message = f"""检测到新的 GitHub 星标仓库！

**仓库**: {repo_name}
**描述**: {description}
**链接**: {repo_url}

请使用 Star-DART Skill 来处理：
1. 获取该仓库的 README 和 DeepWiki 文档
2. 使用 AI 精炼生成高质量中文文档
3. 保存到飞书知识库
4. 在多维表格中创建记录

请开始处理。"""

    return {
        "message": message,
        "name": "GitHub Stars Poller",
        "wakeMode": "now",
        "deliver": True,
        "timeoutSeconds": 600,
    }


def load_sample_repo(sample_path: str) -> dict:
    with open(sample_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        if not data:
            raise ValueError("sample 文件为空")
        return data[0]
    return data


def format_dry_run_output(repo_info: dict) -> str:
    payload = build_agent_payload(repo_info, target="office-raccoon")
    return f"""# Star-DART OPC DRY RUN

默认轮询间隔: 3 小时

## 新发现 Star

- 仓库: {repo_info.get("full_name")}
- 描述: {repo_info.get("description", "")}
- 链接: {repo_info.get("html_url", "")}

## 办公小浣熊任务说明

{payload["message"]}

## 预期办公产物

- 项目档案: docx/pdf
- 资产台账: xlsx/csv
- 数据看板: data-dashboard
- 周报材料: markdown/pdf
- 汇报材料: pptx
"""


# ========== GitHub 客户端 ==========
class GitHubMonitor:
    def __init__(self, token: str):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        }
        self.api_url = "https://api.github.com/user/starred"

    async def fetch_recent_stars(self, limit: int = 30):
        """获取最近 star 的仓库"""
        httpx = require_httpx()
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
        httpx = require_httpx()
        all_stars = []
        page = 1
        per_page = 100

        async with httpx.AsyncClient() as client:
            while True:
                try:
                    logger.info(f"获取 stars 页面 {page}...")
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

                except Exception as e:
                    logger.error(f"获取 stars 页面 {page} 失败: {e}")
                    break

        return all_stars


# ========== 状态管理 ==========
class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.processed_ids = self.load_state()

    def load_state(self) -> set:
        """加载已处理的仓库 ID"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    return set(data.get("processed_ids", []))
            except Exception as e:
                logger.warning(f"加载状态文件失败: {e}")
        return set()

    def save_state(self):
        """保存状态"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump({
                    "processed_ids": list(self.processed_ids),
                    "last_update": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")

    def add_processed(self, repo_id: int):
        self.processed_ids.add(str(repo_id))
        self.save_state()


# ========== Webhook 客户端 ==========
class OpenClawWebhook:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def trigger_agent(self, repo_info: dict) -> bool:
        """
        通过 webhook 触发 OpenClaw 生成文档

        Args:
            repo_info: 仓库信息 dict

        Returns:
            bool: 是否成功
        """
        repo_name = repo_info["full_name"]
        payload = build_agent_payload(repo_info)

        if OPENCLAW_AGENT_ID:
            payload["agentId"] = OPENCLAW_AGENT_ID

        if FEISHU_CHANNEL_ID:
            payload["channel"] = "feishu"
            payload["to"] = FEISHU_CHANNEL_ID

        url = f"{self.base_url}{WEBHOOK_PATH}"

        try:
            httpx = require_httpx()
            async with httpx.AsyncClient() as client:
                # 确保中文字符正确编码（使用UTF-8）
                json_content = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                response = await client.post(
                    url, 
                    content=json_content,
                    headers=self.headers, 
                    timeout=30.0
                )

                if response.status_code in [200, 202]:
                    logger.info(f"✅ Webhook 触发成功: {repo_name}")
                    return True
                else:
                    logger.error(f"❌ Webhook 触发失败 [{response.status_code}]: {response.text}")
                    return False

        except Exception as e:
            import traceback
            # 先打印原始错误到 stderr（绕过 logger）
            import sys
            print(f"[ERROR] Webhook 请求异常: {e}", file=sys.stderr)
            print(f"[DEBUG] 详细错误: {traceback.format_exc()}", file=sys.stderr)
            # 记录ASCII兼容的错误消息
            safe_error = str(e).encode('ascii', 'replace').decode('ascii')
            logger.error(f"❌ Webhook 请求异常: {safe_error}")
            return False


# ========== 主程序 ==========
def parse_args():
    parser = argparse.ArgumentParser(description="Star-DART GitHub Star poller")
    parser.add_argument("--dry-run", action="store_true", help="不访问 GitHub/OpenClaw，仅输出办公小浣熊演示任务")
    parser.add_argument("--once", action="store_true", help="只运行一次轮询或 dry-run")
    parser.add_argument("--sample", help="dry-run 使用的 GitHub Star 样例 JSON")
    parser.add_argument("--limit", type=int, default=10, help="每次轮询检查的最近 Star 数量")
    return parser.parse_args()


def validate_runtime_config(args):
    if args.dry_run:
        if not args.sample:
            raise ValueError("dry-run 需要提供 --sample examples/sample_starred_repo.json")
        return
    if not os.getenv("GITHUB_TOKEN"):
        raise ValueError("请设置 GITHUB_TOKEN 环境变量")
    if not WEBHOOK_TOKEN:
        raise ValueError("请设置 WEBHOOK_TOKEN 环境变量")


async def main(args=None):
    args = args or parse_args()
    validate_runtime_config(args)

    if args.dry_run:
        repo_info = load_sample_repo(args.sample)
        print(format_dry_run_output(repo_info))
        return

    logger.info("=" * 60)
    logger.info("GitHub Stars Webhook Poller 启动")
    logger.info(f"轮询间隔: {POLL_INTERVAL} 秒")
    logger.info("=" * 60)

    github = GitHubMonitor(os.getenv("GITHUB_TOKEN"))
    state = StateManager(STATE_FILE)
    webhook = OpenClawWebhook(OPENCLAW_URL, WEBHOOK_TOKEN)

    iteration = 0
    while True:
        iteration += 1
        logger.info(f"\n第 {iteration} 次轮询 - {datetime.now().strftime('%H:%M:%S')}")

        try:
            # 获取最近星标的仓库
            stars = await github.fetch_recent_stars(limit=args.limit)

            new_count = 0
            for star in stars:
                repo_id = str(star["id"])
                repo_name = star["full_name"]

                # 检查是否已处理
                if repo_id in state.processed_ids:
                    logger.debug(f"跳过已处理: {repo_name}")
                    continue

                # 发现新仓库
                logger.info(f"⭐ 发现新仓库: {repo_name}")
                new_count += 1

                # 触发 webhook
                success = await webhook.trigger_agent(star)

                if success:
                    state.add_processed(repo_id)
                    logger.info(f"已记录: {repo_name}")
                else:
                    logger.warning(f"Webhook 失败，稍后重试: {repo_name}")

            if new_count == 0:
                logger.info("暂无新仓库")
            else:
                logger.info(f"本轮处理了 {new_count} 个新仓库")

        except Exception as e:
            logger.error(f"轮询异常: {e}")

        # 等待下次轮询
        if args.once:
            logger.info("已完成一次轮询，退出")
            break
        logger.info(f"\n等待 {POLL_INTERVAL} 秒后进行下一次轮询...")
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n程序已停止")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
