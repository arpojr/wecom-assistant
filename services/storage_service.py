"""
数据存储服务
负责保存用户配置、消息历史和分析结果
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class StorageService:
    """数据存储服务"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.ensure_dir()

        # 文件路径
        self.users_file = os.path.join(data_dir, "users.json")
        self.goals_file = os.path.join(data_dir, "goals.json")
        self.analysis_file = os.path.join(data_dir, "analysis_history.json")
        self.cache_file = os.path.join(data_dir, "cache.json")

        # 初始化文件
        self._init_files()

    def ensure_dir(self):
        """确保目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _init_files(self):
        """初始化数据文件"""
        for file_path in [self.users_file, self.goals_file, self.analysis_file, self.cache_file]:
            if not os.path.exists(file_path):
                self._write_json(file_path, {})

    def _read_json(self, file_path: str) -> dict:
        """读取 JSON 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取文件错误: {e}")
            return {}

    def _write_json(self, file_path: str, data: dict):
        """写入 JSON 文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入文件错误: {e}")

    # ========== 用户管理 ==========

    def save_user(self, user_id: str, user_data: dict):
        """保存用户信息"""
        users = self._read_json(self.users_file)
        users[user_id] = {
            **user_data,
            "updated_at": datetime.now().isoformat()
        }
        self._write_json(self.users_file, users)

    def get_user(self, user_id: str) -> Optional[dict]:
        """获取用户信息"""
        users = self._read_json(self.users_file)
        return users.get(user_id)

    def get_all_users(self) -> Dict[str, dict]:
        """获取所有用户"""
        return self._read_json(self.users_file)

    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        users = self._read_json(self.users_file)
        if user_id in users:
            del users[user_id]
            self._write_json(self.users_file, users)
            return True
        return False

    # ========== 目标管理 ==========

    def save_goals(self, user_id: str, goals: List[str]):
        """保存用户目标"""
        goals_data = self._read_json(self.goals_file)
        goals_data[user_id] = {
            "goals": goals,
            "updated_at": datetime.now().isoformat()
        }
        self._write_json(self.goals_file, goals_data)

    def get_goals(self, user_id: str) -> List[str]:
        """获取用户目标"""
        goals_data = self._read_json(self.goals_file)
        user_goals = goals_data.get(user_id, {})
        return user_goals.get("goals", [])

    # ========== 分析历史 ==========

    def save_analysis(self, user_id: str, analysis: dict):
        """保存分析结果"""
        history = self._read_json(self.analysis_file)

        if user_id not in history:
            history[user_id] = []

        # 添加新分析记录
        history[user_id].append({
            **analysis,
            "timestamp": datetime.now().isoformat()
        })

        # 只保留最近30条记录
        if len(history[user_id]) > 30:
            history[user_id] = history[user_id][-30:]

        self._write_json(self.analysis_file, history)

    def get_analysis_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """获取分析历史"""
        history = self._read_json(self.analysis_file)
        user_history = history.get(user_id, [])
        return user_history[-limit:]

    # ========== 缓存管理 ==========

    def set_cache(self, key: str, value: any, expire_seconds: int = 3600):
        """设置缓存"""
        cache = self._read_json(self.cache_file)
        cache[key] = {
            "value": value,
            "expire_at": datetime.now().timestamp() + expire_seconds
        }
        self._write_json(self.cache_file, cache)

    def get_cache(self, key: str) -> Optional[any]:
        """获取缓存"""
        cache = self._read_json(self.cache_file)
        item = cache.get(key)

        if item:
            # 检查是否过期
            if item.get("expire_at", 0) > datetime.now().timestamp():
                return item.get("value")
            else:
                # 删除过期缓存
                del cache[key]
                self._write_json(self.cache_file, cache)

        return None

    def clear_expired_cache(self):
        """清除过期缓存"""
        cache = self._read_json(self.cache_file)
        now = datetime.now().timestamp()

        cache = {k: v for k, v in cache.items() if v.get("expire_at", 0) > now}
        self._write_json(self.cache_file, cache)


# 全局实例
storage = StorageService()
