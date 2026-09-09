"""
数据预处理与探索性分析
- 清洗、jieba分词、TF-IDF特征提取
- 生成可视化图表
- 使用FinBERT自动标注情感标签（伪标签）
"""
import pandas as pd
import numpy as np
import jieba
import re
import os
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')
FIGURE_DIR = os.path.join(BASE, 'figures')
os.makedirs(FIGURE_DIR, exist_ok=True)

# 停用词
STOPWORDS = set()
stopword_list = [
    '的', '了', '是', '我', '你', '他', '她', '它', '们', '在', '有', '和', '与', '或',
    '也', '都', '就', '不', '没', '要', '会', '能', '可', '以', '到', '为', '着', '看',
    '说', '这个', '那个', '什么', '怎么', '为什么', '哪里', '哪个', '一个', '一些',
    '可以', '这样', '那样', '这种', '那种', '这些', '那些', '已经', '还是', '只是',
    '但是', '不过', '如果', '虽然', '因为', '所以', '而且', '然后', '其实', '真的',
    '觉得', '感觉', '应该', '可能', '也许', '大概', '好像', '似乎', '一样', '一般',
    '今天', '明天', '昨天', '现在', '以后', '以前', '之前', '之后', '之间', '当中',
    '这', '那', '其', '之', '于', '而', '则', '乃', '及', '或', '且', '若', '故',
    '从', '把', '被', '让', '使', '给', '对', '向', '往', '由', '据', '按', '照',
    '着', '过', '起', '来', '去', '上', '下', '进', '出', '回', '到', '开', '关',
    '很', '太', '更', '最', '非', '极', '十', '百', '千', '万', '亿', '点', '些',
    '个', '只', '本', '次', '每', '各', '某', '另', '其', '此', '彼', '该',
    '吧', '啊', '哦', '呢', '嘛', '呀', '哈', '嘿', '喂', '嗯', '唉', '哇',
    '股票', '股吧', '公司', '目前', '情况', '时候', '问题', '知道', '没有', '不是',
    '没有', '一下', '一直', '起来', '出来', '下来', '上来', '过去', '回来', '过来',
    '他们', '我们', '你们', '自己', '别人', '大家', '人家', '没啥', '这种', '那种',
    '一下', '一些', '一种', '一切', '一样', '一般', '一直', '一起', '一定', '还是',
    '或者', '比较', '时候', '什么', '怎么', '为什么', '这样', '那样', '这么', '那么',
    '其实', '真的', '觉得', '感觉', '应该', '可能', '也许', '大概', '好像', '似乎',
    '但是', '不过', '如果', '虽然', '因为', '所以', '而且', '然后', '不过', '然而',
    '已经', '还是', '只是', '或者', '比较', '时候', '可以', '这样', '那样',
]
STOPWORDS = set(stopword_list)


def clean_text(text):
    """清洗文本：去HTML、去特殊字符"""
    if not isinstance(text, str):
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&quot;|&amp;|&lt;|&gt;|&nbsp;', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'#.*?#', '', text)
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def segment_text(text):
    """jieba分词 + 停用词过滤"""
    if not text:
        return ''
    words = jieba.cut(text)
    words = [w for w in words if w.strip() and w not in STOPWORDS and len(w) > 1]
    return ' '.join(words)


def run_preprocessing():
    print("=" * 60)
    print("第4章 数据预处理与探索性分析")
    print("=" * 60)

    # 4.1 原始数据探查
    print("\n--- 4.1 原始数据探查 ---")
    df = pd.read_csv(os.path.join(DATA_DIR, 'guba_posts.csv'))
    print(f"数据形状: {df.shape}")
    print(f"字段: {df.columns.tolist()}")
    print(f"数据类型:\n{df.dtypes}")
    print(f"缺失值:\n{df.isnull().sum()}")
    print(f"重复值: {df.duplicated().sum()}")
    print(f"总记录数: {len(df)}")

    # 4.2 数据清洗
    print("\n--- 4.2 数据清洗 ---")
    df = df.drop_duplicates(subset=['post_id'])
    df['title'] = df['title'].fillna('')
    df['title_clean'] = df['title'].apply(clean_text)
    df = df[df['title_clean'].str.len() > 0].reset_index(drop=True)
    print(f"清洗后记录数: {len(df)}")

    # 4.3 文本预处理：分词
    print("\n--- 4.3 jieba分词 ---")
    df['title_segmented'] = df['title_clean'].apply(segment_text)
    df = df[df['title_segmented'].str.len() > 0].reset_index(drop=True)
    print(f"分词后有效记录: {len(df)}")
    print(f"示例:")
    for i in range(3):
        print(f"  原文: {df.iloc[i]['title']}")
        print(f"  分词: {df.iloc[i]['title_segmented']}")

    # 4.3.2 TF-IDF特征提取
    print("\n--- TF-IDF特征提取 ---")
    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(df['title_segmented'])
    print(f"TF-IDF矩阵形状: {tfidf_matrix.shape}")
    print(f"特征词数量: {len(vectorizer.get_feature_names_out())}")

    # 保存处理后的数据
    df.to_csv(os.path.join(DATA_DIR, 'processed_data.csv'), index=False, encoding='utf-8-sig')
    print(f"已保存: data/processed_data.csv ({len(df)}条)")

    # 4.4 可视化分析
    print("\n--- 4.4 探索性可视化分析 ---")

    # 4.4.1 各股票帖子数量
    stock_names = {'601360': '三六零', '300229': '拓尔思', '300624': '万兴科技',
                   '300058': '蓝色光标', '300459': '汤姆猫', '2555': '三七互娱',
                   '300364': '中文在线'}
    df['stock_name'] = df['stock_code'].astype(str).map(stock_names)
    plt.figure(figsize=(10, 5))
    counts = df['stock_name'].value_counts()
    plt.bar(range(len(counts)), counts.values, color='#4A90D9')
    plt.xticks(range(len(counts)), counts.index, rotation=30)
    plt.title('各股票股吧帖子数量分布', fontsize=14)
    plt.ylabel('帖子数量')
    for i, v in enumerate(counts.values):
        plt.text(i, v + 5, str(v), ha='center')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '4_1_stock_distribution.png'), dpi=150)
    plt.close()
    print("  [saved] 4_1_stock_distribution.png")

    # 4.4.2 细分主线帖子数量
    sector_names = {'AI_Agent': 'AI Agent', 'AIGC': 'AIGC创意', 'AI_Game': 'AI游戏', 'AI_Media': 'AI传媒'}
    df['sector_name'] = df['sector'].map(sector_names)
    plt.figure(figsize=(8, 8))
    sector_counts = df['sector_name'].value_counts()
    plt.pie(sector_counts.values, labels=sector_counts.index, autopct='%1.1f%%',
            colors=['#4A90D9', '#50C878', '#FF6B6B', '#FFB347'])
    plt.title('AI应用细分主线帖子数量占比', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '4_2_sector_pie.png'), dpi=150)
    plt.close()
    print("  [saved] 4_2_sector_pie.png")

    # 4.4.3 阅读量分布
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(np.log10(df['reads'] + 1), bins=50, color='#4A90D9', edgecolor='white')
    axes[0].set_title('帖子阅读量分布（对数）', fontsize=13)
    axes[0].set_xlabel('log10(阅读量)')
    axes[0].set_ylabel('帖子数量')
    axes[1].boxplot([np.log10(df[df['sector'] == s]['reads'] + 1) for s in ['AI_Agent', 'AIGC', 'AI_Game', 'AI_Media']],
                    labels=['AI Agent', 'AIGC', 'AI游戏', 'AI传媒'])
    axes[1].set_title('各细分主线阅读量对比（对数）', fontsize=13)
    axes[1].set_ylabel('log10(阅读量)')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '4_3_reads_distribution.png'), dpi=150)
    plt.close()
    print("  [saved] 4_3_reads_distribution.png")

    # 4.4.4 回复量分布
    plt.figure(figsize=(10, 5))
    plt.hist(df['replies'] + 1, bins=50, color='#50C878', edgecolor='white')
    plt.title('帖子回复量分布', fontsize=14)
    plt.xlabel('回复量')
    plt.ylabel('帖子数量')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '4_4_replies_distribution.png'), dpi=150)
    plt.close()
    print("  [saved] 4_4_replies_distribution.png")

    # 4.4.5 词频统计
    all_words = []
    for text in df['title_segmented']:
        all_words.extend(text.split())
    word_counts = Counter(all_words)
    top20 = word_counts.most_common(20)

    plt.figure(figsize=(12, 6))
    words, freqs = zip(*top20)
    plt.barh(range(len(words)), freqs, color='#4A90D9')
    plt.yticks(range(len(words)), words)
    plt.title('股吧帖子高频词Top20', fontsize=14)
    plt.xlabel('词频')
    plt.gca().invert_yaxis()
    for i, v in enumerate(freqs):
        plt.text(v + 1, i, str(v), va='center')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '4_5_word_frequency.png'), dpi=150)
    plt.close()
    print("  [saved] 4_5_word_frequency.png")
    print(f"  Top10高频词: {top20[:10]}")

    # 4.4.6 TF-IDF重要特征词
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    top_tfidf_idx = tfidf_scores.argsort()[-20:][::-1]
    top_tfidf = [(feature_names[i], tfidf_scores[i]) for i in top_tfidf_idx]

    plt.figure(figsize=(12, 6))
    words_t, scores_t = zip(*top_tfidf)
    plt.barh(range(len(words_t)), scores_t, color='#FF6B6B')
    plt.yticks(range(len(words_t)), words_t)
    plt.title('TF-IDF重要性Top20特征词', fontsize=14)
    plt.xlabel('TF-IDF均值')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, '4_6_tfidf_top.png'), dpi=150)
    plt.close()
    print("  [saved] 4_6_tfidf_top.png")
    print(f"  Top10 TF-IDF: {top_tfidf[:10]}")

    # 保存TF-IDF矩阵和向量化器信息
    np.save(os.path.join(DATA_DIR, 'tfidf_matrix.npy'), tfidf_matrix.toarray())
    import pickle
    with open(os.path.join(DATA_DIR, 'tfidf_vectorizer.pkl'), 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"\n已保存: data/tfidf_matrix.npy, data/tfidf_vectorizer.pkl")

    print("\n" + "=" * 60)
    print("数据预处理与探索性分析完成！")
    print(f"有效数据: {len(df)}条")
    print(f"图表: {len(os.listdir(FIGURE_DIR))}张 -> figures/")
    print("=" * 60)

    return df


if __name__ == '__main__':
    df = run_preprocessing()
