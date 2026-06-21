import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "webhook_poller.py"


def load_module_without_tokens():
    old_env = dict(os.environ)
    for key in ("GITHUB_TOKEN", "WEBHOOK_TOKEN"):
        os.environ.pop(key, None)
    try:
        spec = importlib.util.spec_from_file_location("webhook_poller", SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        os.environ.clear()
        os.environ.update(old_env)


class WebhookPollerTest(unittest.TestCase):
    def test_module_imports_without_runtime_tokens(self):
        module = load_module_without_tokens()
        self.assertEqual(module.DEFAULT_POLL_INTERVAL, 10800)

    def test_build_agent_payload_mentions_office_raccoon_workflow(self):
        module = load_module_without_tokens()
        repo = {
            "id": 123,
            "full_name": "example/agent-browser",
            "description": "Browser automation agent",
            "html_url": "https://github.com/example/agent-browser",
        }

        payload = module.build_agent_payload(repo, target="office-raccoon")

        self.assertEqual(payload["name"], "GitHub Stars Poller")
        self.assertIn("example/agent-browser", payload["message"])
        self.assertIn("办公小浣熊", payload["message"])
        self.assertIn("定时轮询", payload["message"])
        self.assertIn("3 小时", payload["message"])
        self.assertIn("docx/pdf", payload["message"])
        self.assertIn("xlsx", payload["message"])
        self.assertIn("data-dashboard", payload["message"])

    def test_dry_run_once_with_sample_does_not_require_tokens(self):
        sample = {
            "id": 123,
            "full_name": "example/agent-browser",
            "description": "Browser automation agent",
            "html_url": "https://github.com/example/agent-browser",
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            json.dump(sample, handle)
            sample_path = handle.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--dry-run",
                    "--once",
                    "--sample",
                    sample_path,
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            os.unlink(sample_path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("example/agent-browser", result.stdout)
        self.assertIn("办公小浣熊", result.stdout)
        self.assertIn("默认轮询间隔: 3 小时", result.stdout)


if __name__ == "__main__":
    unittest.main()
