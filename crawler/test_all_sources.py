"""
测试所有数据源可用性
"""
from curl_cffi import requests as cf
import json
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://data.eastmoney.com/",
}

print("=" * 60)
print("1. 东方财富-资讯/新闻")
print("=" * 60)
try:
    url = "https://search-api-web.eastmoney.com/search/jsonp"
    params = {
        "cb": "jQuery",
        "param": json.dumps({"uid": "", "keyword": "AI应用", "type": ["cmsArticleWebOld"], "client": "web", "clientType": "web", "clientVersion": "curr", "param": {"cmsArticleWebOld": {"sort": "dt", "pageIndex": 1, "pageSize": 10, "preTag": "", "postTag": ""}}}),
    }
    r = cf.get(url, params=params, headers=HEADERS, timeout=15, impersonate="chrome")
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    print(f"Response: {r.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

time.sleep(random.uniform(1, 2))

print("\n" + "=" * 60)
print("2. 东方财富-个股实时行情")
print("=" * 60)
try:
    # 601360=三六零 300229=拓尔思
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": "1.601360",
        "fields": "f57,f58,f43,f170,f169,f171,f47,f48,f60,f168,f161,f162",
    }
    r = cf.get(url, params=params, headers=HEADERS, timeout=15, impersonate="chrome")
    data = json.loads(r.text)
    d = data.get("data", {})
    print(f"股票: {d.get('f57')} {d.get('f58')}")
    print(f"最新价: {d.get('f43')}")
    print(f"涨跌幅: {d.get('f170')}%")
    print(f"成交额: {d.get('f47')}")
    print(f"换手率: {d.get('f168')}%")
    print(f"市盈率: {d.get('f162')}")
except Exception as e:
    print(f"Error: {e}")

time.sleep(random.uniform(1, 2))

print("\n" + "=" * 60)
print("3. 东方财富-主力资金流向")
print("=" * 60)
try:
    url = "https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "secid": "1.601360",
        "lmt": 5,
        "klt": 101,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63",
    }
    r = cf.get(url, params=params, headers=HEADERS, timeout=15, impersonate="chrome")
    data = json.loads(r.text)
    klines = data.get("data", {}).get("klines", [])
    print(f"获取 {len(klines)} 天资金流向数据:")
    for k in klines:
        parts = k.split(",")
        print(f"  日期:{parts[0]} 主力净流入:{parts[1]} 超大单:{parts[2]} 大单:{parts[4]} 中单:{parts[6]} 小单:{parts[8]}")
except Exception as e:
    print(f"Error: {e}")

time.sleep(random.uniform(1, 2))

print("\n" + "=" * 60)
print("4. 东方财富-概念板块行情")
print("=" * 60)
try:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": 5,
        "fs": "b:BK1629 f:!50",
        "fields": "f12,f14,f2,f3,f4,f8",
        "fid": "f3",
        "po": 1,
    }
    r = cf.get(url, params=params, headers=HEADERS, timeout=15, impersonate="chrome")
    data = json.loads(r.text)
    diff = data.get("data", {}).get("diff", {})
    print(f"AI应用板块成分股 Top5:")
    for k, v in diff.items():
        print(f"  {v['f12']} {v['f14']} | 价格:{v.get('f2')} 涨跌幅:{v.get('f3')}% 成交量:{v.get('f4')}")
except Exception as e:
    print(f"Error: {e}")

time.sleep(random.uniform(1, 2))

print("\n" + "=" * 60)
print("5. 东方财富-股吧帖子(已有2480条)")
print("=" * 60)
print("已保存在 data/guba_posts.csv")

time.sleep(random.uniform(1, 2))

print("\n" + "=" * 60)
print("6. 东方财富-资讯快讯")
print("=" * 60)
try:
    url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
    params = {
        "client": "web",
        "biz": "web_news_col",
        "column": "350",
        "order": 1,
        "needInteractData": 0,
        "page_index": 1,
        "page_size": 5,
    }
    r = cf.get(url, params=params, headers=HEADERS, timeout=15, impersonate="chrome")
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

time.sleep(random.uniform(1, 2))

print("\n" + "=" * 60)
print("7. AKShare-个股历史K线")
print("=" * 60)
try:
    import akshare as ak
    df = ak.stock_zh_a_hist(symbol="601360", period="daily", start_date="20260801", end_date="20260907", adjust="qfq")
    print(f"获取 {len(df)} 条K线数据:")
    print(df[["日期", "开盘", "收盘", "最高", "最低", "成交量"]].tail(5).to_string())
except Exception as e:
    print(f"AKShare Error: {e}")
    print("尝试直接API...")
    try:
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": "1.601360",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
            "klt": "101",
            "fqt": "1",
            "beg": "20260801",
            "end": "20260907",
        }
        r = cf.get(url, params=params, headers=HEADERS, timeout=15, impersonate="chrome")
        data = json.loads(r.text)
        klines = data.get("data", {}).get("klines", [])
        print(f"直接API获取 {len(klines)} 条K线:")
        for k in klines[-5:]:
            parts = k.split(",")
            print(f"  日期:{parts[0]} 开:{parts[1]} 收:{parts[2]} 高:{parts[3]} 低:{parts[4]} 量:{parts[5]}")
    except Exception as e2:
        print(f"Direct API Error: {e2}")
