"""
消息分析服务模块
使用 AI 分析消息内容，提取重点和待办事项
"""

import json
from datetime import datetime
from typing import List, Dict


class MessageAnalyzer:
    """消息分析器"""

    def __init__(self):
        self.importance_keywords = [
            "紧急", "紧急@", "重要", "截止", "deadline", "急需",
            "@所有人", "@all", "必须", "需要今天", "立即",
            "提醒", "注意", "截止日期", "完成"
        ]

        self.action_keywords = [
            "请", "帮我", "需要你", "要你", "麻烦", "麻烦你",
            "能不能", "是否可以", "请帮忙", "负责", "跟进",
            "处理", "完成", "回复", "确认", "联系"
        ]

        self.completed_keywords = [
            "已完成", "搞定了", "完成了", "做好", "done",
            "搞定", "结束", "完毕", "没问题"
        ]

    def analyze_messages(self, messages_data: List[dict], user_goals: List[str] = None) -> dict:
        """
        分析消息数据，生成摘要

        Args:
            messages_data: 消息数据列表
            user_goals: 用户的目标列表

        Returns:
            分析结果字典
        """
        all_messages = []

        # 收集所有消息
        for chat_data in messages_data:
            for msg in chat_data.get("messages", []):
                all_messages.append({
                    "content": msg.get("content", ""),
                    "time": msg.get("msgtime", ""),
                    "sender": msg.get("from", {}).get("name", "未知"),
                    "chat_name": chat_data.get("chat_name", "未知群")
                })

        # 按时间排序
        all_messages.sort(key=lambda x: x.get("time", ""), reverse=True)

        # 提取重点消息
        important_messages = self._extract_important(all_messages)

        # 提取待办事项
        todo_items = self._extract_todos(all_messages)

        # 生成摘要
        summary = self._generate_summary(important_messages, todo_items, user_goals)

        return {
            "summary": summary,
            "important_messages": important_messages,
            "todo_items": todo_items,
            "total_messages": len(all_messages),
            "analyzed_at": datetime.now().isoformat()
        }

    def _extract_important(self, messages: List[dict]) -> List[dict]:
        """提取重要消息"""
        important = []

        for msg in messages:
            content = msg.get("content", "").lower()

            # 检查是否包含重要关键词
            is_important = any(kw in content for kw in self.importance_keywords)

            # 检查是否 @ 了用户
            if "@" in content and "我" in content:
                is_important = True

            if is_important:
                important.append({
                    "content": msg.get("content", ""),
                    "time": msg.get("time", ""),
                    "sender": msg.get("sender", "未知"),
                    "chat_name": msg.get("chat_name", "未知群"),
                    "reason": self._get_important_reason(content)
                })

        return important[:20]  # 最多返回20条

    def _extract_todos(self, messages: List[dict]) -> List[dict]:
        """提取待办事项"""
        todos = []

        for msg in messages:
            content = msg.get("content", "")
            content_lower = content.lower()

            # 检查是否包含行动关键词
            has_action = any(kw in content for kw in self.action_keywords)

            # 检查是否未完成
            is_completed = any(kw in content_lower for kw in self.completed_keywords)

            if has_action and not is_completed:
                todos.append({
                    "content": content,
                    "time": msg.get("time", ""),
                    "sender": msg.get("sender", "未知"),
                    "chat_name": msg.get("chat_name", "未知群"),
                    "priority": self._get_priority(content)
                })

        return todos[:15]  # 最多返回15条

    def _get_important_reason(self, content: str) -> str:
        """获取重要性原因"""
        content_lower = content.lower()

        if "@所有人" in content or "@all" in content_lower:
            return "📢 全员通知"
        elif "紧急" in content or "急需" in content:
            return "🔴 紧急事项"
        elif "@" in content and "我" in content:
            return "👤 @提及你"
        elif "截止" in content or "deadline" in content_lower:
            return "⏰ 截止日期"
        else:
            return "⭐ 重要内容"

    def _get_priority(self, content: str) -> str:
        """获取优先级"""
        if "紧急" in content or "立即" in content:
            return "高"
        elif "尽快" in content or "尽快" in content:
            return "中"
        else:
            return "普通"

    def _generate_summary(self, important: List[dict], todos: List[dict], goals: List[str] = None) -> str:
        """生成摘要文本"""
        lines = []
        lines.append("📊 WeCom 消息摘要")
        lines.append("=" * 40)
        lines.append("")

        # 重要通知
        if important:
            lines.append(f"📌 重要通知 ({len(important)} 条)")
            lines.append("-" * 20)
            for i, msg in enumerate(important[:5], 1):
                lines.append(f"{i}. [{msg['reason']}] {msg['content'][:50]}...")
                lines.append(f"   💬 {msg['chat_name']} | {msg['sender']}")
            lines.append("")

        # 待办事项
        if todos:
            lines.append(f"📋 待办事项 ({len(todos)} 项)")
            lines.append("-" * 20)
            for i, todo in enumerate(todos[:8], 1):
                priority_icon = "🔴" if todo['priority'] == "高" else "🟡" if todo['priority'] == "中" else "🟢"
                lines.append(f"{i}. {priority_icon} {todo['content'][:60]}...")
                lines.append(f"   📍 {todo['chat_name']}")
            lines.append("")

        # 目标关联
        if goals:
            lines.append(f"🎯 目标进度提醒")
            lines.append("-" * 20)
            for goal in goals[:3]:
                lines.append(f"• {goal}")
            lines.append("")

        lines.append("=" * 40)
        lines.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        return "\n".join(lines)

    def format_todo_for_display(self, todos: List[dict]) -> str:
        """格式化待办事项为易读格式"""
        if not todos:
            return "✅ 暂无待办事项"

        lines = ["📋 你的待办事项：", ""]

        # 按优先级分组
        high_priority = [t for t in todos if t['priority'] == "高"]
        medium_priority = [t for t in todos if t['priority'] == "中"]
        normal_priority = [t for t in todos if t['priority'] == "普通"]

        if high_priority:
            lines.append("🔴 高优先级:")
            for i, todo in enumerate(high_priority, 1):
                lines.append(f"   {i}. {todo['content']}")
                lines.append(f"      来自: {todo['chat_name']} | {todo['sender']}")
            lines.append("")

        if medium_priority:
            lines.append("🟡 中优先级:")
            for i, todo in enumerate(medium_priority, 1):
                lines.append(f"   {i}. {todo['content']}")
            lines.append("")

        if normal_priority:
            lines.append("🟢 普通:")
            for i, todo in enumerate(normal_priority, 1):
                lines.append(f"   {i}. {todo['content'][:50]}...")

        return "\n".join(lines)


# 全局实例
analyzer = MessageAnalyzer()
