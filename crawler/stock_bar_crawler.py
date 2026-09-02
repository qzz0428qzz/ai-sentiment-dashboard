"""
东方财富股吧评论爬虫
采集AI应用板块个股的股吧评论数据
"""
import requests
import time
import random
import pandas as pd
from datetime import datetime


class StockBarCrawler:
    def __init__(self):
        self.base_url = "https://guba.eastmoney.com/interf/Interface.aspx"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://guba.eastmoney.com/",
        }
        # AI应用板块代表个股
        self.stock_list = {
            "AI_Agent": ["sz300229", "sz300634"],
            "AIGC": ["sz300624", "sz300058", "sz301171"],
            "AI_Game": ["sz300459", "sz300315"],
            "AI_Media": ["sz300364", "sz300133"],
        }

    def get_comments(self, stock_code, page=1):
        params = {
            "path": f"api/Reply/ReplyList",
            "param": f"code={stock_code}&ps=50&p={page}",
        }
        try:
            time.sleep(random.uniform(1, 3))
            resp = requests.get(
                f"https://guba.eastmoney.com/list,{stock_code}_{page}.html",
                headers=self.headers,
                timeout=10,
            )
            return resp
        except Exception as e:
            print(f"[ERROR] {stock_code} page {page}: {e}")
            return None

    def crawl_all(self, max_pages=20):
        all_data = []
        for sector, stocks in self.stock_list.items():
            for stock in stocks:
                print(f"[INFO] 爬取 {sector} - {stock}")
                for page in range(1, max_pages + 1):
                    resp = self.get_comments(stock, page)
                    if resp is None:
                        break
                    # TODO: 解析评论内容、时间、用户
                    time.sleep(random.uniform(2, 5))
        return all_data


if __name__ == "__main__":
    crawler = StockBarCrawler()
    data = crawler.crawl_all(max_pages=10)
    print(f"采集完成，共 {len(data)} 条记录")
