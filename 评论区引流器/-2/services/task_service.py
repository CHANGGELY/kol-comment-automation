from typing import Dict, Any
from utils.logger import get_logger
from .browser_service import BrowserService


class TaskService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.browser_service = BrowserService()

    async def run_comment_task(self, task: Dict[str, Any]) -> bool:
        account_id = task.get("account_id", "default_account")
        platform = task.get("platform", "youtube")
        video_id = task["video_id"]
        content = task["content"]
        ok = await self.browser_service.open_video_and_comment(account_id, platform, video_id, content)
        return ok
