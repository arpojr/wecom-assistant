# WeCom AI 助手

智能分析企业微信群组消息，自动提取重点和待办事项。

## 功能

- 📊 自动获取群组消息
- 🔍 智能分析重要内容
- 📋 提取待办事项
- 🎯 目标追踪
- ⏰ 定时摘要推送

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python app.py
```

## 配置

在 `config.py` 中配置你的 WeCom API 凭据：

```python
WECOM_CONFIG = {
    "corp_id": "你的企业ID",
    "agent_id": "你的应用AgentId",
    "secret": "你的应用Secret"
}
```
