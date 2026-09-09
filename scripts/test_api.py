import requests

BASE = 'http://127.0.0.1:5000'

for code in ['300364', '601360', '300058', '300229', '300624', '002555', '300459']:
    d = requests.get(f'{BASE}/api/stock/{code}?period=today', timeout=10).json()
    s = d['trend_sentiment']
    p = d['trend_prices']
    print(f"{d['stock_name']}({code}): 今日指数={d['sentiment_index']}, "
          f"趋势{len(s)}点, 指数范围[{min(s)}, {max(s)}], "
          f"股价范围[{min(x for x in p if x)}, {max(x for x in p if x)}]")

ov = requests.get(f'{BASE}/api/overview?period=today', timeout=10).json()
print('\n大盘今日: 指数', ov['sentiment_index'], '| 帖子', ov['total_posts'], '| 区间', ov['date_range'])

sec = requests.get(f'{BASE}/api/sector_sentiment?period=today', timeout=10).json()
for x in sec:
    print(f"  {x['name']}: {x['index']} (n={x['posts']})")

rk = requests.get(f'{BASE}/api/stock_ranking?period=30d', timeout=10).json()
print('\n个股排行(近30日):')
for x in rk:
    print(f"  {x['name']}: {x['index']} (n={x['posts']})")
