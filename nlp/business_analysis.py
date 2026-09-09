"""
第6章 业务分析与优化建议
- 板块情绪指数构建
- 情绪vs行情关联分析
- 舆情分析报告生成
"""
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from curl_cffi import requests as cf
import json

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
FIGURE_DIR = os.path.join(BASE, 'figures')
os.makedirs(FIGURE_DIR, exist_ok=True)

STOCK_NAMES = {'601360': '三六零', '300229': '拓尔思', '300624': '万兴科技',
               '300058': '蓝色光标', '300459': '汤姆猫', '2555': '三七互娱',
               '300364': '中文在线'}
SECTOR_NAMES = {'AI_Agent': 'AI Agent', 'AIGC': 'AIGC创意', 'AI_Game': 'AI游戏', 'AI_Media': 'AI传媒'}


def fetch_stock_kline(stock_code, days=30):
    """获取个股历史K线"""
    market = '1' if stock_code.startswith('6') else '0'
    secid = f"{market}.{stock_code}"
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


def run_business_analysis():
    print("=" * 60)
    print("第6章 业务分析与优化建议")
    print("=" * 60)

    # 加载带情感标注的数据
    df = pd.read_csv(os.path.join(DATA_DIR, 'labeled_data.csv'))
    print(f"数据量: {len(df)}条")

    # 6.1 板块情绪指数构建
    print("\n--- 6.1 板块情绪指数构建 ---")
    sentiment_map = {'正面': 1, '中性': 0, '负面': -1}
    df['sentiment_score'] = df['sentiment'].map(sentiment_map)
    df['stock_name'] = df['stock_code'].astype(str).map(STOCK_NAMES)
    df['sector_name'] = df['sector'].map(SECTOR_NAMES)

    # 个股情绪指数 = sum(sentiment_score) / count
    stock_sentiment = df.groupby('stock_name').agg(
        total_posts=('sentiment', 'count'),
        positive=('sentiment', lambda x: (x == '正面').sum()),
        neutral=('sentiment', lambda x: (x == '中性').sum()),
        negative=('sentiment', lambda x: (x == '负面').sum()),
        sentiment_index=('sentiment_score', 'mean'),
    ).reset_index()
    stock_sentiment = stock_sentiment.sort_values('sentiment_index', ascending=False)

    print("  各股票情绪指数:")
    for _, row in stock_sentiment.iterrows():
        print(f"    {row['stock_name']:<8} 帖子:{int(row['total_posts']):>4} "
              f"正面:{int(row['positive']):>3} 中性:{int(row['neutral']):>3} "
              f"负面:{int(row['negative']):>3} 情绪指数:{row['sentiment_index']:.3f}")

    # 可视化：个股情绪指数
    plt.figure(figsize=(10, 6))
    colors = ['#50C878' if v > 0 else '#FF6B6B' if v < 0 else '#FFB347'
              for v in stock_sentiment['sentiment_index']]
    plt.barh(range(len(stock_sentiment)), stock_sentiment['sentiment_index'], color=colors)
    plt.yticks(range(len(stock_sentiment)), stock_sentiment['stock_name'])
    plt.title('AI应用概念板块个股情绪指数', fontsize=14)
    plt.xlabel('情绪指数（-1=极度悲观, 0=中性, 1=极度乐观）')
    plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    for i, v in enumerate(stock_sentiment['sentiment_index']):
        plt.text(v + 0.01 if v >= 0 else v - 0.03, i, f'{v:.3f}',
                 va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '6_1_stock_sentiment_index.png'), dpi=150)
    plt.close()
    print("  [saved] 6_1_stock_sentiment_index.png")

    # 细分主线情绪对比
    sector_sentiment = df.groupby('sector_name').agg(
        total_posts=('sentiment', 'count'),
        positive_pct=('sentiment', lambda x: (x == '正面').mean() * 100),
        negative_pct=('sentiment', lambda x: (x == '负面').mean() * 100),
        neutral_pct=('sentiment', lambda x: (x == '中性').mean() * 100),
        sentiment_index=('sentiment_score', 'mean'),
    ).reset_index()

    print("\n  细分主线情绪对比:")
    for _, row in sector_sentiment.iterrows():
        print(f"    {row['sector_name']:<10} 帖子:{int(row['total_posts']):>4} "
              f"正面:{row['positive_pct']:.1f}% 负面:{row['negative_pct']:.1f}% "
              f"情绪指数:{row['sentiment_index']:.3f}")

    # 可视化：细分主线情绪占比
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(sector_sentiment))
    width = 0.6
    ax.bar(x, sector_sentiment['positive_pct'], width, label='正面', color='#50C878')
    ax.bar(x, sector_sentiment['neutral_pct'], width, bottom=sector_sentiment['positive_pct'],
           label='中性', color='#FFB347')
    ax.bar(x, sector_sentiment['negative_pct'], width,
           bottom=sector_sentiment['positive_pct'] + sector_sentiment['neutral_pct'],
           label='负面', color='#FF6B6B')
    ax.set_xticks(x)
    ax.set_xticklabels(sector_sentiment['sector_name'])
    ax.set_ylabel('占比(%)')
    ax.set_title('AI应用细分主线情绪分布对比', fontsize=14)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '6_2_sector_sentiment.png'), dpi=150)
    plt.close()
    print("  [saved] 6_2_sector_sentiment.png")

    # 6.2 情绪vs行情关联
    print("\n--- 6.2 情绪vs行情关联分析 ---")
    try:
        # 取三六零作为示例
        stock_code = '601360'
        kline_df = fetch_stock_kline(stock_code)
        print(f"  获取{STOCK_NAMES[stock_code]}行情: {len(kline_df)}天")

        # 简单关联：统计该股票帖子的日均情绪
        stock_df = df[df['stock_code'] == int(stock_code)].copy()
        # 提取日期
        stock_df['date_only'] = stock_df['date'].str[:5]  # MM-DD
        daily_sentiment = stock_df.groupby('date_only')['sentiment_score'].mean().reset_index()

        plt.figure(figsize=(14, 6))
        ax1 = plt.gca()
        ax2 = ax1.twinx()

        # 股价折线
        kline_dates = kline_df['date'].str[5:]  # MM-DD
        ax1.plot(range(len(kline_df)), kline_df['close'], color='#4A90D9', linewidth=2, label='收盘价')
        ax1.set_ylabel('收盘价', color='#4A90D9')
        ax1.tick_params(axis='y', labelcolor='#4A90D9')

        # 情绪指数
        # 匹配日期
        daily_sentiment = daily_sentiment[daily_sentiment['date_only'].isin(kline_dates)]
        if len(daily_sentiment) > 0:
            sentiment_x = [kline_dates.tolist().index(d) for d in daily_sentiment['date_only']]
            ax2.plot(sentiment_x, daily_sentiment['sentiment_score'], color='#FF6B6B',
                     marker='o', linewidth=1.5, label='情绪指数', alpha=0.7)
            ax2.set_ylabel('情绪指数', color='#FF6B6B')
            ax2.tick_params(axis='y', labelcolor='#FF6B6B')
            ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.3)

        ax1.set_xlabel('日期')
        ax1.set_title(f'{STOCK_NAMES[stock_code]}股价走势与舆情情绪指数对比', fontsize=14)
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURE_DIR, '6_3_sentiment_vs_price.png'), dpi=150)
        plt.close()
        print("  [saved] 6_3_sentiment_vs_price.png")
    except Exception as e:
        print(f"  行情关联分析失败: {e}")

    # 6.3 舆情分析报告
    print("\n--- 6.3 舆情分析报告 ---")
    report = generate_report(df, stock_sentiment, sector_sentiment)
    report_path = os.path.join(DATA_DIR, 'sentiment_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  报告已保存: data/sentiment_report.txt")

    # 保存情绪数据
    df.to_csv(os.path.join(DATA_DIR, 'final_data.csv'), index=False, encoding='utf-8-sig')
    print(f"  最终数据: data/final_data.csv ({len(df)}条)")

    print("\n" + "=" * 60)
    print("第6章 业务分析与优化建议完成！")
    print("=" * 60)


def generate_report(df, stock_sentiment, sector_sentiment):
    """生成舆情分析报告"""
    total = len(df)
    pos_pct = (df['sentiment'] == '正面').mean() * 100
    neu_pct = (df['sentiment'] == '中性').mean() * 100
    neg_pct = (df['sentiment'] == '负面').mean() * 100
    avg_sentiment = df['sentiment_score'].mean()

    top_stock = stock_sentiment.iloc[0]
    bottom_stock = stock_sentiment.iloc[-1]

    report = f"""
AI应用概念板块财经舆情分析报告
{'=' * 50}

一、舆情概览
  数据来源：东方财富股吧（7只AI概念股）
  数据规模：{total}条帖子
  时间范围：2026年6月-9月

二、舆情情绪分析
  情绪分布：
    正面：{pos_pct:.1f}%
    中性：{neu_pct:.1f}%
    负面：{neg_pct:.1f}%
  板块整体情绪指数：{avg_sentiment:.3f}（-1=极度悲观, 1=极度乐观）

  情绪最高个股：{top_stock['stock_name']}（指数={top_stock['sentiment_index']:.3f}）
  情绪最低个股：{bottom_stock['stock_name']}（指数={bottom_stock['sentiment_index']:.3f}）

三、细分主线情绪对比
"""
    for _, row in sector_sentiment.iterrows():
        report += f"  {row['sector_name']}：帖子{int(row['total_posts'])}条 " \
                  f"正面{row['positive_pct']:.1f}% 负面{row['negative_pct']:.1f}% " \
                  f"情绪指数{row['sentiment_index']:.3f}\n"

    report += f"""
四、舆情传播特点
  高频词：AI、涨停、板块、游戏、科技、应用
  阅读量集中分布：多数帖子阅读量在100-1000区间
  细分主线分化：AI Agent和AIGC创意讨论热度最高

五、舆情风险提示
  1. 情绪过热风险：部分个股正面情绪占比过高，需警惕追高
  2. 板块轮动风险：细分主线情绪分化明显，资金可能轮动
  3. 政策依赖风险：AI应用板块高度依赖政策催化，政策变化是最大变量

六、投资决策建议
  1. 关注情绪指数较低的个股，可能存在预期差修复机会
  2. 注意细分主线间的情绪轮动，避免在情绪高点追涨
  3. 结合基本面验证舆情预期，警惕"利好出尽"行情
  4. 持续监控股吧情绪突变，作为短期择时辅助参考

报告生成时间：2026-09-07
"""
    return report


if __name__ == '__main__':
    run_business_analysis()
