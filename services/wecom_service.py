"""
WeCom API 服务模块
处理与 WeCom API 的所有交互
"""

import requests
import json
import time
from datetime import datetime
from config import WECOM_CONFIG, WECOM_API_BASE


class WeComService:
    """WeCom API 服务类"""

    def __init__(self):
        self.corp_id = WECOM_CONFIG["corp_id"]
        self.agent_id = WECOM_CONFIG["agent_id"]
        self.secret = WECOM_CONFIG["secret"]
        self.access_token = None
        self.token_expires_at = 0

    def _get_access_token(self) -> str:
        """获取访问令牌"""
        # 检查是否已缓存且未过期
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = f"{WECOM_API_BASE}/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("errcode") == 0:
                self.access_token = data["access_token"]
                # 提前5分钟过期
                self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
                return self.access_token
            else:
                raise Exception(f"获取 access_token 失败: {data}")
        except Exception as e:
            print(f"获取 access_token 错误: {e}")
            raise

    def get_department_list(self) -> list:
        """获取部门列表"""
        token = self._get_access_token()
        url = f"{WECOM_API_BASE}/department/list"
        params = {"access_token": token}

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("errcode") == 0:
            return data.get("department", [])
        return []

    def get_group_chat_list(self, limit: int = 100) -> list:
        """获取群聊列表"""
        token = self._get_access_token()
        url = f"{WECOM_API_BASE}/appchat/list"
        params = {"access_token": token, "limit": limit}

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("errcode") == 0:
            return data.get("chatlist", [])
        return []

    def get_group_messages(self, chat_id: str, limit: int = 50) -> list:
        """获取群聊消息"""
        token = self._get_access_token()
        url = f"{WECOM_API_BASE}/appchat/get"
        params = {"access_token": token, "chatid": chat_id}

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("errcode") == 0:
                return data.get("chat", {}).get("msgs", [])
            return []
        except Exception as e:
            print(f"获取群消息错误: {e}")
            return []

    def get_user_info(self, user_id: str) -> dict:
        """获取用户信息"""
        token = self._get_access_token()
        url = f"{WECOM_API_BASE}/user/get"
        params = {"access_token": token, "userid": user_id}

        response = requests.get(url, params=params, timeout=10)
        return response.json()

    def send_message(self, user_id: str, content: str, msg_type: str = "text") -> bool:
        """发送消息给用户"""
        token = self._get_access_token()
        url = f"{WECOM_API_BASE}/message/send"
        params = {"access_token": token}

        data = {
            "touser": user_id,
            "msgtype": msg_type,
            "agentid": int(self.agent_id),
            msg_type: {
                "content": content
            }
        }

        try:
            response = requests.post(url, params=params, json=data, timeout=10)
            result = response.json()
            return result.get("errcode") == 0
        except Exception as e:
            print(f"发送消息错误: {e}")
            return False

    def get_all_messages(self, limit_per_chat: int = 50) -> list:
        """获取所有群聊的最新消息"""
        all_messages = []
        group_chats = self.get_group_chat_list()

        for chat in group_chats:
            chat_id = chat.get("chatid")
            if chat_id:
                messages = self.get_group_messages(chat_id, limit_per_chat)
                if messages:
                    all_messages.append({
                        "chat_id": chat_id,
                        "chat_name": chat.get("name", "未知群"),
                        "messages": messages
                    })

        return all_messages


# 全局实例
wecom_service = WeComService()
