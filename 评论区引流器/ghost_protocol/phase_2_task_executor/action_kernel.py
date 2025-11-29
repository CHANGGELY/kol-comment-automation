# -*- coding: utf-8 -*-
import asyncio
import random


class ActionKernel:
    def __init__(self):
        pass

    async def thinking_pause(self, min_seconds: float = 1.0, max_seconds: float = 2.0):
        duration = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(duration)

    async def smooth_scroll(self, page, pixels: int = 600):
        await page.evaluate(f"window.scrollBy(0, {int(pixels)})")

    async def human_like_click(self, page, selector: str):
        locator = page.locator(selector)
        await locator.scroll_into_view_if_needed()
        await self.thinking_pause(0.2, 0.6)
        await locator.click(delay=int(random.uniform(50, 150)))

    async def human_like_type(self, page, selector: str, text: str):
        locator = page.locator(selector)
        await locator.scroll_into_view_if_needed()
        await self.thinking_pause(0.2, 0.6)
        await locator.fill("")
        await locator.type(text, delay=int(random.uniform(30, 90)))
