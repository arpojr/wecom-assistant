"""
定时任务调度器
负责定时获取消息、生成摘要并推送
"""

import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from services.wecom_service import wecom_service
from services.analyzer_service import analyzer


class NotificationScheduler:
    """通知调度器"""

    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Shanghai'))
        self.app = app
        self.user_id = None
        self.goals = []

    def set_user(self, user_id: str):
        """设置用户ID"""
        self.user_id = user_id

    def set_goals(self, goals: list):
        """设置用户目标"""
        self.goals = goals

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            # 每天早上 9:00 发送日报
            self.scheduler.add_job(
                self.send_daily_summary,
                CronTrigger(hour=9, minute=0, timezone='Asia/Shanghai'),
                id='daily_summary',
                name='每日摘要'
            )

            # 每30分钟检查一次新消息（仅在工作时间）
            self.scheduler.add_job(
                self.check_new_messages,
                CronTrigger(hour='9-18', minute='*/30', timezone='Asia/Shanghai'),
                id='check_messages',
                name='检查新消息'
            )

            self.scheduler.start()
            print("✅ 调度器已启动")

    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("⏹️ 调度器已停止")

    def send_daily_summary(self):
        """发送每日摘要"""
        print(f"📊 正在生成每日摘要... 时间: {datetime.now()}")

        try:
            # 获取所有消息
            messages_data = wecom_service.get_all_messages()

            if not messages_data:
                print("📭 暂无消息")
                return

            # 分析消息
            analysis = analyzer.analyze_messages(messages_data, self.goals)

            # 发送摘要
            summary = analysis.get("summary", "")

            if self.user_id:
                success = wecom_service.send_message(self.user_id, summary)
                if success:
                    print("✅ 每日摘要已发送")
                else:
                    print("❌ 发送摘要失败")
            else:
                print("⚠️ 未设置用户ID")

            return analysis

        except Exception as e:
            print(f"❌ 生成摘要时出错: {e}")
            return None

    def check_new_messages(self):
        """检查新消息并发送提醒"""
        print(f"🔔 检查新消息... 时间: {datetime.now()}")

        try:
            # 获取所有消息
            messages_data = wecom_service.get_all_messages()

            if not messages_data:
                return None

            # 分析消息
            analysis = analyzer.analyze_messages(messages_data, self.goals)

            # 检查是否有紧急事项
            important = analysis.get("important_messages", [])
            urgent_items = [m for m in important if "紧急" in m.get("reason", "")]

            if urgent_items and self.user_id:
                # 发送紧急提醒
                urgent_text = "🔴 紧急提醒！\n\n"
                for item in urgent_items[:3]:
                    urgent_text += f"• {item['content']}\n"
                    urgent_text += f"  来自: {item['chat_name']}\n\n"

                wecom_service.send_message(self.user_id, urgent_text)
                print(f"✅ 已发送 {len(urgent_items)} 条紧急提醒")

            return analysis

        except Exception as e:
            print(f"❌ 检查消息时出错: {e}")
            return None

    def generate_summary_now(self):
        """立即生成摘要（用于手动触发）"""
        return self.send_daily_summary()


# 全局实例
scheduler = NotificationScheduler()
