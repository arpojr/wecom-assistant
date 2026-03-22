"""
WeCom Assistant 配置文件
"""

# WeCom API 凭据
WECOM_CONFIG = {
    "corp_id": "ww2abafbe540dbfff3",
    "agent_id": "1000003",
    "secret": "4Kv3Z8LRMcwGlWEetSVynjzgSNuS8tRAEyVUqhzp9Wc"
}

# API 地址
WECOM_API_BASE = "https://qyapi.weixin.qq.com/cgi-bin"

# 系统设置
SYSTEM_CONFIG = {
    "check_interval_minutes": 30,  # 每30分钟检查一次新消息
    "daily_summary_time": "09:00",  # 每天早上9点发送摘要
    "max_messages_per_summary": 50,  # 每次摘要最多处理的消息数
    "timezone": "Asia/Shanghai"
}

# 存储路径
DATA_DIR = "./data"
LOG_DIR = "./logs"
