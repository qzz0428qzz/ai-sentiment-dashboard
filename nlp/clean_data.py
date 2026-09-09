"""
数据清洗V2：股吧帖子适度过滤
策略：
1. 确认stock_code正确映射
2. 过滤纯水帖（标题<5字、纯符号数字、全是水词）
3. 过滤明显不相关的帖子（标题完全在说别的股票/公司）
4. 保留有实质内容的帖子
"""
import pandas as pd
import re
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')

STOCK_MAP = {
    '601360': {'name': '三六零', 'sector': 'AI Agent'},
    '300229': {'name': '拓尔思', 'sector': 'AI Agent'},
    '300624': {'name': '万兴科技', 'sector': 'AIGC创意'},
    '300058': {'name': '蓝色光标', 'sector': 'AIGC创意'},
    '002555': {'name': '三七互娱', 'sector': 'AI游戏'},
    '300459': {'name': '汤姆猫', 'sector': 'AI游戏'},
    '300364': {'name': '中文在线', 'sector': 'AI传媒'},
}

# 其他股票名称（用来检测明显跑题的帖子）
OTHER_STOCKS = ['贵州茅台', '宁德时代', '比亚迪', '腾讯', '阿里', '百度', '京东', '美团',
                '小米', '华为', '苹果', '特斯拉', '英伟达', '微软', '谷歌', '亚马逊',
                '万科', '保利', '平安', '招行', '工行', '建行', '中石油', '中石化',
                '宇树科技', '新易盛', '中际旭创', '天孚通信', '工业富联',
                '易点天下', '光线传媒', '华策影视', '芒果超媒', '完美世界', '吉比特',
                '昆仑万维', '科大讯飞', '寒武纪', '海光信息', '龙芯',
                '中文传媒', '出版传媒', '浙数文化', '人民网', '新华网']

# 纯水帖关键词组合（标题去掉股票名后只剩这些）
EMPTY_PATTERNS = [
    r'^[转发顶赞][\s\！\!\。\.\，\,]*$',
    r'^沙发板凳路过围观看看$',
    r'^[冲加油支持同意好不错顶赞][\s\！\!\。\.]+$',
    r'^[\d\s\.\,\!\?\。\，\！\？\~\~\-]+$',
    r'^今天明天昨天周[一二三四五六日]早盘午盘尾盘盘前盘后$',
]


def clean_text(text):
    if not isinstance(text, str):
        return ''
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_water_post(title):
    """判断是否是水帖"""
    if not title or len(title) < 4:
        return True
    # 纯数字符号
    if re.match(r'^[\d\s\.\,\!\?\。\，\！\？\~\~\-\_\=\+\*\@\#\$\%\^\&\(\)\[\]\{\}\;\:\'\"\\\|\/]+$', title):
        return True
    # 单字重复
    if len(set(title)) <= 2 and len(title) > 5:
        return True
    return False


def is_off_topic(title, stock_code):
    """判断是否明显跑题（在说别的股票）"""
    info = STOCK_MAP.get(str(stock_code).zfill(6))
    if not info:
        return True
    title_lower = title.lower()
    stock_name = info['name'].lower()

    # 检查是否提到了其他股票名称，且没有提到本股票
    has_other = False
    for other in OTHER_STOCKS:
        if other.lower() in title_lower:
            has_other = True
            break

    if has_other and stock_name not in title_lower:
        return True

    return False


def run_clean():
    print("=" * 60)
    print("数据清洗V2：适度过滤")
    print("=" * 60)

    df = pd.read_csv(os.path.join(DATA_DIR, 'guba_posts.csv'))
    print(f"\n原始数据: {len(df)} 条")

    # 清洗标题
    df['title'] = df['title'].apply(clean_text)

    # stock_code格式化
    df['stock_code'] = df['stock_code'].astype(str).str.zfill(6)

    # 映射名称和行业
    df['stock_name'] = df['stock_code'].map(lambda x: STOCK_MAP.get(x, {}).get('name', ''))
    df['sector_name'] = df['stock_code'].map(lambda x: STOCK_MAP.get(x, {}).get('sector', ''))

    # 过滤无效映射
    df = df[df['stock_name'] != ''].reset_index(drop=True)
    print(f"有效映射: {len(df)} 条")

    # 去重
    before = len(df)
    df = df.drop_duplicates(subset=['post_id']).reset_index(drop=True)
    print(f"去重后: {len(df)} 条 (去掉{before-len(df)}条重复)")

    # 过滤水帖
    water_mask = df['title'].apply(is_water_post)
    df = df[~water_mask].reset_index(drop=True)
    print(f"过滤水帖后: {len(df)} 条")

    # 过滤明显跑题
    off_mask = df.apply(lambda r: is_off_topic(r['title'], r['stock_code']), axis=1)
    off_count = off_mask.sum()
    df = df[~off_mask].reset_index(drop=True)
    print(f"过滤跑题帖后: {len(df)} 条 (去掉{off_count}条明显跑题)")

    print(f"\n各股票帖子数:")
    counts = df.groupby('stock_name').size().sort_values(ascending=False)
    for name, cnt in counts.items():
        print(f"  {name}: {cnt} 条")

    # 中文在线数据少，检查一下
    zwzx = df[df['stock_name'] == '中文在线']
    print(f"\n中文在线样例（前10条）:")
    for i, row in zwzx.head(10).iterrows():
        print(f"  [{i}] {row['title'][:60]}")

    # 保存
    df.to_csv(os.path.join(DATA_DIR, 'clean_posts.csv'), index=False, encoding='utf-8-sig')
    print(f"\n已保存: data/clean_posts.csv ({len(df)}条)")
    return df


if __name__ == '__main__':
    run_clean()
