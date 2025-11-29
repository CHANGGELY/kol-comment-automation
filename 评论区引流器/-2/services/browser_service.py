from typing import Tuple
from utils.logger import get_logger
from utils.exceptions import BrowserError
from 评论区引流器.ghost_protocol.phase_2_task_executor.ghost_browser import GhostBrowser
from 评论区引流器.ghost_protocol.phase_2_task_executor.selector_manager import SelectorManager


class BrowserService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.browser = GhostBrowser()
        self.selector_manager = SelectorManager()

    async def open_video_and_comment(self, account_id: str, platform: str, video_id: str, content: str) -> bool:
        page = None
        context = None
        p = None
        try:
            page, context, p = await self.browser.launch(account_id)
            if platform == "youtube":
                url = f"https://www.youtube.com/watch?v={video_id}"
            elif platform == "bilibili":
                url = f"https://www.bilibili.com/video/{video_id}"
            elif platform == "douyin":
                url = f"https://www.douyin.com/video/{video_id}"
            else:
                url = f"https://www.youtube.com/watch?v={video_id}"
            await page.goto(url, wait_until="networkidle")
            ak = self.browser.action_kernel
            await ak.thinking_pause(2, 5)
            await ak.smooth_scroll(page, 800)
            await ak.thinking_pause(1, 3)
            selectors = await self.selector_manager.verify_and_update_selectors(page, platform)
            box = selectors.get("comment_box")
            inp = selectors.get("comment_input")
            btn = selectors.get("submit_button")
            await ak.human_like_click(page, box)
            await ak.human_like_type(page, inp, content)
            await ak.thinking_pause(1, 4)
            await ak.human_like_click(page, btn)
            return True
        except Exception as e:
            self.logger.error(f"浏览器服务错误: {e}")
            raise BrowserError(str(e))
        finally:
            try:
                if context:
                    await context.close()
                if p:
                    await p.stop()
            except Exception:
                pass
