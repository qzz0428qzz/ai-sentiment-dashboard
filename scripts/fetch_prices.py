"""
抓取个股日线收盘价（东方财富K线接口），保存到 data/stock_prices.csv
"""
from curl_cffi import requests as cf
import pandas as pd
import time
import random
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')

STOCKS = ['601360', '300229', '300624', '300058', '002555', '300459', '300364']


def secid_of(code):
    return ('1.' if code.startswith('6') else '0.') + code


def fetch_kline(code, beg='20260601', end='20260909'):
    url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
    params = {
        'secid': secid_of(code),
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
        'klt': '101', 'fqt': '1', 'beg': beg, 'end': end,
    }
    r = cf.get(url, params=params, impersonate='chrome', timeout=15)
    data = r.json().get('data') or {}
    rows = []
    for line in data.get('klines', []):
        p = line.split(',')
        rows.append({
            'stock_code': int(code),
            'date': p[0],
            'open': float(p[1]),
            'close': float(p[2]),
            'high': float(p[3]),
            'low': float(p[4]),
            'volume': int(p[5]),
        })
    return rows


def main():
    all_rows = []
    for code in STOCKS:
        rows = fetch_kline(code)
        print(f'{code}: {len(rows)} 个交易日, {rows[0]["date"]} ~ {rows[-1]["date"]}, 最新收盘 {rows[-1]["close"]}')
        all_rows.extend(rows)
        time.sleep(random.uniform(0.5, 1.0))
    df = pd.DataFrame(all_rows)
    out = os.path.join(DATA_DIR, 'stock_prices.csv')
    df.to_csv(out, index=False, encoding='utf-8-sig')
    print(f'已保存 {len(df)} 行 -> {out}')


if __name__ == '__main__':
    main()
