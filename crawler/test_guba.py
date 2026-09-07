"""测试爬取股吧评论"""
from curl_cffi import requests as cf
import re

stock = "601360"  # 三六零
url = f"https://guba.eastmoney.com/list,{stock}_1.html"
r = cf.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Referer": "https://guba.eastmoney.com/"}, timeout=15, impersonate="chrome")
print(f"Status: {r.status_code}, Length: {len(r.text)}")

# 尝试多种方式提取帖子标题
# 方式1: JSON API
api_url = f"https://guba.eastmoney.com/interface/ThreadList?product_code={stock}&page_no=1&page_size=20"
r2 = cf.get(api_url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://guba.eastmoney.com/"}, timeout=15, impersonate="chrome")
print(f"\nAPI Status: {r2.status_code}, Length: {len(r2.text)}")
print(f"API Response: {r2.text[:500]}")

# 方式2: 从HTML提取
titles = re.findall(r'title="(.*?)"', r.text)
post_titles = [t for t in titles if len(t) > 5 and ("跌" in t or "涨" in t or "?" in t or "！" in t or "吗" in t or "看" in t)]
print(f"\nHTML提取到 {len(post_titles)} 个可能的帖子标题:")
for t in post_titles[:10]:
    print(f"  {t}")

# 方式3: 手帖子链接
links = re.findall(r'href="/post,{stock},(\d+).html'.replace("{stock}", stock), r.text)
print(f"\n帖子链接数: {len(links)}")
if links:
    print(f"前5个帖子ID: {links[:5]}")
    # 爬第一个帖子内容
    post_id = links[0]
    post_url = f"https://guba.eastmoney.com/post,{stock},{post_id}.html"
    r3 = cf.get(post_url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://guba.eastmoney.com/"}, timeout=15, impersonate="chrome")
    print(f"帖子页面 Status: {r3.status_code}")
    # 提取帖子内容
    content_match = re.search(r'<div class="stockcodecckdend">(.*?)</div>', r3.text, re.S)
    if content_match:
        content = re.sub(r'<[^>]+>', '', content_match.group(1)).strip()
        print(f"帖子内容: {content[:200]}")
