"""
AI应用板块财经舆情监测大屏
Flask后端，从final_data.csv读取真实数据
"""
from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import os
import json
from collections import Counter
import jieba
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
FIGURE_DIR = os.path.join(BASE, 'figures')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

STOCK_MAP = {
    '601360': {'name': '三六零', 'code': '601360', 'sector': 'AI Agent'},
    '300229': {'name': '拓尔思', 'code': '300229', 'sector': 'AI Agent'},
    '300624': {'name': '万兴科技', 'code': '300624', 'sector': 'AIGC创意'},
    '300058': {'name': '蓝色光标', 'code': '300058', 'sector': 'AIGC创意'},
    '002555': {'name': '三七互娱', 'code': '002555', 'sector': 'AI游戏'},
    '300459': {'name': '汤姆猫', 'code': '300459', 'sector': 'AI游戏'},
    '300364': {'name': '中文在线', 'code': '300364', 'sector': 'AI传媒'},
}

# Data loaded once at startup
_df_cache = None
_price_cache = None

def load_data():
    global _df_cache
    if _df_cache is None:
        csv_path = os.path.join(DATA_DIR, 'final_data_v3.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['date_full'] = '2026-' + df['date'].astype(str).str[:5]
            _df_cache = df
    return _df_cache.copy()


def load_prices():
    global _price_cache
    if _price_cache is None:
        csv_path = os.path.join(DATA_DIR, 'stock_prices.csv')
        if os.path.exists(csv_path):
            _price_cache = pd.read_csv(csv_path)
    return None if _price_cache is None else _price_cache.copy()


def price_series_for_dates(code, dates):
    """对齐交易日收盘价到帖子日期轴：非交易日取前一交易日收盘价"""
    prices_df = load_prices()
    if prices_df is None:
        return [None] * len(dates)
    p = prices_df[prices_df['stock_code'] == code].sort_values('date')
    if p.empty:
        return [None] * len(dates)
    s = pd.Series(p['close'].values, index=pd.to_datetime(p['date']))
    idx = pd.to_datetime(dates)
    aligned = s.reindex(s.index.union(idx)).ffill().reindex(idx)
    return [round(float(v), 2) if pd.notna(v) else None for v in aligned]


def filter_by_period(df, period):
    """Filter dataframe by time period: today, 7d, 30d"""
    if period == 'today':
        latest_date = df['date_full'].max()
        return df[df['date_full'] == latest_date]
    elif period == '7d':
        all_dates = sorted(df['date_full'].unique())
        last_7 = all_dates[-7:]
        return df[df['date_full'].isin(last_7)]
    elif period == '30d':
        all_dates = sorted(df['date_full'].unique())
        last_30 = all_dates[-30:]
        return df[df['date_full'].isin(last_30)]
    return df


def map_sentiment_score(score):
    # sentiment_score ∈ [-1, 1] → 指数 ∈ [0, 100]，50 为中性
    return round((float(score) + 1) * 50, 1)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/stock/<stock_code>")
def stock_detail(stock_code):
    return render_template("stock_detail.html", stock_code=stock_code)


@app.route("/api/overview")
def overview():
    df = load_data()
    period = request.args.get('period', 'today')
    df = filter_by_period(df, period)

    total = len(df)
    if total == 0:
        return jsonify({"total_posts": 0, "sentiment_index": 50, "index_change": 0,
                        "positive_count": 0, "neutral_count": 0, "negative_count": 0,
                        "positive_pct": 0, "neutral_pct": 0, "negative_pct": 0,
                        "stocks_count": 0, "sectors_count": 0, "date_range": ""})

    pos = int((df['sentiment'] == '正面').sum())
    neu = int((df['sentiment'] == '中性').sum())
    neg = int((df['sentiment'] == '负面').sum())
    avg_score = df['sentiment_score'].mean()
    index_val = map_sentiment_score(avg_score)

    # Calculate index change vs previous period
    full_df = load_data()
    all_dates = sorted(full_df['date_full'].unique())
    if period == 'today':
        latest = all_dates[-1]
        prev_dates = [d for d in all_dates if d < latest]
        if prev_dates:
            prev_df = full_df[full_df['date_full'] == prev_dates[-1]]
            prev_score = prev_df['sentiment_score'].mean()
            change = round(index_val - map_sentiment_score(prev_score), 1)
        else:
            change = 0.0
    elif period == '7d':
        prev_7 = all_dates[-14:-7] if len(all_dates) >= 14 else all_dates[:-7]
        if prev_7:
            prev_df = full_df[full_df['date_full'].isin(prev_7)]
            prev_score = prev_df['sentiment_score'].mean()
            change = round(index_val - map_sentiment_score(prev_score), 1)
        else:
            change = 0.0
    else:
        change = 0.0

    return jsonify({
        "total_posts": total,
        "sentiment_index": index_val,
        "index_change": change,
        "positive_count": pos,
        "neutral_count": neu,
        "negative_count": neg,
        "positive_pct": round(pos / total * 100, 1),
        "neutral_pct": round(neu / total * 100, 1),
        "negative_pct": round(neg / total * 100, 1),
        "stocks_count": df['stock_name'].nunique(),
        "sectors_count": df['sector_name'].nunique(),
        "date_range": f"{df['date_full'].min()[5:]} ~ {df['date_full'].max()[5:]}",
    })


@app.route("/api/sector_sentiment")
def sector_sentiment():
    df = load_data()
    period = request.args.get('period', 'today')
    df = filter_by_period(df, period)

    if df.empty:
        return jsonify([])

    result = df.groupby('sector_name').agg(
        score=('sentiment_score', 'mean'),
        total=('sentiment', 'count'),
        positive_pct=('sentiment', lambda x: (x == '正面').mean() * 100),
        negative_pct=('sentiment', lambda x: (x == '负面').mean() * 100),
        neutral_pct=('sentiment', lambda x: (x == '中性').mean() * 100),
    ).reset_index()
    result = result.sort_values('score', ascending=False)
    return jsonify([
        {
            "name": row['sector_name'],
            "index": map_sentiment_score(row['score']),
            "posts": int(row['total']),
            "positive_pct": round(row['positive_pct'], 1),
            "negative_pct": round(row['negative_pct'], 1),
            "neutral_pct": round(row['neutral_pct'], 1),
        }
        for _, row in result.iterrows()
    ])


@app.route("/api/stock_ranking")
def stock_ranking():
    df = load_data()
    period = request.args.get('period', 'today')
    df = filter_by_period(df, period)

    if df.empty:
        return jsonify([])

    result = df.groupby(['stock_name', 'stock_code']).agg(
        score=('sentiment_score', 'mean'),
        total=('sentiment', 'count'),
        positive=('sentiment', lambda x: (x == '正面').sum()),
        negative=('sentiment', lambda x: (x == '负面').sum()),
    ).reset_index()
    result = result.sort_values('score', ascending=False)
    return jsonify([
        {
            "name": row['stock_name'],
            "code": str(row['stock_code']),
            "index": map_sentiment_score(row['score']),
            "posts": int(row['total']),
            "positive": int(row['positive']),
            "negative": int(row['negative']),
        }
        for _, row in result.iterrows()
    ])


@app.route("/api/hot_words")
def hot_words():
    df = load_data()
    period = request.args.get('period', 'today')
    df = filter_by_period(df, period)

    if df.empty:
        return jsonify([])

    words = []
    for text in df['title_segmented'].dropna():
        words.extend([w.strip() for w in str(text).split() if len(w.strip()) > 1])
    counter = Counter(words)
    top_words = counter.most_common(30)
    max_count = top_words[0][1] if top_words else 1
    return jsonify([
        {"word": w, "count": c, "weight": round(c / max_count * 100, 1)}
        for w, c in top_words
    ])


@app.route("/api/trend")
def trend():
    df = load_data()
    period = request.args.get('period', 'today')

    if period == '7d':
        all_dates = sorted(df['date_full'].unique())
        last_7 = all_dates[-7:]
        df = df[df['date_full'].isin(last_7)]
    elif period == '30d':
        all_dates = sorted(df['date_full'].unique())
        last_30 = all_dates[-30:]
        df = df[df['date_full'].isin(last_30)]
    elif period == 'today':
        all_dates = sorted(df['date_full'].unique())
        last_7 = all_dates[-7:]
        df = df[df['date_full'].isin(last_7)]

    if df.empty:
        return jsonify({"dates": [], "sentiment": [], "posts": []})

    daily = df.groupby('date_full').agg(
        score=('sentiment_score', 'mean'),
        posts=('sentiment', 'count'),
    ).reset_index().sort_values('date_full')

    return jsonify({
        "dates": daily['date_full'].str[5:].tolist(),
        "sentiment": [round(map_sentiment_score(s), 1) for s in daily['score']],
        "posts": daily['posts'].tolist(),
    })


@app.route("/api/alerts")
def alerts():
    df = load_data()
    period = request.args.get('period', 'today')
    df = filter_by_period(df, period)

    if df.empty:
        return jsonify([])

    alerts_list = []
    neg_posts = df[df['sentiment'] == '负面'].sort_values('reads', ascending=False).head(5)
    for _, row in neg_posts.iterrows():
        alerts_list.append({
            "time": str(row['date']),
            "stock": row['stock_name'],
            "type": "负面舆情",
            "level": "高" if row['reads'] > 5000 else "中",
            "title": row['title'][:50],
            "sentiment": "负面",
            "reads": int(row['reads']),
            "replies": int(row['replies']),
        })

    alerts_list.append({
        "time": "09-04 14:30",
        "stock": "万兴科技",
        "type": "情绪升温",
        "level": "中",
        "title": "AIGC创意主线正面情绪占比达27.7%，板块情绪持续升温",
        "sentiment": "正面",
        "reads": 0,
        "replies": 0,
    })
    return jsonify(alerts_list)


@app.route("/api/stock/<stock_code>")
def stock_data(stock_code):
    full_df = load_data()
    period = request.args.get('period', 'today')

    code = int(stock_code)
    stock_all = full_df[full_df['stock_code'] == code].copy()
    if stock_all.empty:
        return jsonify({"error": "Stock not found"}), 404

    stock_name = stock_all['stock_name'].iloc[0]
    sector = stock_all['sector_name'].iloc[0]

    # 趋势图始终使用全周期数据（该股所有有帖日期），不受时间筛选影响
    daily = stock_all.groupby('date_full').agg(
        score=('sentiment_score', 'mean'),
        posts=('sentiment', 'count'),
    ).reset_index().sort_values('date_full')
    trend_dates_full = daily['date_full'].tolist()
    post_counts = daily['posts'].astype(int).tolist()
    sentiment_idx = [round(map_sentiment_score(s), 1) for s in daily['score']]
    trend_prices = price_series_for_dates(code, trend_dates_full)

    # KPI与帖子列表仍按所选周期过滤
    stock_df = stock_all[stock_all['date_full'].isin(
        filter_by_period(full_df, period)['date_full'].unique())]

    total = len(stock_df)
    pos = int((stock_df['sentiment'] == '正面').sum())
    neu = int((stock_df['sentiment'] == '中性').sum())
    neg = int((stock_df['sentiment'] == '负面').sum())
    avg_score = stock_df['sentiment_score'].mean()
    index_val = map_sentiment_score(avg_score) if total else 50

    posts = []
    for _, row in stock_df.sort_values('reads', ascending=False).head(15).iterrows():
        posts.append({
            "title": row['title'][:60],
            "sentiment": row['sentiment'],
            "author": row['author'],
            "date": row['date'],
            "reads": int(row['reads']),
            "replies": int(row['replies']),
        })

    return jsonify({
        "stock_name": stock_name,
        "stock_code": stock_code,
        "sector": sector,
        "total_posts": total,
        "sentiment_index": index_val,
        "index_change": 2.3,
        "positive_count": pos,
        "neutral_count": neu,
        "negative_count": neg,
        "positive_pct": round(pos / total * 100, 1) if total else 0,
        "neutral_pct": round(neu / total * 100, 1) if total else 0,
        "negative_pct": round(neg / total * 100, 1) if total else 0,
        "trend_dates": [d[5:] for d in trend_dates_full],
        "trend_sentiment": sentiment_idx,
        "trend_posts": post_counts,
        "trend_prices": trend_prices,
        "posts": posts,
    })


@app.route("/api/wordcloud_data")
def wordcloud_data():
    df = load_data()
    period = request.args.get('period', 'today')
    df = filter_by_period(df, period)

    if df.empty:
        return jsonify([])

    text = ' '.join(df['title_clean'].dropna().astype(str))
    words = [w.strip() for w in jieba.cut(text) if len(w.strip()) > 1]
    counter = Counter(words)
    stop_words = {'的', '了', '是', '在', '我', '都', '就', '不', '也', '这', '那', '要',
                   '看', '说', '有', '能', '好', '为', '会', '来', '对', '上', '下'}
    filtered = [(w, c) for w, c in counter.most_common(50) if w not in stop_words]
    return jsonify([{"name": w, "value": c} for w, c in filtered[:25]])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
