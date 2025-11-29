#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证码服务 - 封装所有验证码处理功能
"""
import asyncio
from typing import Optional

from visual_automation.captcha_solver import CaptchaSolver
from utils.logger import get_logger
from utils.exceptions import CaptchaError


class CaptchaService:
    """验证码服务类"""
    
    def __init__(self):
        self.captcha_solver = CaptchaSolver()
        self.logger = get_logger(__name__)
        
    async def solve_captcha(self) -> bool:
        """
        解决屏幕上的验证码
        
        Returns:
            bool: 验证码是否解决成功
        """
        try:
            self.logger.info("🧩 开始处理验证码")
            success = await self.captcha_solver.detect_and_solve_captcha()
            
            if success:
                self.logger.info("✅ 验证码处理成功")
            else:
                self.logger.warning("⚠️ 验证码处理失败")
                
            return success
            
        except CaptchaError as e:
            self.logger.error(f"验证码处理错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            raise CaptchaError(f"验证码处理失败: {str(e)}")
    
    async def wait_for_captcha_and_solve(self, timeout: int = 30) -> bool:
        """
        等待并解决验证码
        
        Args:
            timeout: 等待超时时间（秒）
            
        Returns:
            bool: 验证码是否解决成功
        """
        try:
            self.logger.info(f"⏳ 等待验证码出现，超时时间: {timeout}秒")
            
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < timeout:
                # 检查是否出现验证码
                success = await self.solve_captcha()
                if success:
                    return True
                    
                # 等待一段时间后重试
                await asyncio.sleep(2)
            
            self.logger.warning("⏰ 等待验证码超时")
            return False
            
        except CaptchaError as e:
            self.logger.error(f"等待验证码错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            raise CaptchaError(f"等待验证码失败: {str(e)}")
