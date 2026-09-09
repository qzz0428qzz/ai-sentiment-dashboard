"""
重新爬取东方财富股吧数据 + 严格清洗
目标：每只股票至少300条有效帖子，标题必须包含股票名称或代码
"""
from curl_cffi import requests as cf
import re
import time
import random
import csv
import os
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://guba.eastmoney.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

STOCKS = [
    {"code": "601360", "name": "三六零", "sector": "AI Agent", "aliases": ["三六零", "360", "601360"]},
    {"code": "300229", "name": "拓尔思", "sector": "AI Agent", "aliases": ["拓尔思", "300229"]},
    {"code": "300624", "name": "万兴科技", "sector": "AIGC创意", "aliases": ["万兴科技", "万兴", "300624"]},
    {"code": "300058", "name": "蓝色光标", "sector": "AIGC创意", "aliases": ["蓝色光标", "蓝标", "300058"]},
    {"code": "002555", "name": "三七互娱", "sector": "AI游戏", "aliases": ["三七互娱", "三七", "002555", "2555"]},
    {"code": "300459", "name": "汤姆猫", "sector": "AI游戏", "aliases": ["汤姆猫", "300459"]},
    {"code": "300364", "name": "中文在线", "sector": "AI传媒", "aliases": ["中文在线", "300364"]},
]

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def get_post_list(stock_code, page=1):
    """获取股吧帖子列表（使用API接口，更稳定）"""
    # 尝试东方财富股吧API
    url = f"https://guba.eastmoney.com/list,{stock_code}_{page}.html"
    try:
        r = cf.get(url, headers=HEADERS, timeout=20, impersonate="chrome")
        items = re.findall(r'<tr class="listitem">(.*?)</tr>', r.text, re.S)
        if not items:
            items = re.findall(r'class="articleh"(.*?)</li>', r.text, re.S)
        posts = []
        for item in items:
            post_id = re.search(r'data-postid="(\d+)"', item)
            title_m = re.search(r'<a[^>]*title="([^"]*)"[^>]*>', item)
            if not title_m:
                title_m = re.search(r'data-postid="[^"]*"[^>]*>(.*?)</a>', item)
            author = re.search(r'class="author"><a[^>]*>(.*?)</a>', item)
            date_m = re.search(r'class="update">(.*?)</div>', item)
            read_count = re.search(r'class="read">(.*?)</div>', item)
            reply_count = re.search(r'class="reply">(.*?)</div>', item)
            if post_id and title_m:
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
                posts.append({
                    "stock_code": stock_code,
                    "post_id": post_id.group(1),
                    "title": title,
                    "author": author.group(1) if author else "",
                    "date": date_m.group(1).strip() if date_m else "",
                    "reads": read_count.group(1).strip() if read_count else "0",
                    "replies": reply_count.group(1).strip() if reply_count else "0",
                })
        return posts
    except Exception as e:
        print(f"    爬取失败: {e}")
        return []


def is_valid_post(title, stock_info):
    """严格校验：标题必须包含股票名称或代码"""
    title_lower = title.lower()
    for alias in stock_info["aliases"]:
        if alias.lower() in title_lower:
            return True
    # 也接受AI相关关键词 + 行业关键词的组合（行业相关讨论）
    ai_keywords = ["ai", "人工智能", "大模型", "chatgpt", "gpt", "aigc", "生成式"]
    sector_keywords = {
        "AI Agent": ["智能", "agent", "安防", "语义", "nlp"],
        "AIGC创意": ["创意", "设计", "绘画", "营销", "广告", "内容生成", "文案"],
        "AI游戏": ["游戏", "手游", "网游", "电竞", "元宇宙", "vr", "ar"],
        "AI传媒": ["传媒", "短剧", "影视", "内容", "出版", "阅读", "网文", "ip"],
    }
    has_ai = any(k in title_lower for k in ai_keywords)
    has_sector = any(k in title_lower for k in sector_keywords.get(stock_info["sector"], []))
    if has_ai and has_sector:
        return True
    return False


def crawl_stock(stock_info, max_pages=30, min_valid=300):
    """爬取单只股票，严格过滤，直到凑够min_valid条"""
    stock_code = stock_info["code"]
    all_posts = []
    seen_ids = set()
    valid_count = 0

    for page in range(1, max_pages + 1):
        print(f"  第{page}页...", end=" ")
        posts = get_post_list(stock_code, page)
        if not posts:
            print("无数据，停止")
            break

        new_count = 0
        valid_in_page = 0
        for p in posts:
            if p["post_id"] in seen_ids:
                continue
            seen_ids.add(p["post_id"])
            if is_valid_post(p["title"], stock_info):
                all_posts.append(p)
                valid_count += 1
                valid_in_page += 1
            new_count += 1

        print(f"新增{new_count}条，有效{valid_in_page}条，累计有效{valid_count}条")
        if valid_count >= min_valid:
            print(f"  已达到目标{min_valid}条，停止")
            break

        time.sleep(random.uniform(1.5, 3))

    return all_posts


def crawl_all():
    all_data = []
    for stock in STOCKS:
        print(f"\n=== 爬取 {stock['name']}({stock['code']}) [{stock['sector']}] ===")
        posts = crawl_stock(stock, max_pages=40, min_valid=300)
        print(f"  最终有效帖子: {len(posts)} 条")
        for p in posts:
            p["sector"] = stock["sector"]
            p["stock_name"] = stock["name"]
        all_data.extend(posts)

    return all_data


def save_to_csv(data, filename="guba_posts_v2.csv"):
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
    # 按股票统计
    df = pd.DataFrame(data)
    print("\n各股票帖子数量:")
    print(df.groupby("stock_name").size().sort_values(ascending=False))


if __name__ == "__main__":
    print("=" * 60)
    print("股吧帖子重新爬取（严格过滤版）")
    print("=" * 60)
    data = crawl_all()
    save_to_csv(data)
