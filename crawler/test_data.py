"""
直接请求东方财富API获取概念板块和成分股
"""
import requests
import pandas as pd
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://data.eastmoney.com/",
}


def get_concept_boards():
    """获取所有概念板块"""
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    all_boards = []
    for page in range(1, 20):
        params = {
            "pn": page,
            "pz": 100,
            "fs": "m:90 t:3",
            "fields": "f12,f14,f3",
            "fid": "f3",
            "po": 1,
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        if data.get("data") is None:
            break
        diff = data["data"].get("diff", {})
        for k, v in diff.items():
            all_boards.append({"板块代码": v["f12"], "板块名称": v["f14"]})
        if len(all_boards) >= data["data"].get("total", 0):
            break
    return pd.DataFrame(all_boards)


def get_board_stocks(board_code):
    """获取某板块成分股"""
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    all_stocks = []
    for page in range(1, 20):
        params = {
            "pn": page,
            "pz": 100,
            "fs": f"b:{board_code} f:!50",
            "fields": "f12,f14,f2",
            "fid": "f3",
            "po": 1,
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        if data.get("data") is None:
            break
        diff = data["data"].get("diff", {})
        for k, v in diff.items():
            all_stocks.append({"股票代码": v["f12"], "股票名称": v["f14"]})
        if len(all_stocks) >= data["data"].get("total", 0):
            break
    return pd.DataFrame(all_stocks)


def get_stock_bar_comments(stock_code, page=1):
    """爬取股吧评论"""
    # 股吧URL格式: https://guba.eastmoney.com/list,{stock_code}_{page}.html
    url = f"https://guba.eastmoney.com/list,{stock_code}_{page}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://guba.eastmoney.com/",
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.encoding = "utf-8"
    return r


if __name__ == "__main__":
    # 1. 找AI相关板块
    print("=== 获取概念板块列表 ===")
    boards = get_concept_boards()
    ai_boards = boards[boards["板块名称"].str.contains("AI|人工智能|智能|机器", na=False)]
    print(ai_boards.to_string())
    print(f"\n共找到 {len(ai_boards)} 个AI相关板块")

    # 2. 获取AI应用板块成分股
    if len(ai_boards) > 0:
        # 找"AI应用"或最接近的
        target = ai_boards[ai_boards["板块名称"].str.contains("AI应用|AI概念", na=False)]
        if len(target) == 0:
            target = ai_boards.head(1)
        code = target.iloc[0]["板块代码"]
        name = target.iloc[0]["板块名称"]
        print(f"\n=== 获取板块成分股: {name} ({code}) ===")
        stocks = get_board_stocks(code)
        print(stocks.to_string())
        print(f"\n共 {len(stocks)} 只成分股")

    # 3. 测试爬股吧评论
    print("\n=== 测试爬取股吧评论 ===")
    test_code = "300229"  # 拓尔思
    print(f"测试股票: {test_code}")
    resp = get_stock_bar_comments(test_code, 1)
    print(f"HTTP状态: {resp.status_code}")
    print(f"页面长度: {len(resp.text)}")
    # 检查是否包含帖子标题
    if "post_title" in resp.text or "class=\"l1\"" in resp.text:
        print("包含帖子内容!")
    else:
        print("页面结构可能需要解析JSON，检查API接口...")
