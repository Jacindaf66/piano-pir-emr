# backend/config/ai_config.py
"""
AI 模型配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AIConfig:
    """AI 模型配置"""
    
    # 豆包配置
    DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "91be1b79-0621-44a1-a725-a59462602582")
    DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3/")
    DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-seed-1-6-250615")
    
    # DeepSeek 配置 (通过 SiliconFlow)
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-edmctfrdmjllptnrkqyqlwhunenwdhaqgzcfxzkkcvadvesp")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.siliconflow.cn/v1")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-R1")
    
    # 通用配置
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    TIMEOUT = 60
    
    @classmethod
    def get_doubao_config(cls):
        """获取豆包配置"""
        return {
            "api_key": cls.DOUBAO_API_KEY,
            "base_url": cls.DOUBAO_BASE_URL,
            "model": cls.DOUBAO_MODEL
        }
    
    @classmethod
    def get_deepseek_config(cls):
        """获取 DeepSeek 配置"""
        return {
            "api_key": cls.DEEPSEEK_API_KEY,
            "base_url": cls.DEEPSEEK_BASE_URL,
            "model": cls.DEEPSEEK_MODEL
        }
    
    @classmethod
    def print_config(cls):
        """打印配置信息（调试用）"""
        print(f"[AI配置] 豆包模型: {cls.DOUBAO_MODEL}")
        print(f"[AI配置] DeepSeek模型: {cls.DEEPSEEK_MODEL}")