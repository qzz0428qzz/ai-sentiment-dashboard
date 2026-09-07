"""
东方财富股吧评论爬虫
采集AI应用板块个股的股吧帖子标题与内容
"""
from curl_cffi import requests as cf
import re
import time
import random
import csv
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://guba.eastmoney.com/",
}

# AI应用板块代表个股
STOCKS = {
    "AI_Agent": ["601360", "300229"],
    "AIGC": ["300624", "300058"],
    "AI_Game": ["300459", "002555"],
    "AI_Media": ["300364", "300133"],
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def get_post_list(stock_code, page=1):
    """获取股吧帖子列表"""
    url = f"https://guba.eastmoney.com/list,{stock_code}_{page}.html"
    r = cf.get(url, headers=HEADERS, timeout=15, impersonate="chrome")
    items = re.findall(r'<tr class="listitem">(.*?)</tr>', r.text, re.S)
    posts = []
    for item in items:
        post_id = re.search(r'data-postid="(\d+)"', item)
        title = re.search(r'data-postid="[^"]*"[^>]*>(.*?)</a>', item)
        author = re.search(r'class="author"><a[^>]*>(.*?)</a>', item)
        date = re.search(r'class="update">(.*?)</div>', item)
        read_count = re.search(r'class="read">(.*?)</div>', item)
        reply_count = re.search(r'class="reply">(.*?)</div>', item)
        if post_id and title:
            posts.append({
                "stock_code": stock_code,
                "post_id": post_id.group(1),
                "title": re.sub(r'<[^>]+>', '', title.group(1)).strip(),
                "author": author.group(1) if author else "",
                "date": date.group(1).strip() if date else "",
                "reads": read_count.group(1).strip() if read_count else "0",
                "replies": reply_count.group(1).strip() if reply_count else "0",
            })
    return posts


def get_post_content(stock_code, post_id):
    """获取帖子正文内容"""
    url = f"https://guba.eastmoney.com/news,{stock_code},{post_id}.html"
    r = cf.get(url, headers=HEADERS, timeout=15, impersonate="chrome")
    # 帖子内容在 <div class="stockcodecckdend"> 或 <div id="post_content">
    content = re.search(r'<div class="stockcodecckdend">(.*?)</div>', r.text, re.S)
    if not content:
        content = re.search(r'id="post_content"[^>]*>(.*?)</div>', r.text, re.S)
    if content:
        text = re.sub(r'<[^>]+>', '', content.group(1)).strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    return ""


def crawl_stock(stock_code, max_pages=5):
    """爬取单只股票的股吧帖子"""
    all_posts = []
    for page in range(1, max_pages + 1):
        print(f"  第{page}页...")
        posts = get_post_list(stock_code, page)
        if not posts:
            print(f"  第{page}页无数据，停止")
            break
        all_posts.extend(posts)
        time.sleep(random.uniform(1, 2))
    return all_posts


def crawl_all(max_pages=5):
    """爬取所有股票"""
    all_data = []
    for sector, stocks in STOCKS.items():
        for stock in stocks:
            print(f"\n[{sector}] 爬取 {stock}...")
            posts = crawl_stock(stock, max_pages)
            print(f"  获取 {len(posts)} 条帖子")
            for p in posts:
                p["sector"] = sector
            all_data.extend(posts)
    return all_data


def save_to_csv(data, filename="guba_posts.csv"):
    """保存到CSV"""
    filepath = os.path.join(DATA_DIR, filename)
    if not data:
        print("无数据可保存")
        return
    keys = data[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"\n保存到 {filepath}, 共 {len(data)} 条")


if __name__ == "__main__":
    print("=== 股吧帖子爬虫 ===")
    data = crawl_all(max_pages=5)
    save_to_csv(data)
    # 打印前10条
    print("\n=== 前10条帖子 ===")
    for p in data[:10]:
        print(f"[{p['sector']}] {p['stock_code']} | {p['title'][:30]} | {p['date']} | 阅读{p['reads']}")
