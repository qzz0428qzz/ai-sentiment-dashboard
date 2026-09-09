"""
修复三张图表:
- 6_1_stock_sentiment_index.png (个股情绪指数) - 确保数据完整显示
- 6_2_sector_sentiment.png (细分主线情绪对比) - 修正数据异常
- 6_3_sentiment_vs_price.png (情绪指数与股价走势) - 重新计算生成
"""
import pandas as pd
import numpy as np
import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from curl_cffi import requests as cf

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
FIGURE_DIR = os.path.join(BASE, 'figures')
os.makedirs(FIGURE_DIR, exist_ok=True)

STOCK_NAMES = {'601360': '三六零', '300229': '拓尔思', '300624': '万兴科技',
               '300058': '蓝色光标', '300459': '汤姆猫', '002555': '三七互娱',
               '300364': '中文在线'}
SECTOR_NAMES = {'AI_Agent': 'AI Agent', 'AIGC': 'AIGC创意', 'AI_Game': 'AI游戏', 'AI_Media': 'AI传媒'}


def fix_chart_6_1(df):
    """图6-4 个股情绪指数 - 确保数据完整显示"""
    print("--- 修复 6_1_stock_sentiment_index.png ---")

    sentiment_map = {'正面': 1, '中性': 0, '负面': -1}
    df['sentiment_score'] = df['sentiment'].map(sentiment_map)

    stock_sentiment = df.groupby('stock_name').agg(
        total_posts=('sentiment', 'count'),
        positive=('sentiment', lambda x: (x == '正面').sum()),
        neutral=('sentiment', lambda x: (x == '中性').sum()),
        negative=('sentiment', lambda x: (x == '负面').sum()),
        sentiment_index=('sentiment_score', 'mean'),
    ).reset_index()
    stock_sentiment = stock_sentiment.sort_values('sentiment_index', ascending=True)

    print("  各股票情绪指数:")
    for _, row in stock_sentiment.iterrows():
        print(f"    {row['stock_name']:<8} 帖子:{int(row['total_posts']):>4} "
              f"正面:{int(row['positive']):>3} 中性:{int(row['neutral']):>3} "
              f"负面:{int(row['negative']):>3} 情绪指数:{row['sentiment_index']:.3f}")

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#50C878' if v > 0 else '#FF6B6B' if v < 0 else '#FFB347'
              for v in stock_sentiment['sentiment_index']]
    bars = ax.barh(range(len(stock_sentiment)), stock_sentiment['sentiment_index'],
                   color=colors, edgecolor='#333333', linewidth=0.5, height=0.6)

    ax.set_yticks(range(len(stock_sentiment)))
    ax.set_yticklabels(stock_sentiment['stock_name'], fontsize=12)
    ax.set_xlabel('情绪指数（-1=极度悲观, 0=中性, 1=极度乐观）', fontsize=11)
    ax.set_title('AI应用概念板块个股情绪指数', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlim(-0.02, 0.28)

    for i, (v, posts) in enumerate(zip(stock_sentiment['sentiment_index'],
                                        stock_sentiment['total_posts'])):
        ax.text(v + 0.005, i, f'{v:.3f} (n={int(posts)})', va='center', fontsize=10,
                fontweight='bold')

    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '6_1_stock_sentiment_index.png'), dpi=150)
    plt.close()
    print("  [saved] 6_1_stock_sentiment_index.png")


def fix_chart_6_2(df):
    """图6-5 细分主线情绪对比 - 修正数据异常"""
    print("\n--- 修复 6_2_sector_sentiment.png ---")

    sentiment_map = {'正面': 1, '中性': 0, '负面': -1}
    df['sentiment_score'] = df['sentiment'].map(sentiment_map)
    df['sector_name'] = df['sector'].map(SECTOR_NAMES)

    sector_sentiment = df.groupby('sector_name').agg(
        total_posts=('sentiment', 'count'),
        positive_pct=('sentiment', lambda x: (x == '正面').mean() * 100),
        negative_pct=('sentiment', lambda x: (x == '负面').mean() * 100),
        neutral_pct=('sentiment', lambda x: (x == '中性').mean() * 100),
        sentiment_index=('sentiment_score', 'mean'),
    ).reset_index()
    sector_sentiment = sector_sentiment.sort_values('sentiment_index', ascending=False)

    print("  细分主线情绪对比:")
    for _, row in sector_sentiment.iterrows():
        print(f"    {row['sector_name']:<10} 帖子:{int(row['total_posts']):>4} "
              f"正面:{row['positive_pct']:.1f}% 中性:{row['neutral_pct']:.1f}% "
              f"负面:{row['negative_pct']:.1f}% 情绪指数:{row['sentiment_index']:.3f}")

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(sector_sentiment))
    width = 0.55

    bars_pos = ax.bar(x, sector_sentiment['positive_pct'], width, label='正面', color='#50C878', edgecolor='#333333', linewidth=0.5)
    bars_neu = ax.bar(x, sector_sentiment['neutral_pct'], width, bottom=sector_sentiment['positive_pct'],
                      label='中性', color='#FFB347', edgecolor='#333333', linewidth=0.5)
    bars_neg = ax.bar(x, sector_sentiment['negative_pct'], width,
                      bottom=sector_sentiment['positive_pct'] + sector_sentiment['neutral_pct'],
                      label='负面', color='#FF6B6B', edgecolor='#333333', linewidth=0.5)

    for i, row in sector_sentiment.iterrows():
        idx = list(sector_sentiment.index).index(i)
        ax.text(idx, row['positive_pct'] / 2, f"{row['positive_pct']:.1f}%",
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax.text(idx, row['positive_pct'] + row['neutral_pct'] / 2, f"{row['neutral_pct']:.1f}%",
                ha='center', va='center', fontsize=8, color='#333333')
        if row['negative_pct'] > 3:
            ax.text(idx, row['positive_pct'] + row['neutral_pct'] + row['negative_pct'] / 2,
                    f"{row['negative_pct']:.1f}%", ha='center', va='center', fontsize=8, color='white')
        ax.text(idx, 105, f"情绪指数: {row['sentiment_index']:.3f}\n帖子数: {int(row['total_posts'])}",
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(sector_sentiment['sector_name'], fontsize=12)
    ax.set_ylabel('占比(%)', fontsize=11)
    ax.set_title('AI应用细分主线情绪分布对比', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(0, 125)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '6_2_sector_sentiment.png'), dpi=150)
    plt.close()
    print("  [saved] 6_2_sector_sentiment.png")


def fetch_stock_kline(stock_code):
    """获取个股历史K线"""
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
    elif stock_code.startswith('0'):
        secid = f"0.{stock_code}"
    elif stock_code.startswith('3'):
        secid = f"0.{stock_code}"
    else:
        secid = f"0.{stock_code}"

    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
        "klt": "101",
        "fqt": "1",
        "beg": "20260601",
        "end": "20260907",
    }
    r = cf.get(url, params=params, timeout=15, impersonate="chrome")
    data = json.loads(r.text)
    klines = data.get("data", {}).get("klines", [])
    records = []
    for k in klines:
        parts = k.split(",")
        records.append({
            'date': parts[0],
            'open': float(parts[1]),
            'close': float(parts[2]),
            'high': float(parts[3]),
            'low': float(parts[4]),
            'volume': float(parts[5]),
        })
    return pd.DataFrame(records)


def fix_chart_6_3(df):
    """图6-6 情绪指数与股价走势对比 - 重新计算生成
    使用全部股票的情绪数据(而非仅三六零)以增加数据覆盖日期数
    """
    print("\n--- 修复 6_3_sentiment_vs_price.png ---")

    sentiment_map = {'正面': 1, '中性': 0, '负面': -1}
    df['sentiment_score'] = df['sentiment'].map(sentiment_map)

    stock_code = '601360'
    stock_name = STOCK_NAMES.get(stock_code, stock_code)

    try:
        kline_df = fetch_stock_kline(stock_code)
        print(f"  获取{stock_name}行情: {len(kline_df)}天")
    except Exception as e:
        print(f"  获取行情数据失败: {e}")
        return

    all_daily = df.copy()
    all_daily['date_full'] = '2026-' + all_daily['date'].str[:5]
    daily_sentiment = all_daily.groupby('date_full').agg(
        sentiment_score=('sentiment_score', 'mean'),
        post_count=('sentiment', 'count')
    ).reset_index()
    daily_sentiment = daily_sentiment.sort_values('date_full')

    print(f"  全板块有情绪数据的日期数: {len(daily_sentiment)}")

    kline_df = kline_df.sort_values('date').reset_index(drop=True)

    merged = pd.merge(kline_df[['date', 'close']], daily_sentiment,
                      left_on='date', right_on='date_full', how='left')
    merged['sentiment_score'] = merged['sentiment_score'].fillna(np.nan)
    merged['post_count'] = merged['post_count'].fillna(0).astype(int)

    merged['sentiment_7d'] = merged['sentiment_score'].rolling(window=7, min_periods=1).mean()
    merged['sentiment_interp'] = merged['sentiment_score'].interpolate(method='linear', limit=5)

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()

    x = range(len(merged))

    ax1.plot(x, merged['close'], color='#E74C3C', linewidth=2.5, label='三六零收盘价(元)', zorder=3)
    ax1.fill_between(x, merged['close'], alpha=0.08, color='#E74C3C')
    ax1.set_ylabel('收盘价（元）', color='#E74C3C', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#E74C3C')

    has_sentiment = merged['sentiment_score'].notna()
    if has_sentiment.any():
        sentiment_x = [i for i, v in enumerate(has_sentiment) if v]
        sentiment_y = [merged['sentiment_score'].iloc[i] for i in sentiment_x]
        sizes = [30 + merged['post_count'].iloc[i] * 0.8 for i in sentiment_x]
        ax2.scatter(sentiment_x, sentiment_y, color='#2ECC71', s=sizes, zorder=5,
                    label='当日板块情绪指数', edgecolors='#27AE60', linewidth=1, alpha=0.8)

    valid_interp = merged['sentiment_interp'].notna()
    if valid_interp.any():
        ax2.plot(x, merged['sentiment_interp'], color='#2ECC71', linewidth=1.5, linestyle='-',
                 alpha=0.5, label='情绪指数(插值平滑)', zorder=4)

    ax2.set_ylabel('板块情绪指数', color='#2ECC71', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='#2ECC71')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
    ax2.set_ylim(-0.4, 0.5)

    tick_step = max(1, len(merged) // 12)
    tick_positions = list(range(0, len(merged), tick_step))
    tick_labels = [merged['date'].iloc[i][5:] for i in tick_positions]
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=30, ha='right', fontsize=9)

    ax1.set_xlabel('日期', fontsize=11)
    ax1.set_title(f'{stock_name}股价走势与板块舆情情绪指数对比', fontsize=14, fontweight='bold')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9,
               framealpha=0.9)

    ax1.grid(axis='y', alpha=0.2, linestyle='--')
    ax1.set_axisbelow(True)

    data_start = merged['sentiment_score'].first_valid_index()
    if data_start is not None:
        ax1.axvspan(data_start, len(merged), alpha=0.05, color='#2ECC71', zorder=1)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '6_3_sentiment_vs_price.png'), dpi=150)
    plt.close()
    print("  [saved] 6_3_sentiment_vs_price.png")


if __name__ == '__main__':
    df = pd.read_csv(os.path.join(DATA_DIR, 'final_data.csv'))
    print(f"加载数据: {len(df)}条")

    fix_chart_6_1(df)
    fix_chart_6_2(df)
    fix_chart_6_3(df)

    print("\n=== 三张图表修复完成 ===")
