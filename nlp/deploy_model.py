# -*- coding: utf-8 -*-
"""
模型部署：用 FinBERT 伪标签数据集训练最优随机森林模型，
对深度清洗后的 2312 条有效帖子进行情感预测，生成大屏最终数据 final_data_v3.csv
同时保存模型文件 rf_model.pkl 供系统加载。
"""
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'data')

# 1. 加载伪标签训练集（2379条，FinBERT 自动标注）
labeled = pd.read_csv(os.path.join(DATA_DIR, 'labeled_data.csv'))
labeled['title_segmented'] = labeled['title_segmented'].fillna('')
print(f'训练集（FinBERT伪标签）: {len(labeled)} 条')
print(labeled['sentiment'].value_counts())

# 2. TF-IDF 特征（与论文5.2.4一致）
tfidf = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=2)
X = tfidf.fit_transform(labeled['title_segmented'])
y = labeled['sentiment']
print(f'TF-IDF 特征矩阵: {X.shape}')

# 3. 训练最优随机森林（论文6.2.2 调参结果）
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
rf = RandomForestClassifier(
    n_estimators=200, max_depth=30, min_samples_split=5,
    min_samples_leaf=2, class_weight='balanced', random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
print('\n=== 测试集评估（复现论文6.3）===')
print(f'准确率: {accuracy_score(y_test, y_pred):.4f}')
print(f'宏平均F1: {f1_score(y_test, y_pred, average="macro"):.4f}')
print(classification_report(y_test, y_pred, target_names=['负面', '中性', '正面'], digits=4))

# 4. 全量重训后保存模型
rf_full = RandomForestClassifier(
    n_estimators=200, max_depth=30, min_samples_split=5,
    min_samples_leaf=2, class_weight='balanced', random_state=42, n_jobs=-1)
rf_full.fit(X, y)
joblib.dump({'vectorizer': tfidf, 'model': rf_full},
            os.path.join(DATA_DIR, 'rf_model.pkl'))
print('模型已保存: data/rf_model.pkl')

# 5. 对深度清洗后的 2312 条有效帖子预测（先做文本清洗+分词）
import re, jieba
STOPWORDS = set(['的','了','是','我','你','他','她','它','们','在','有','和','与','或','也','都',
    '就','不','没','要','会','能','可','以','到','为','着','看','说','这个','那个','什么','怎么',
    '股票','股吧','公司','目前','情况','时候','问题','知道','没有','不是','一下','一直','今天',
    '明天','昨天','现在','可以','这样','那样','这种','那种','这些','那些','已经','还是','只是',
    '但是','不过','如果','因为','所以','而且','然后','其实','真的','觉得','感觉','应该','可能'])
def clean_text(t):
    if not isinstance(t, str): return ''
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'#.*?#', '', t)
    t = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()
def seg(t):
    ws = jieba.cut(t)
    return ' '.join(w for w in ws if w.strip() and w not in STOPWORDS and len(w) > 1)

clean = pd.read_csv(os.path.join(DATA_DIR, 'clean_posts.csv'))
clean['title_clean'] = clean['title'].apply(clean_text)
clean['title_segmented'] = clean['title_clean'].apply(seg)
print(f'\n待预测有效帖子: {len(clean)} 条')

X_new = tfidf.transform(clean['title_segmented'])
labels = rf_full.predict(X_new)
proba = rf_full.predict_proba(X_new)
classes = list(rf_full.classes_)
p_pos = proba[:, classes.index('正面')]
p_neg = proba[:, classes.index('负面')]
# 情感得分 ∈ [-1,1]：正面概率 - 负面概率
scores = np.round(p_pos - p_neg, 4)

clean['sentiment'] = labels
clean['sentiment_score'] = scores
print('预测标签分布:')
print(clean['sentiment'].value_counts())

# 6. 输出大屏最终数据
out_cols = ['stock_code', 'post_id', 'title', 'author', 'date', 'reads', 'replies',
            'sector', 'stock_name', 'sector_name', 'title_clean', 'title_segmented',
            'sentiment', 'sentiment_score']
clean[out_cols].to_csv(os.path.join(DATA_DIR, 'final_data_v3.csv'),
                       index=False, encoding='utf-8-sig')
print(f'\n已生成 final_data_v3.csv: {len(clean)} 条')

# 7. 各股情绪指数（与大屏口径一致：(score+1)*50）
clean['idx'] = (clean['sentiment_score'] + 1) * 50
print('\n各股情绪指数:')
print(clean.groupby('stock_name')['idx'].mean().round(1).sort_values(ascending=False))
