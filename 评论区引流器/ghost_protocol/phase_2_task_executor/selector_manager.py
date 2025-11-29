# -*- coding: utf-8 -*-
"""
选择器管理器
负责管理和维护各平台的DOM选择器，支持自动检测和更新。
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class SelectorManager:
    """
    选择器管理器，负责管理不同平台的DOM选择器配置。
    支持自动检测选择器有效性并进行更新。
    """
    def __init__(self, config_path: str = None):
        """
        初始化选择器管理器
        
        :param config_path: 选择器配置文件路径，默认为模块同级目录下的selectors.json
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 'selectors.json'
        )
        self.selectors = {}
        self.load_selectors()
        
    def load_selectors(self) -> None:
        """加载选择器配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.selectors = json.load(f)
                print(f"✅ 已加载选择器配置: {len(self.selectors)} 个平台")
            else:
                print("⚠️ 选择器配置文件不存在，将使用默认配置")
                # 初始化默认选择器配置
                self.selectors = {
                    "youtube": {
                        "comment_box": "#placeholder-area",
                        "comment_input": "#contenteditable-root",
                        "submit_button": "#submit-button",
                        "version": 1,
                        "history": [],
                        "last_updated": datetime.now().isoformat(),
                        "fallbacks": {
                            "comment_box": ["ytd-comment-simplebox-renderer", ".ytd-comments-header-renderer"],
                            "comment_input": ["#contenteditable-textarea", ".ytd-commentbox"],
                            "submit_button": ["#submit", "paper-button#button"]
                        }
                    },
                    "bilibili": {
                        "comment_box": ".ipt-txt",
                        "comment_input": ".ipt-txt",
                        "submit_button": ".comment-submit",
                        "version": 1,
                        "history": [],
                        "last_updated": datetime.now().isoformat(),
                        "fallbacks": {
                            "comment_box": [".comment-send-lite .textarea-container"],
                            "comment_input": [".comment-send-lite .textarea-container textarea"],
                            "submit_button": [".comment-submit"]
                        }
                    },
                    "douyin": {
                        "comment_box": ".public-DraftEditor-content",
                        "comment_input": ".public-DraftEditor-content",
                        "submit_button": ".comment-input button",
                        "version": 1,
                        "history": [],
                        "last_updated": datetime.now().isoformat(),
                        "fallbacks": {
                            "comment_box": [".comment-input-container"],
                            "comment_input": [".comment-input-container textarea"],
                            "submit_button": [".comment-input-container .send-button"]
                        }
                    }
                }
                self.save_selectors()
        except Exception as e:
            print(f"❌ 加载选择器配置失败: {e}")
            # 使用内存中的默认配置
            self.selectors = {
                "youtube": {
                    "comment_box": "#placeholder-area",
                    "comment_input": "#contenteditable-root",
                    "submit_button": "#submit-button"
                }
            }
    
    def save_selectors(self) -> None:
        """保存选择器配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.selectors, f, indent=2, ensure_ascii=False)
            print(f"✅ 选择器配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"❌ 保存选择器配置失败: {e}")
    
    def get_selectors(self, platform: str) -> Dict[str, str]:
        """
        获取指定平台的选择器
        
        :param platform: 平台名称，如youtube, bilibili等
        :return: 包含选择器的字典
        """
        if platform not in self.selectors:
            print(f"⚠️ 未找到平台 {platform} 的选择器配置，将使用YouTube配置")
            platform = "youtube"
        
        # 返回主选择器（不包括fallbacks和metadata）
        return {
            k: v for k, v in self.selectors[platform].items() 
            if k not in ["fallbacks", "last_updated"]
        }
    
    def get_fallbacks(self, platform: str, selector_type: str) -> list:
        """
        获取指定平台和选择器类型的备选选择器
        
        :param platform: 平台名称
        :param selector_type: 选择器类型，如comment_box
        :return: 备选选择器列表
        """
        if platform not in self.selectors:
            return []
        
        fallbacks = self.selectors[platform].get("fallbacks", {})
        return fallbacks.get(selector_type, [])
    
    async def verify_and_update_selectors(self, page, platform: str) -> Dict[str, str]:
        """
        验证选择器是否有效，如果无效则尝试使用备选选择器
        
        :param page: Playwright页面对象
        :param platform: 平台名称
        :return: 更新后的选择器字典
        """
        selectors = self.get_selectors(platform)
        updated = False
        
        for selector_type, selector in selectors.items():
            # 检查选择器是否存在
            element = await page.query_selector(selector)
            if not element:
                print(f"⚠️ 选择器 {selector_type}: {selector} 无效，尝试备选选择器")
                
                # 尝试备选选择器
                fallbacks = self.get_fallbacks(platform, selector_type)
                for fallback in fallbacks:
                    element = await page.query_selector(fallback)
                    if element:
                        print(f"✅ 找到有效的备选选择器: {fallback}")
                        prev = {
                            "selector_type": selector_type,
                            "old": self.selectors[platform].get(selector_type),
                            "new": fallback,
                            "timestamp": datetime.now().isoformat()
                        }
                        self.selectors[platform][selector_type] = fallback
                        selectors[selector_type] = fallback
                        self.selectors[platform]["version"] = self.selectors[platform].get("version", 1) + 1
                        hist = self.selectors[platform].get("history", [])
                        hist.append(prev)
                        self.selectors[platform]["history"] = hist
                        updated = True
                        break
                
                if not element:
                    print(f"❌ 所有 {selector_type} 选择器都无效")
        
        if updated:
            # 更新最后更新时间
            self.selectors[platform]["last_updated"] = datetime.now().isoformat()
            self.save_selectors()
            print(f"✅ 已更新 {platform} 平台的选择器配置")
        
        return selectors
