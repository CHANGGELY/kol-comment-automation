# -*- coding: utf-8 -*-
"""
视觉自动化核心模块
基于OCR、多模态AI和操作系统自动化，不依赖DOM，只相信眼睛
"""
import asyncio
import base64
import io
import time
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from PIL import Image, ImageDraw
import pyautogui
import cv2
import numpy as np

# 禁用pyautogui的安全机制
pyautogui.FAILSAFE = False

# 导入项目自定义异常
from utils.exceptions import VisionError

@dataclass
class VisualElement:
    """视觉元素"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    element_type: str  # 'text', 'button', 'input', 'video', 'avatar'
    
@dataclass
class ScreenRegion:
    """屏幕区域"""
    x: int
    y: int
    width: int
    height: int
    
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

class VisionCore:
    """视觉自动化核心类"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.ocr_client = None
        self.multimodal_client = None
        self.last_screenshot = None
        self._ocr_cache = {}  # OCR结果缓存
        self._cache_ttl = 5.0  # 缓存有效期5秒
        self.setup_clients()
        
    def setup_clients(self):
        try:
            import easyocr
            try:
                self.ocr_client = easyocr.Reader(['ch_sim', 'en'], gpu=True)
            except Exception:
                self.ocr_client = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        except Exception as e:
            raise VisionError(f"初始化OCR客户端失败: {str(e)}")
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理以提高OCR识别准确率
        
        Args:
            image: 原始图像
            
        Returns:
            处理后的图像
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            return morph
        except Exception as e:
            raise VisionError(f"图像预处理失败: {str(e)}")
    
    def _get_cache_key(self, region: Optional[ScreenRegion]) -> str:
        """生成缓存键"""
        if region:
            return f"{region.x}_{region.y}_{region.width}_{region.height}"
        return "full_screen"
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """检查缓存是否有效"""
        return time.time() - timestamp < self._cache_ttl
    
    def capture_screen(self, region: Optional[ScreenRegion] = None) -> np.ndarray:
        """
        截取屏幕截图
        
        Args:
            region: 截图区域，如果为None则截取全屏
            
        Returns:
            屏幕截图的numpy数组
        """
        try:
            if region:
                screenshot = pyautogui.screenshot(region=(region.x, region.y, region.width, region.height))
            else:
                screenshot = pyautogui.screenshot()
            
            # 转换为OpenCV格式
            opencv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.last_screenshot = opencv_image
            return opencv_image
        except Exception as e:
            raise VisionError(f"屏幕截图失败: {str(e)}")
    
    def ocr_screen(self, region: Optional[ScreenRegion] = None, use_cache: bool = True) -> List[Dict]:
        """
        对屏幕区域进行OCR识别
        
        Args:
            region: OCR识别区域，如果为None则识别全屏
            use_cache: 是否使用缓存结果
            
        Returns:
            OCR识别结果列表
        """
        try:
            cache_key = self._get_cache_key(region)
            
            # 检查缓存
            if use_cache and cache_key in self._ocr_cache:
                cached_result, timestamp = self._ocr_cache[cache_key]
                if self._is_cache_valid(timestamp):
                    return cached_result
            
            # 截图
            image = self.capture_screen(region)
            
            # 预处理图像
            processed_image = self._preprocess_image(image)
            
            # OCR识别
            results = self.ocr_client.readtext(processed_image)
            
            # 格式化结果
            formatted_results = []
            for (bbox, text, confidence) in results:
                formatted_results.append({
                    'text': text.strip(),
                    'confidence': confidence,
                    'bbox': [int(coord) for coord in bbox[0]]  # 左上角坐标
                })
            
            # 更新缓存
            self._ocr_cache[cache_key] = (formatted_results, time.time())
            
            return formatted_results
        except Exception as e:
            raise VisionError(f"OCR识别失败: {str(e)}")
    
    def find_text_on_screen(self, text: str, region: Optional[ScreenRegion] = None, 
                           confidence_threshold: float = 0.6) -> Optional[VisualElement]:
        """
        在屏幕上查找指定文本
        
        Args:
            text: 要查找的文本
            region: 查找区域
            confidence_threshold: 置信度阈值
            
        Returns:
            找到的视觉元素，未找到则返回None
        """
        try:
            ocr_results = self.ocr_screen(region)
            
            for result in ocr_results:
                # 简单文本匹配（可扩展为模糊匹配）
                if text in result['text'] and result['confidence'] >= confidence_threshold:
                    # 创建视觉元素对象
                    element = VisualElement(
                        text=result['text'],
                        confidence=result['confidence'],
                        bbox=result['bbox'],
                        element_type='text'
                    )
                    return element
            
            return None
        except Exception as e:
            raise VisionError(f"查找文本失败: {str(e)}")
    
    def click_on_text(self, text: str, region: Optional[ScreenRegion] = None,
                     confidence_threshold: float = 0.6) -> bool:
        """
        点击屏幕上的指定文本
        
        Args:
            text: 要点击的文本
            region: 搜索区域
            confidence_threshold: 置信度阈值
            
        Returns:
            是否成功点击
        """
        try:
            element = self.find_text_on_screen(text, region, confidence_threshold)
            
            if element:
                # 计算点击位置（文本区域中心）
                x, y = element.bbox[0], element.bbox[1]
                pyautogui.click(x, y)
                return True
            
            return False
        except Exception as e:
            raise VisionError(f"点击文本失败: {str(e)}")
