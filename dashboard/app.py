"""
Flask后端 - 舆情监测可视化大屏
"""
from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/sentiment/sector")
def sector_sentiment():
    return jsonify({
        "sector": "AI应用板块",
        "score": 68.5,
        "trend": "上升",
        "main_lines": {
            "AI Agent": 72.3,
            "AIGC创意营销": 75.1,
            "AI游戏": 61.2,
            "AI传媒": 65.4,
        }
    })


@app.route("/api/sentiment/stock")
def stock_ranking():
    return jsonify([
        {"name": "拓尔思", "code": "300229", "score": 78.2, "change": 5.1},
        {"name": "万兴科技", "code": "300624", "score": 75.6, "change": 3.2},
        {"name": "蓝色光标", "code": "300058", "score": 71.4, "change": -1.3},
        {"name": "汤姆猫", "code": "300459", "score": 63.8, "change": 2.7},
        {"name": "中文在线", "code": "300364", "score": 60.2, "change": -0.8},
    ])


@app.route("/api/alerts")
def alerts():
    return jsonify([
        {"time": "2026-08-30 14:23", "stock": "蓝色光标", "type": "情绪突变", "level": "高", "desc": "负面情绪1小时内上升23%"},
        {"time": "2026-08-30 13:15", "stock": "万兴科技", "type": "关键词命中", "level": "中", "desc": "检测到'减持'相关讨论"},
    ])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
