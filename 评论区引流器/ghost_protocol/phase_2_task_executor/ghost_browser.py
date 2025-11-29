# -*- coding: utf-8 -*-
import os
from typing import Tuple
from playwright.async_api import async_playwright, BrowserContext, Page
from .action_kernel import ActionKernel


class GhostBrowser:
    def __init__(self):
        self.action_kernel = ActionKernel()

    async def launch(self, account_id: str, headless: bool | None = None) -> Tuple[Page, BrowserContext, any]:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass

        enable_headless = os.getenv("ENABLE_HEADLESS", "false").lower() in {"1", "true", "yes"}
        proxy_server = os.getenv("PROXY_SERVER", "").strip()
        use_headless = enable_headless if headless is None else headless

        p = await async_playwright().start()
        launch_args = {"headless": use_headless}

        browser = await p.chromium.launch(**launch_args)

        context_args = {}
        if proxy_server:
            context_args["proxy"] = {"server": proxy_server}

        context = await browser.new_context(**context_args)
        page = await context.new_page()
        return page, context, p
