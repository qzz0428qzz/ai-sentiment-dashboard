"""分析股吧页面结构"""
from curl_cffi import requests as cf
import re

stock = "601360"
url = f"https://guba.eastmoney.com/list,{stock}_1.html"
r = cf.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Referer": "https://guba.eastmoney.com/"}, timeout=15, impersonate="chrome")

text = r.text

# 找包含帖子信息的标签
# 尝试找 <a> 标签中包含 post 的链接
post_links = re.findall(r'/post[^"]*', text)
print(f"Post links found: {len(post_links)}")
for p in post_links[:5]:
    print(f"  {p}")

# 找 list_a 或 article 类
list_items = re.findall(r'class="l1[^"]*"', text)
print(f"\nl1 class items: {len(list_items)}")

# 找所有 <a> 标签到 /post 或 /news
all_links = re.findall(r'href="(/[^"]*post[^"]*)"', text)
print(f"\nPost href links: {len(all_links)}")
for l in all_links[:5]:
    print(f"  {l}")

# 找帖子标题 - 可能用 span 或 a 标签
# 试试找 title 属性
title_attrs = re.findall(r'title="([^"]{5,})"', text)
print(f"\nTitle attributes: {len(title_attrs)}")
for t in title_attrs[:10]:
    print(f"  {t}")

# 看看页面有没有用JS加载数据
json_data = re.search(r'var\s+post_list\s*=\s*(\[.*?\]);', text, re.S)
if json_data:
    print(f"\nFound JS post_list data! Length: {len(json_data.group(1))}")
else:
    print("\nNo JS post_list found")

# 找一找 data 属性
data_attrs = re.findall(r'data-[a-z]+="([^"]{10,})"', text)
print(f"\nData attributes: {len(data_attrs)}")

# 搜索关键词看页面里有什么
for keyword in ["帖子", "评论", "回复", "阅读", "l1", "article", "post_list", "thread"]:
    count = text.lower().count(keyword.lower())
    if count > 0:
        print(f"'{keyword}' appears {count} times")

# 输出页面中间一部分看看结构
print("\n=== HTML snippet (chars 5000-6000) ===")
print(text[5000:6000])
