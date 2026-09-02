# AI应用板块财经舆情监测大屏

从0到1设计并开发的财经舆情可视化产品，覆盖监测、预警、报告、处置全链路。

## 项目简介

针对AI应用概念板块（AI Agent、AIGC创意营销、AI游戏、AI传媒四条新兴主线），采集股吧评论与行情数据，基于FinBERT实现情感分析，提供板块、细分主线、个股三层情绪监测与可视化，配套规则预警、周期报告与处置工单形成产品闭环。

## 功能模块

| 模块 | 功能 |
|------|------|
| 舆情监测 | 板块/主线/个股三层情绪指数看板，热点事件聚合 |
| 舆情预警 | 关键词触发、情绪突变检测、趋势预判的规则预警 |
| 舆情报告 | 周期性情绪报告自动生成，主线对比分析 |
| 舆情处置 | 预警→复核→标记→入库工单闭环 |

## 技术栈

- **数据采集**：Python爬虫（东方财富股吧）、AKShare（行情数据）
- **情感分析**：FinBERT（金融领域BERT微调）
- **数据存储**：MySQL / SQLite
- **可视化**：ECharts / Matplotlib
- **后端**：Python Flask
- **前端**：HTML / CSS / JavaScript

## 项目结构

```
ai-sentiment-dashboard/
├── crawler/              # 数据采集模块
│   ├── stock_bar_crawler.py   # 股吧评论爬虫
│   └── market_data.py         # AKShare行情数据
├── nlp/                  # 情感分析模块
│   ├── finbert_model.py       # FinBERT情感分类
│   └── keyword_extract.py     # 关键词与事件抽取
├── analysis/             # 数据分析模块
│   ├── sentiment_index.py     # 情绪指数计算
│   └── divergence.py          # 情绪突变检测
├── alert/                # 预警模块
│   └── rule_engine.py         # 规则预警引擎
├── report/               # 报告模块
│   └── report_generator.py    # 周期报告生成
├── dashboard/            # 可视化大屏
│   ├── templates/             # 前端页面
│   ├── static/                # 静态资源
│   └── app.py                 # Flask后端
├── data/                 # 数据存储
├── docs/                 # 产品文档
│   └── PRD.md                  # 产品需求文档
├── requirements.txt
└── README.md
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动数据采集
python crawler/stock_bar_crawler.py

# 启动可视化大屏
python dashboard/app.py
```

## 产品设计文档

详见 [docs/PRD.md](docs/PRD.md)
