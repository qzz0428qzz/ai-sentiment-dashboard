"""
用清洗后的数据重新生成final_data
- 清洗文本
- jieba分词
- 基于金融情感词典的规则法标注情感
"""
import pandas as pd
import jieba
import re
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')

# 金融领域正面情感词
POSITIVE_WORDS = [
    '涨', '上涨', '大涨', '飙升', '暴涨', '冲高', '拉升', '走强', '走高', '看好',
    '利好', '利多', '盈利', '赚钱', '收益', '增长', '爆发', '起飞', '牛', '牛市',
    '涨停', '大涨', '新高', '突破', '反弹', '回暖', '复苏', '繁荣', '机遇', '机会',
    '看好', '乐观', '积极', '强劲', '出色', '优秀', '超预期', '超预期', '超跌反弹',
    '加仓', '满仓', '抄底', '低吸', '买入', '买进', '建仓', '增持',
    '人工智能', 'ai', 'aigc', 'chatgpt', '大模型', '生成式', '智能',
    '创新', '发展', '合作', '签约', '订单', '中标', '业绩', '增长',
    '翻倍', '十倍', '百倍', '万亿', '千亿', '龙头', '领涨', '领跑',
    '加油', '冲', '起飞', '发财', '暴富', '赚', '盈利', '利润',
]

# 金融领域负面情感词
NEGATIVE_WORDS = [
    '跌', '下跌', '大跌', '暴跌', '跳水', '下挫', '走弱', '走低', '看空',
    '利空', '利空', '亏损', '亏钱', '损失', '下降', '崩盘', '暴跌', '熊', '熊市',
    '跌停', '大跌', '新低', '破位', '下跌', '恶化', '衰退', '萧条', '风险', '危机',
    '看空', '悲观', '消极', '疲软', '糟糕', '差劲', '不及预期', '低于预期',
    '减仓', '清仓', '割肉', '止损', '卖出', '抛售', '砸盘', '减持', '平仓',
    '套牢', '被套', '深套', '血亏', '爆仓', '强平', '退市', 'st', '*st',
    '造假', '欺诈', '违规', '处罚', '调查', '起诉', '败诉', '亏损',
    '裁员', '降薪', '倒闭', '破产', '跑路', '暴雷', '雷', '坑',
    '完了', '完蛋', '没救了', '凉凉', 'GG', 'game over',
    '跌', '暴跌', '下', '空', '卖', '抛', '砸',
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


def segment_text(text):
    if not text:
        return ''
    words = jieba.cut(text)
    stopwords = {'的', '了', '是', '我', '你', '他', '在', '有', '和', '与', '也', '都', '就', '不', '没', '要', '会', '能', '可以', '这', '那', '一个', '一下', '今天', '明天', '昨天', '什么', '怎么', '为什么', '觉得', '感觉', '应该', '可能', '但是', '不过', '如果', '因为', '所以', '而且', '然后', '其实', '真的', '还是', '只是', '或者', '比较', '时候', '股票', '股吧', '公司'}
    words = [w for w in words if w.strip() and w not in stopwords and len(w) > 1]
    return ' '.join(words)


def predict_sentiment(text):
    """基于情感词典的规则法"""
    if not text:
        return '中性', 0.0

    text_lower = text.lower()
    pos_score = 0
    neg_score = 0

    for w in POSITIVE_WORDS:
        pos_score += text_lower.count(w.lower())
    for w in NEGATIVE_WORDS:
        neg_score += text_lower.count(w.lower())

    total = pos_score + neg_score
    if total == 0:
        return '中性', 0.0

    # 归一化到 -1 到 1
    raw_score = (pos_score - neg_score) / total

    if raw_score > 0.2:
        label = '正面'
    elif raw_score < -0.2:
        label = '负面'
    else:
        label = '中性'

    return label, round(raw_score, 4)


def run():
    print("=" * 60)
    print("生成清洗后的情感数据")
    print("=" * 60)

    df = pd.read_csv(os.path.join(DATA_DIR, 'clean_posts.csv'))
    print(f"输入数据: {len(df)} 条")

    # 确保必要字段
    df['title_clean'] = df['title'].apply(clean_text)
    df['title_segmented'] = df['title_clean'].apply(segment_text)

    # 情感标注
    print("正在标注情感...")
    sentiments = []
    scores = []
    for i, row in df.iterrows():
        label, score = predict_sentiment(row['title_clean'])
        sentiments.append(label)
        scores.append(score)
        if (i + 1) % 500 == 0:
            print(f"  已处理 {i+1}/{len(df)}")

    df['sentiment'] = sentiments
    df['sentiment_score'] = scores

    # 统计
    print(f"\n情感分布:")
    print(df['sentiment'].value_counts())

    print(f"\n各股票情感分布:")
    cross = pd.crosstab(df['stock_name'], df['sentiment'])
    print(cross)

    # 保存
    output_path = os.path.join(DATA_DIR, 'final_data_v2.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n已保存: {output_path} ({len(df)}条)")

    return df


if __name__ == '__main__':
    run()
