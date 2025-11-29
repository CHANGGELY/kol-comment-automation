#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉服务 - 封装所有视觉相关的功能
"""
import asyncio
from typing import Optional, List, Dict
from dataclasses import dataclass

from visual_automation.vision_core import VisionCore, VisualElement, ScreenRegion
from utils.logger import get_logger
from utils.exceptions import VisionError


@dataclass
class TextSearchResult:
    """文本搜索结果"""
    found: bool
    element: Optional[VisualElement] = None
    error: Optional[str] = None


class VisionService:
    """视觉服务类"""
    
    def __init__(self):
        self.vision_core = VisionCore()
        self.logger = get_logger(__name__)
        
    async def find_text(self, text: str, region: Optional[ScreenRegion] = None,
                       confidence_threshold: float = 0.6) -> TextSearchResult:
        """
        在屏幕上查找指定文本
        
        Args:
            text: 要查找的文本
            region: 搜索区域
            confidence_threshold: 置信度阈值
            
        Returns:
            TextSearchResult: 搜索结果
        """
        try:
            self.logger.debug(f"🔍 搜索文本: '{text}'")
            element = self.vision_core.find_text_on_screen(
                text, region, confidence_threshold
            )
            
            result = TextSearchResult(
                found=element is not None,
                element=element
            )
            
            if result.found:
                self.logger.debug(f"✅ 找到文本: '{text}' 在位置 {element.bbox}")
            else:
                self.logger.debug(f"❌ 未找到文本: '{text}'")
                
            return result
            
        except VisionError as e:
            self.logger.error(f"视觉搜索错误: {e}")
            return TextSearchResult(
                found=False,
                error=str(e)
            )
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            return TextSearchResult(
                found=False,
                error=f"未知错误: {str(e)}"
            )
    
    async def click_text(self, text: str, region: Optional[ScreenRegion] = None,
                        confidence_threshold: float = 0.6) -> bool:
        """
        点击屏幕上的指定文本
        
        Args:
            text: 要点击的文本
            region: 搜索区域
            confidence_threshold: 置信度阈值
            
        Returns:
            bool: 是否成功点击
        """
        try:
            self.logger.debug(f"🖱️ 点击文本: '{text}'")
            success = self.vision_core.click_on_text(
                text, region, confidence_threshold
            )
            
            if success:
                self.logger.debug(f"✅ 成功点击文本: '{text}'")
                await asyncio.sleep(0.5)  # 等待界面响应
            else:
                self.logger.warning(f"❌ 未找到文本: '{text}'，无法点击")
                
            return success
            
        except VisionError as e:
            self.logger.error(f"点击文本错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            return False
    
    async def ocr_region(self, region: Optional[ScreenRegion] = None) -> List[Dict]:
        """
        对指定区域进行OCR识别
        
        Args:
            region: OCR识别区域，None表示全屏
            
        Returns:
            List[Dict]: OCR识别结果
        """
        try:
            self.logger.debug(f"🔍 OCR识别区域: {region}")
            results = self.vision_core.ocr_screen(region)
            self.logger.debug(f"✅ OCR识别完成，找到 {len(results)} 个文本元素")
            return results
            
        except VisionError as e:
            self.logger.error(f"OCR识别错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            raise VisionError(f"OCR识别失败: {str(e)}")
