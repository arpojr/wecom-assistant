"""
WeCom 助手 - 主应用
Web 界面 + API 服务
"""

from flask import Flask, render_template, request, jsonify
import os

from services.wecom_service import wecom_service
from services.analyzer_service import analyzer
from services.scheduler_service import scheduler
from services.storage_service import storage
from config import WECOM_CONFIG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wecom-assistant-secret-key-2024'
app.config['JSON_AS_ASCII'] = False


# ========== 路由 ==========

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/dashboard')
def dashboard():
    """仪表盘数据"""
    try:
        # 获取用户配置
        user_id = WECOM_CONFIG.get("agent_id")
        goals = storage.get_goals(user_id)
        analysis_history = storage.get_analysis_history(user_id, limit=5)

        # 获取群聊列表
        chats = wecom_service.get_group_chat_list()

        return jsonify({
            "success": True,
            "data": {
                "goals": goals,
                "recent_analysis": analysis_history,
                "chat_count": len(chats),
                "user_id": user_id
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/messages')
def get_messages():
    """获取消息"""
    try:
        limit = request.args.get('limit', 50, type=int)
        messages = wecom_service.get_all_messages(limit)

        return jsonify({
            "success": True,
            "data": messages
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析消息"""
    try:
        data = request.json or {}
        user_id = data.get('user_id') or WECOM_CONFIG.get("agent_id")

        # 获取消息
        messages = wecom_service.get_all_messages()

        # 获取用户目标
        goals = storage.get_goals(user_id)

        # 分析
        result = analyzer.analyze_messages(messages, goals)

        # 保存分析结果
        storage.save_analysis(user_id, result)

        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/goals', methods=['GET', 'POST', 'DELETE'])
def goals():
    """目标管理"""
    user_id = request.args.get('user_id') or WECOM_CONFIG.get("agent_id")

    if request.method == 'GET':
        goals = storage.get_goals(user_id)
        return jsonify({"success": True, "goals": goals})

    elif request.method == 'POST':
        data = request.json
        goals = data.get('goals', [])
        storage.save_goals(user_id, goals)

        # 更新调度器
        scheduler.set_goals(goals)

        return jsonify({"success": True, "message": "目标已保存"})

    elif request.method == 'DELETE':
        goal = request.args.get('goal', '')
        current_goals = storage.get_goals(user_id)
        if goal in current_goals:
            current_goals.remove(goal)
            storage.save_goals(user_id, current_goals)
        return jsonify({"success": True})


@app.route('/api/send', methods=['POST'])
def send_message():
    """发送测试消息"""
    try:
        data = request.json
        user_id = data.get('user_id')
        message = data.get('message', '这是一条测试消息')

        if not user_id:
            return jsonify({"success": False, "error": "缺少 user_id"})

        success = wecom_service.send_message(user_id, message)

        return jsonify({
            "success": success,
            "message": "发送成功" if success else "发送失败"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/summary')
def get_summary():
    """获取最新摘要"""
    try:
        user_id = request.args.get('user_id') or WECOM_CONFIG.get("agent_id")

        # 立即生成摘要
        result = scheduler.generate_summary_now()

        if result:
            return jsonify({
                "success": True,
                "data": result
            })
        else:
            return jsonify({"success": False, "error": "生成摘要失败"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/chats')
def get_chats():
    """获取群聊列表"""
    try:
        chats = wecom_service.get_group_chat_list()

        chat_list = []
        for chat in chats:
            chat_list.append({
                "chat_id": chat.get("chatid"),
                "name": chat.get("name", "未知群"),
                "type": chat.get("chat_type", "unknown")
            })

        return jsonify({
            "success": True,
            "data": chat_list
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ========== 启动 ==========

def init_app():
    """初始化应用"""
    print("🚀 初始化 WeCom 助手...")

    # 启动调度器
    scheduler.start()

    print("✅ WeCom 助手已就绪！")


if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
