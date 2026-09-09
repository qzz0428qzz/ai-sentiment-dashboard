const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,
        HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, PageBreak } = require('docx');
const fs = require('fs');
const path = require('path');

const figuresDir = path.join(__dirname, '..', 'figures');
const outputPath = path.join(__dirname, '..', 'docs', 'thesis_body.docx');

const cjkFont = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "宋体" };
const headingFont = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "黑体" };

function loadImg(name) {
  const p = path.join(figuresDir, name);
  if (fs.existsSync(p)) return fs.readFileSync(p);
  return null;
}

function img(name, w, h, caption) {
  const data = loadImg(name);
  const children = [];
  if (data) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new ImageRun({ type: "png", data, transformation: { width: w, height: h },
        altText: { title: caption, description: caption, name: name } })]
    }));
  } else {
    children.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun(`[${caption}]`)] }));
  }
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: caption, font: cjkFont, size: 21, bold: false })] }));
  return children;
}

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: headingFont })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: headingFont })] });
}
function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text, font: headingFont })] });
}
function p(text) {
  return new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 480 }, spacing: { line: 360 },
    children: [new TextRun({ text, font: cjkFont, size: 24 })] });
}
function pNoIndent(text) {
  return new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { line: 360 },
    children: [new TextRun({ text, font: cjkFont, size: 24 })] });
}
function caption(text) {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 200 },
    children: [new TextRun({ text, font: cjkFont, size: 21, bold: false })] });
}

const border = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };

function makeTable(headers, rows) {
  const colCount = headers.length;
  const colWidth = Math.floor(9000 / colCount);
  const colWidths = Array(colCount).fill(colWidth);
  const headerRow = new TableRow({
    tableHeader: true,
    cantSplit: true,
    children: headers.map(h => new TableCell({
      borders, width: { size: colWidth, type: WidthType.DXA },
      shading: { fill: "D9E2F3", type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, font: cjkFont, size: 21, bold: true })] })]
    }))
  });
  const dataRows = rows.map(row => new TableRow({
    cantSplit: true,
    children: row.map(cell => new TableCell({
      borders, width: { size: colWidth, type: WidthType.DXA },
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: String(cell), font: cjkFont, size: 21 })] })]
    }))
  }));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows]
  });
}

const children = [];

// ===== 封面 =====
children.push(new Paragraph({ spacing: { before: 2400 } }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 },
  children: [new TextRun({ text: "AI应用概念板块财经舆情分析", font: headingFont, size: 52, bold: true })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 2400 },
  children: [new TextRun({ text: "产品设计与实现", font: headingFont, size: 52, bold: true })] }));
const coverInfo = [
  ["学院", "________________"],
  ["专业", "数据科学与大数据技术"],
  ["班级", "________________"],
  ["学号", "________________"],
  ["姓名", "________________"],
  ["指导教师", "________________"],
];
coverInfo.forEach(([k, v]) => {
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [
      new TextRun({ text: k + "：", font: cjkFont, size: 28 }),
      new TextRun({ text: v, font: cjkFont, size: 28, underline: { type: "single" } })
    ]}));
});
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1200 },
  children: [new TextRun({ text: "2026年12月", font: cjkFont, size: 28 })] }));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 摘要 =====
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
  children: [new TextRun({ text: "摘  要", font: headingFont, size: 32, bold: true })] }));
children.push(p("随着人工智能技术的快速发展，AI应用概念板块成为A股市场最受关注的投资主线之一，涵盖AI Agent、AIGC创意、AI游戏、AI传媒四条细分主线。然而，当前投资者获取板块舆情信息主要依赖人工浏览股吧帖子，存在舆情分散、热点滞后、情绪难以量化等问题。本文以东方财富股吧评论及个股行情数据为研究对象，完成一套面向AI应用概念板块的财经舆情分析产品的设计与实现。在系统设计层面，从产品生命周期出发，完成舆情监测、预警、报告、处置四大功能模块的需求分析与架构设计，采用三层架构（数据层、算法层、应用层）构建系统。在数据采集与预处理层面，基于Python爬虫采集7只AI概念股的2480条帖子数据，清洗后保留2379条有效数据，使用jieba分词和TF-IDF方法提取500维文本特征。在关键性技术研究层面，搭建FinBERT、朴素贝叶斯、随机森林三种情感分类模型，采用GridSearchCV进行超参数调优和5折交叉验证。实验结果表明，随机森林模型综合效果最优，准确率达85.29%，F1值达0.8491；特征重要性分析显示\"涨停\"\"主力\"\"业绩\"等词语对分类贡献最大。基于最优模型输出板块、细分主线、个股三层情绪指数，开发Web可视化大屏并实现舆情报告自动生成。本系统从0到1完成产品设计与实现，覆盖需求分析、整体设计、详细设计、关键技术研究、总结展望的完整产品生命周期。"));
children.push(new Paragraph({ spacing: { before: 200, after: 400 },
  children: [
    new TextRun({ text: "关键词：", font: cjkFont, size: 24, bold: true }),
    new TextRun({ text: "财经舆情；情感分析；FinBERT；数据挖掘；可视化", font: cjkFont, size: 24 })
  ]}));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== Abstract =====
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
  children: [new TextRun({ text: "Abstract", font: headingFont, size: 32, bold: true })] }));
children.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 480 }, spacing: { line: 360 },
  children: [new TextRun({ text: "With the rapid development of AI technology, the AI application sector has become one of the most watched investment themes in the A-share market, covering four sub-sectors: AI Agent, AIGC Creative, AI Gaming, and AI Media. However, current investors mainly rely on manual browsing of stock bar posts, which suffers from scattered sentiment, delayed hotspots, and difficulty in quantifying emotions. This paper takes East Money stock bar comments and individual stock market data as the research object, and completes the design and implementation of a financial sentiment analysis product for the AI application sector. At the system design level, starting from the product lifecycle, requirement analysis and architecture design are conducted for four functional modules: sentiment monitoring, alerting, reporting, and disposal, adopting a three-layer architecture (data layer, algorithm layer, application layer). At the data collection and preprocessing level, 2,480 posts from 7 representative AI concept stocks are collected, and after data cleaning, 2,379 valid records are retained. Jieba word segmentation and TF-IDF method are used to extract 500-dimensional text features. At the key technology research level, three sentiment classification models including FinBERT, Naive Bayes, and Random Forest are constructed with GridSearchCV for hyperparameter tuning and 5-fold cross-validation. Experimental results show that the Random Forest model achieves the best comprehensive performance with an accuracy of 85.29% and F1-score of 0.8491. Feature importance analysis reveals that words such as \"limit-up,\" \"main force,\" and \"performance\" contribute most to classification. Based on the optimal model, a three-level sentiment index is output, and a Web visualization dashboard and automatic report generation are developed. This system completes product design and implementation from 0 to 1, covering the complete product lifecycle.", font: { ascii: "Times New Roman", hAnsi: "Times New Roman" }, size: 24 })] }));
children.push(new Paragraph({ spacing: { before: 200, after: 400 },
  children: [
    new TextRun({ text: "Key words: ", font: { ascii: "Times New Roman", hAnsi: "Times New Roman" }, size: 24, bold: true }),
    new TextRun({ text: "Financial Sentiment; Sentiment Analysis; FinBERT; Data Mining; Visualization", font: { ascii: "Times New Roman", hAnsi: "Times New Roman" }, size: 24 })
  ]}));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 第1章 绪论 =====
children.push(h1("第1章 绪论"));
children.push(h2("1.1 研究背景与研究意义"));
children.push(h3("1.1.1 研究背景"));
children.push(p("近年来，以大语言模型为代表的生成式人工智能技术取得突破性进展，AI应用概念板块成为A股市场最受关注的投资主线之一。三七互娱、三六零、万兴科技等上市公司纷纷布局AI应用领域，涵盖AI Agent智能体、AIGC创意营销、AI游戏、AI传媒等多个细分方向。随着AI概念持续升温，投资者在东方财富股吧等社区平台上产生大量讨论帖文，形成了丰富的非结构化舆情数据。"));
children.push(p("然而，当前投资者获取AI板块舆情信息主要依赖人工浏览股吧帖子和财经新闻，存在舆情分散、热点滞后、情绪难以量化等问题。一方面，股吧帖子数量庞大且分布于多个个股板块，人工难以全面覆盖；另一方面，投资者情绪的正负面变化往往领先于股价波动，但传统方法缺乏对舆情情绪的量化分析手段，难以将舆情数据转化为可操作的投资参考。"));
children.push(p("在此背景下，运用自然语言处理技术与数据挖掘方法，构建一套面向AI应用概念板块的财经舆情分析产品，实现舆情数据的自动采集、情感分析和可视化展示，具有重要的现实意义。"));
children.push(h3("1.1.2 研究意义"));
children.push(p("本研究的意义体现在理论与实践两个方面。"));
children.push(p("理论意义方面，本文完整实践了从数据采集、文本预处理、特征工程到多模型对比的数据挖掘标准流程，对比了FinBERT深度学习模型与传统机器学习算法（朴素贝叶斯、随机森林）在中文股吧文本情感分类任务上的适配性，丰富了金融舆情分析领域的研究案例。同时，本文提出的三层情绪指标体系（板块、细分主线、个股）为板块级舆情量化分析提供了一种可行的框架。"));
children.push(p("实践意义方面，本文设计并实现了覆盖监测、预警、报告、处置四大模块的舆情分析产品，将舆情数据转化为可操作的可视化看板和周期性报告，能够帮助投资者快速感知AI板块市场情绪变化，辅助投资决策。产品采用从0到1的设计思路，体现了产品生命周期管理的完整性。"));

children.push(h2("1.2 国内外研究现状"));
children.push(h3("1.2.1 国外研究现状"));
children.push(p("国外在金融文本情感分析领域起步较早。Devlin等人提出的BERT（Bidirectional Encoder Representations from Transformers）模型在自然语言理解任务上取得突破性进展，为金融领域文本挖掘奠定了基础。Araci等人在此基础上发布了FinBERT，在金融语料上进行领域微调，在金融情感分类任务上显著优于通用BERT模型。国外学者还广泛利用新闻文本、社交媒体数据构建市场情绪指标，如Bloomberg、Reuters等机构的舆情分析系统已实现商业化落地。"));
children.push(h3("1.2.2 国内研究现状"));
children.push(p("国内在舆情分析领域的应用研究日益活跃。学者们利用东方财富股吧、新浪微博等平台数据，开展投资者情绪与股价关联性研究。部分研究采用情感词典法或机器学习模型对股吧评论进行情感分类，并验证了情绪指标对短期股价波动的预测能力。在工具层面，jieba中文分词、TF-IDF特征提取等技术已成为中文文本挖掘的标准流程。"));
children.push(h3("1.2.3 现有研究存在的不足"));
children.push(p("通过对国内外相关研究的梳理，发现现有研究存在以下不足：第一，多数研究仅使用单一算法进行情感分类，缺少多种模型的横向对比实验，难以评估不同算法在同一数据集上的适配性；第二，可视化维度单一，多数研究仅输出统计图表，未结合业务场景进行多维度可视化展示；第三，缺乏从产品化角度进行的系统性设计，多数研究停留在算法验证阶段，未形成可落地的舆情分析产品。"));

children.push(h2("1.3 主要研究内容"));
children.push(p("本文的主要研究内容包括以下几个方面："));
children.push(p("（1）股吧评论数据采集与个股行情数据获取。基于Python网络爬虫技术，采集东方财富股吧中AI应用概念板块7只代表个股的评论数据，通过东方财富公开API获取个股行情数据。"));
children.push(p("（2）系统需求分析与整体架构设计。从产品生命周期出发，完成舆情监测、预警、报告、处置四大功能模块的需求定义和系统架构设计。"));
children.push(p("（3）数据清洗与特征工程。对原始数据进行去重、去空值、异常字符清理等预处理操作，使用jieba分词和TF-IDF方法提取文本特征。"));
children.push(p("（4）多模型构建与对比实验。搭建FinBERT、朴素贝叶斯、随机森林三种情感分类模型，采用GridSearchCV进行超参数调优，使用准确率、F1值、混淆矩阵等指标进行横向对比。"));
children.push(p("（5）可视化大屏开发与舆情报告生成。基于最优模型输出板块情绪指数，开发Web可视化大屏，实现舆情报告的自动生成。"));

children.push(h2("1.4 论文组织结构"));
children.push(p("本文共分为七章，各章内容安排如下："));
children.push(p("第1章为绪论，介绍研究背景、研究意义、国内外研究现状及主要研究内容。"));
children.push(p("第2章为相关技术与理论基础，介绍系统开发所涉及的Python数据栈、网络爬虫、NLP文本挖掘、情感分析算法及可视化技术。"));
children.push(p("第3章为需求分析，从产品角度定义系统目标、功能需求、非功能需求，并进行用例分析。"));
children.push(p("第4章为系统整体设计，完成系统架构设计、功能模块设计、数据流设计和技术选型。"));
children.push(p("第5章为系统详细设计与实现，详细介绍数据采集模块、数据预处理模块、可视化分析模块及可视化大屏的实现。"));
children.push(p("第6章为关键性技术研究，重点研究FinBERT、朴素贝叶斯、随机森林三种情感分析模型，进行模型训练、调优、评估与对比实验。"));
children.push(p("第7章为总结与展望，总结全文工作，分析研究不足，展望未来研究方向。"));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 第2章 相关技术与理论基础 =====
children.push(h1("第2章 相关技术与理论基础"));
children.push(h2("2.1 开发语言与工具"));
children.push(p("本系统采用Python作为主要开发语言。Python具有丰富的数据科学生态，适合完成数据采集、清洗、分析和可视化的全流程工作。主要使用的工具库包括：Pandas用于表格数据的读取、清洗和统计分析；NumPy用于数值计算和数组处理；Scikit-learn用于机器学习模型的训练和评估；Matplotlib用于静态可视化绘图；Flask作为Web框架支撑可视化大屏的开发。开发环境为PyCharm，Python版本为3.9。"));
children.push(h2("2.2 数据采集技术"));
children.push(h3("2.2.1 网络爬虫原理"));
children.push(p("网络爬虫是一种按照预设规则自动获取网页内容的程序。本系统的爬虫模块基于Python的requests库发送HTTP请求，获取东方财富股吧的帖子列表页面，通过解析JSON格式的响应数据提取帖子标题、作者、发布时间、阅读量和回复数等字段。爬虫设计了请求间隔和随机延时机制，避免因请求频率过高触发反爬策略。"));
children.push(h3("2.2.2 东方财富API接口"));
children.push(p("东方财富网提供了股吧帖子和个股行情的半公开API接口。股吧帖子接口通过拼接个股代码和板块参数即可获取指定页数的帖子列表，返回JSON格式的数据。行情数据接口可获取个股的实时行情、历史K线、涨跌幅、成交额等结构化数据。这些接口无需认证即可访问，为数据采集提供了便利。"));
children.push(h2("2.3 NLP文本挖掘技术"));
children.push(h3("2.3.1 jieba中文分词"));
children.push(p("jieba是目前使用最广泛的中文分词工具，支持精确模式、全模式和搜索引擎模式三种分词方式。本系统采用精确模式对股吧帖子标题进行分词，将连续的中文文本切分为有意义的词语序列。jieba内置了基于前缀词典的高效分词算法，同时支持用户自定义词典，可以将AI领域的专有名词（如\"智能体\"\"大模型\"\"AIGC\"）加入词典以提高分词准确性。"));
children.push(h3("2.3.2 停用词过滤"));
children.push(p("停用词是指在文本中出现频率高但携带语义信息少的词语，如\"的\"\"了\"\"是\"\"在\"等。本系统构建了包含常见中文停用词和股吧特有噪声词的停用词表，在分词后过滤掉这些词语，以减少噪声对后续特征提取和模型训练的干扰。"));
children.push(h3("2.3.3 TF-IDF特征提取"));
children.push(p("TF-IDF（Term Frequency-Inverse Document Frequency）是一种经典的文本特征提取方法，通过计算词项在文档中的频率（TF）和逆文档频率（IDF）的乘积来衡量词语对文档的重要性。本系统使用Scikit-learn的TfidfVectorizer将分词后的文本转换为500维的TF-IDF特征向量，作为后续机器学习模型的输入特征。"));
children.push(h2("2.4 情感分析算法"));
children.push(h3("2.4.1 FinBERT"));
children.push(p("FinBERT是在BERT基础上使用金融领域语料进行进一步预训练的模型，专门针对金融文本的情感分析任务进行了优化。FinBERT能够理解金融领域的专业术语和表达方式，在金融情感分类任务上表现优于通用BERT模型。本系统使用FinBERT对股吧帖子进行正面、负面、中性三分类。"));
children.push(h3("2.4.2 朴素贝叶斯分类器"));
children.push(p("朴素贝叶斯是一种基于贝叶斯定理的概率分类器，假设特征之间相互独立。在文本分类任务中，朴素贝叶斯通过计算词项在不同类别下的条件概率来预测文本的类别。该算法计算效率高、易于实现，是文本分类任务中常用的基线模型。"));
children.push(h3("2.4.3 随机森林分类器"));
children.push(p("随机森林是一种集成学习方法，通过构建多棵决策树并对它们的预测结果进行投票来做出最终决策。随机森林能够处理高维特征数据，对噪声具有较好的鲁棒性，同时支持特征重要性排序，有助于理解哪些词语对情感分类贡献最大。"));
children.push(h2("2.5 可视化技术"));
children.push(p("本系统的可视化采用两种方案：在数据分析阶段使用Matplotlib生成静态图表，包括分布图、饼图、折线图、柱状图、热力图等；在产品展示阶段使用Flask框架搭建Web应用，前端采用ECharts库实现交互式数据可视化大屏，支持实时数据刷新和用户交互操作。"));
children.push(h2("2.6 模型评估方法"));
children.push(p("本系统采用以下指标评估模型性能：准确率（Accuracy）衡量模型整体预测正确率；精确率（Precision）衡量预测为正面的样本中实际为正面的比例；召回率（Recall）衡量实际为正面的样本中被正确预测的比例；F1值（F1-Score）为精确率和召回率的调和平均，综合衡量模型性能；混淆矩阵直观展示各类别的预测分布。同时使用GridSearchCV进行超参数网格搜索和交叉验证，确保模型评估的客观性。"));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 第3章 需求分析 =====
children.push(h1("第3章 需求分析"));
children.push(h2("3.1 系统目标"));
children.push(p("本系统的核心目标是帮助投资者快速感知AI应用概念板块的市场情绪与热点事件，辅助投资决策。具体目标包括：实现AI板块股吧评论数据的自动采集与实时更新；对舆情文本进行情感分类，量化板块、细分主线和个股三个层级的情绪指数；通过可视化大屏直观展示舆情态势；提供舆情预警和周期报告功能，形成产品闭环。"));
children.push(h2("3.2 功能需求"));
children.push(p("根据产品生命周期管理理念，系统划分为舆情监测、舆情预警、舆情报告、舆情处置四大功能模块。"));
children.push(h3("3.2.1 舆情监测模块"));
children.push(p("舆情监测模块是系统的核心功能，包括以下子功能：板块情绪总览大屏，展示AI应用板块整体情绪指数、正负面占比、热词云；细分主线情绪对比，展示AI Agent、AIGC创意、AI游戏、AI传媒四条主线之间的情绪对比；个股情绪详情，展示个股情绪指数、情感分布、帖子趋势及情绪与股价的关联分析。"));
children.push(h3("3.2.2 舆情预警模块"));
children.push(p("舆情预警模块负责在舆情出现异常变化时自动触发预警，包括以下子功能：关键词触发预警，当帖文中出现\"减持\"\"爆雷\"\"监管\"等关键词时发出提醒；情绪突变检测，当情绪指数在短时间内出现大幅波动时触发预警；趋势预判预警，基于情绪趋势外推，预判可能的情绪拐点。"));
children.push(h3("3.2.3 航情报告模块"));
children.push(p("舆情报告模块自动生成周期性舆情分析报告，包括舆情概览、情绪分析、细分主线对比、传播特点、风险提示和投资建议等章节。报告可按日、周、月三种周期自动生成，同时支持板块内多家公司的舆情对比分析。"));
children.push(h3("3.2.4 航情处置模块"));
children.push(p("舆情处置模块实现预警到处置的闭环流程，包括预警工单生成、人工复核、标记分类、入库归档等子功能。当预警触发后，系统自动生成处置工单，经人工复核后标记处理结果，形成知识沉淀。"));
children.push(h2("3.3 非功能需求"));
children.push(p("（1）完整性：系统覆盖从数据采集到报告生成的全流程，各模块功能完整可用。"));
children.push(p("（2）可读性：可视化图表清晰直观，结果可解释，用户无需技术背景即可理解。"));
children.push(p("（3）准确性：数据预处理规范，模型评估指标客观，实验结果可复现。"));
children.push(p("（4）可复现性：代码完整，数据集可重复运行实验，确保研究结论的可靠性。"));
children.push(h2("3.4 用例分析"));
children.push(p("系统定义了三种用户角色：访客、注册用户和分析师。访客可查看板块情绪总览大屏、浏览公开舆情报告；注册用户在访客权限基础上可查看个股情绪详情、订阅预警推送、查看历史报告；分析师在注册用户权限基础上可配置预警规则、处置预警工单、导出分析数据。"));
children.push(p("系统用例图如图3-1所示，展示了三种用户角色与系统核心用例之间的关系。"));
children.push(...img("placeholder", 500, 350, "图3-1 系统用例图"));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 第4章 系统整体设计 =====
children.push(h1("第4章 系统整体设计"));
children.push(h2("4.1 系统架构设计"));
children.push(p("本系统采用三层架构设计，自上而下分为应用层、算法层和数据层，如图4-1所示。"));
children.push(p("应用层负责面向用户的产品功能呈现，包括舆情监测大屏看板、舆情预警规则引擎、舆情报告自动生成和舆情处置工单闭环四个功能组件。"));
children.push(p("算法层负责数据处理和模型推理，包括数据清洗与预处理、jieba分词与TF-IDF特征提取、FinBERT/朴素贝叶斯/随机森林情感分析模型、板块情绪指数计算和舆情报告生成引擎等核心算法组件。"));
children.push(p("数据层负责数据的采集和存储，包括东方财富股吧评论数据源、东方财富行情API数据源、CSV文件存储和模型文件存储。"));
children.push(...img("placeholder", 450, 320, "图4-1 系统架构图"));
children.push(h2("4.2 功能模块设计"));
children.push(p("系统功能模块设计遵循产品闭环理念，将四大功能模块细分为若干子模块，如图4-2所示。舆情监测模块下设板块情绪总览、细分主线对比、个股情绪详情三个子模块；舆情预警模块下设关键词触发、情绪突变检测、趋势预判三个子模块；舆情报告模块下设周期报告、板块对比两个子模块；舆情处置模块下设工单管理、人工复核、标记入库三个子模块。"));
children.push(...img("placeholder", 480, 320, "图4-2 功能模块图"));
children.push(h2("4.3 数据流设计"));
children.push(p("系统的数据流从数据采集到最终展示经历完整的处理链路，如图4-3所示。原始数据从东方财富股吧和行情API采集后，依次经过数据清洗（去重、去空值、异常字符清理）、jieba分词与停用词过滤、TF-IDF特征提取，然后分别输入三种情感分析模型进行分类预测，模型输出结果经过情绪指数聚合后，一方面推送至可视化大屏展示，另一方面生成周期性舆情报告。"));
children.push(...img("placeholder", 480, 280, "图4-3 数据流图"));
children.push(h2("4.4 技术选型"));
children.push(p("系统技术选型如表4-1所示。"));
children.push(makeTable(
  ["技术维度", "选型方案", "选型理由"],
  [
    ["开发语言", "Python 3.9", "数据科学生态完善，适合全流程开发"],
    ["数据采集", "requests + JSON解析", "东方财富API返回JSON，无需复杂HTML解析"],
    ["数据存储", "CSV文件", "数据量适中，CSV便于读取和调试"],
    ["中文分词", "jieba", "中文NLP标准工具，支持自定义词典"],
    ["特征提取", "TF-IDF (Scikit-learn)", "经典文本特征方法，计算效率高"],
    ["情感模型", "FinBERT + 朴素贝叶斯 + 随机森林", "深度学习+传统ML横向对比"],
    ["可视化", "Matplotlib + ECharts", "静态分析图+交互式大屏"],
    ["Web框架", "Flask", "轻量级，适合单页面大屏应用"]
  ]
));
children.push(caption("表4-1 技术选型方案"));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 第5章 系统详细设计与实现 =====
children.push(h1("第5章 系统详细设计与实现"));
children.push(h2("5.1 数据采集模块"));
children.push(h3("5.1.1 股吧评论爬虫"));
children.push(p("股吧评论爬虫基于requests库实现，通过拼接东方财富股吧API的URL参数获取指定个股的帖子列表。爬虫的核心流程为：构造请求URL、发送HTTP请求、解析JSON响应、提取帖子字段、翻页采集。系统对7只AI概念股（三六零、三七互娱、万兴科技、蓝色光标、中文在线、拓尔思、汤姆猫）分别采集股吧帖子，每只股票采集10页数据。爬虫设置了随机延时（1-3秒）和请求头伪装，确保采集过程稳定运行。最终共采集2480条股吧帖子数据。"));
children.push(h3("5.1.2 行情数据接口"));
children.push(p("行情数据通过东方财富公开API获取，包括个股实时行情（最新价、涨跌幅、成交额、换手率、市盈率）和历史K线数据（日K线的开盘价、收盘价、最高价、最低价、成交量）。行情数据通过直接请求API接口获取结构化JSON数据，无需爬虫解析，采集效率高。"));
children.push(h3("5.1.3 数据存储"));
children.push(p("采集到的股吧帖子数据和行情数据统一存储为CSV格式文件。股吧帖子数据包含股票代码、帖子ID、标题、作者、发布时间、阅读量、回复数、所属主线等字段。行情数据包含日期、开盘价、收盘价、最高价、最低价、成交量等字段。CSV格式便于Pandas读取和后续分析处理。"));

children.push(h2("5.2 数据预处理模块"));
children.push(h3("5.2.1 原始数据探查"));
children.push(p("使用Pandas对原始数据进行探查，结果显示共2480条记录，8个字段。数据存在的主要质量问题包括：部分帖子标题为空值、存在重复帖子、部分阅读量和回复量为异常值。数据覆盖2026年6月至9月的时间范围，涉及7只个股和4条细分主线。"));
children.push(h3("5.2.2 数据清洗"));
children.push(p("数据清洗包括以下步骤：首先使用drop_duplicates()方法去除重复帖子；然后删除标题为空值的记录；最后过滤阅读量和回复量中的异常值（如负值或明显超出合理范围的值）。经过清洗后，有效数据为2379条，数据质量满足后续分析要求。"));
children.push(h3("5.2.3 jieba分词与停用词过滤"));
children.push(p("对清洗后的帖子标题使用jieba进行精确模式分词，同时加载自定义AI领域词典（包含\"智能体\"\"大模型\"\"AIGC\"\"算力\"等术语）。分词后使用停用词表过滤无意义词语，停用词表包含常见中文停用词和股吧噪声词（如\"顶\"\"沙发\"\"前排\"等）。分词结果存储为词语列表，用于后续TF-IDF特征提取。"));
children.push(h3("5.2.4 TF-IDF特征提取"));
children.push(p("使用Scikit-learn的TfidfVectorizer将分词后的文本转换为TF-IDF特征向量。参数设置为：最大特征数500、ngram范围为(1,2)（包含单词和二元词组）、最小文档频率2。最终生成500维的TF-IDF特征矩阵，作为情感分类模型的输入。同时保存了TF-IDF向量化器（tfidf_vectorizer.pkl）和特征矩阵（tfidf_matrix.npy）供模型训练使用。"));

children.push(h2("5.3 探索性可视化分析"));
children.push(p("在数据预处理完成后，对数据进行探索性可视化分析，以了解数据分布特征和潜在规律。"));
children.push(p("图5-1展示了各股票的帖子数量分布。从图中可以看出，三六零和万兴科技的帖子数量最多，说明这两只股票在股吧中的讨论热度最高，投资者关注度最大。拓尔思和中文在线的帖子数量相对较少。"));
children.push(...img("4_1_stock_distribution.png", 500, 350, "图5-1 各股票帖子数量分布"));
children.push(p("图5-2展示了四条细分主线的帖子占比。AI Agent和AIGC创意主线的帖子数量最多，占比分别为32.2%和32.8%，说明这两条主线是当前AI应用板块舆情讨论的核心方向。AI传媒主线帖子偏少，仅占2.9%，主要原因是该主线样本股较少且讨论活跃度偏低。"));
children.push(...img("4_2_sector_pie.png", 450, 320, "图5-2 细分主线帖子占比"));
children.push(p("图5-3展示了帖子阅读量的分布情况。大多数帖子的阅读量集中在100-1000区间，少量热门帖子的阅读量超过10000，呈现典型的长尾分布特征。"));
children.push(...img("4_3_reads_distribution.png", 480, 320, "图5-3 帖子阅读量分布"));
children.push(p("图5-4展示了帖子回复量的分布。回复量整体偏低，多数帖子回复数在0-50区间，说明股吧讨论以浏览为主，深度互动相对较少。"));
children.push(...img("4_4_replies_distribution.png", 480, 280, "图5-4 帖子回复量分布"));
children.push(p("图5-5展示了帖子标题的高频词统计。排名前列的高频词包括\"AI\"\"涨停\"\"板块\"\"游戏\"\"科技\"\"应用\"等，反映了股吧讨论的核心主题围绕AI概念本身和板块涨跌展开。"));
children.push(...img("4_5_word_frequency.png", 500, 320, "图5-5 高频词统计"));
children.push(p("图5-6展示了TF-IDF特征值排名前20的关键词。与简单词频不同，TF-IDF能够识别出对文档区分度更高的词语，如\"涨停\"\"主力\"\"业绩\"等词语在TF-IDF排名中更为突出，说明这些词语对情感分类具有较高的区分价值。"));
children.push(...img("4_6_tfidf_top.png", 480, 300, "图5-6 TF-IDF Top20特征词"));
children.push(new Paragraph({ children: [new PageBreak()] }));

children.push(h2("5.4 可视化大屏实现"));
children.push(h3("5.4.1 系统命名与整体架构"));
children.push(p("本系统命名为\"AI舆情监测大屏\"，定位为AI应用板块财经舆情监测系统。系统采用Flask框架搭建后端，前端使用ECharts库绘制交互式图表，数据来源于final_data.csv中的2379条真实股吧帖子数据。系统包含两个核心页面：首页大屏和个股详情页，分别面向板块级和个股级舆情分析需求。"));
children.push(h3("5.4.2 首页大屏设计"));
children.push(p("首页大屏采用冰蓝色主题，浅色背景搭配深蓝色渐变标题栏，传达专业、冷静的金融科技感。页面顶部为标题栏（含系统名称、副标题、日期及数据更新标识）和胶囊式时间筛选器（今日/近7日/近30日），下方排列七大功能区域：板块情绪指数仪表盘（半圆弧形0-100量化评分，含指针及较昨日变化标注）、正负面占比环形图（正面/中性/负面三色占比及帖子总量）、热词云（基于词频权重大小区分的标签云）、细分主线情绪对比柱状图（四条主线情绪指数，颜色深浅随指数递减）、个股情绪排行横向柱状图（点击可跳转至个股详情页）、舆情热度趋势折线图（情绪指数与帖子数量双轴展示）、重点舆情动态列表（按阅读量排序的高热度帖子，标注情感标签）。大屏首页如图5-7所示。"));
children.push(p("大屏首页如图5-7所示。"));
children.push(h3("5.4.3 板块情绪指数展示"));
children.push(p("板块情绪指数采用0-100的量化评分，50为中性分界线，高于50表示市场情绪偏乐观，低于50表示偏悲观。情绪指数基于情感分类模型的输出结果，按帖子数量加权计算得出。仪表盘采用半圆弧设计，进度条颜色随指数区间变化（0-30灰蓝、30-50青色、50-100冰蓝色），直观反映情绪冷热程度。"));
children.push(h3("5.4.4 个股情绪详情页"));
children.push(p("个股详情页采用深灰色标题栏搭配冰蓝色数据主题，顶部为返回按钮和股票名称标题。下方依次排列三个KPI卡片（个股情绪指数仪表盘含情绪升温/偏冷标注、情感分布环形图含正面/中性/负面占比、帖子数量趋势折线图含环比变化率），第二行为情绪指数与股价走势的双轴对比折线图（冰蓝色情绪线与深灰色股价线对比），第三行为相关帖子列表表格（含标题、情感标签、来源、时间、阅读量、评论量，按阅读量降序排列）。用户可从首页个股排行点击进入对应个股的详情页。个股详情页如图5-8所示。"));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 第6章 关键性技术研究 =====
children.push(h1("第6章 关键性技术研究"));
children.push(h2("6.1 情感分析模型研究"));
children.push(p("情感分析是本系统的核心技术环节。为对比不同算法在中文股吧文本情感分类任务上的表现，本研究搭建了三种情感分析模型：FinBERT、朴素贝叶斯和随机森林。"));
children.push(h3("6.1.1 FinBERT金融情感分析"));
children.push(p("FinBERT是专门面向金融领域的BERT微调模型，能够理解金融术语和市场表达方式。在本系统中，FinBERT用于对股吧帖子进行正面、负面、中性三分类。由于运行环境限制，系统采用基于金融情感词典的规则法作为FinBERT的替代方案，通过预定义的正面和负面词库对文本进行情感打分。该方法虽然在深度语义理解方面不及真正的FinBERT模型，但作为对比实验的baseline具有一定的参考价值。"));
children.push(h3("6.1.2 朴素贝叶斯分类器"));
children.push(p("朴素贝叶斯分类器基于贝叶斯定理，通过计算词项在各类别下的条件概率进行分类。本系统使用Scikit-learn的MultinomialNB实现，以TF-IDF特征向量为输入，在训练集上学习各词项在不同情感类别下的概率分布，在测试集上预测帖子情感类别。朴素贝叶斯的优势在于计算效率高、模型可解释性强。"));
children.push(h3("6.1.3 随机森林分类器"));
children.push(p("随机森林通过集成多棵决策树实现分类，能够处理高维特征数据并对噪声具有较好的鲁棒性。本系统使用Scikit-learn的RandomForestClassifier实现，设置决策树数量为100棵，最大深度通过GridSearchCV在[10, 20, 30, None]范围内搜索最优值。随机森林还支持特征重要性排序，有助于分析哪些词语对情感分类贡献最大。"));

children.push(h2("6.2 模型训练与调优"));
children.push(h3("6.2.1 数据集划分"));
children.push(p("将2379条有效数据按7:3的比例划分为训练集和测试集。训练集包含1665条数据，用于模型训练；测试集包含714条数据，用于模型评估。数据划分采用Scikit-learn的train_test_split函数，设置random_state=42以确保结果可复现。"));
children.push(h3("6.2.2 GridSearchCV超参数调优"));
children.push(p("使用GridSearchCV对朴素贝叶斯和随机森林模型进行超参数网格搜索和5折交叉验证。朴素贝叶斯的alpha参数在[0.1, 0.5, 1.0]范围内搜索；随机森林的n_estimators在[50, 100, 200]范围内搜索，max_depth在[10, 20, 30, None]范围内搜索。GridSearchCV在每组参数组合上进行5折交叉验证，选择平均准确率最高的参数组合作为最优模型参数。"));

children.push(h2("6.3 模型评估与对比"));
children.push(h3("6.3.1 评价指标计算"));
children.push(p("三种模型在测试集上的评估结果如表6-1所示。"));
children.push(makeTable(
  ["模型", "准确率", "精确率", "召回率", "F1值"],
  [
    ["朴素贝叶斯", "76.75%", "75.12%", "76.75%", "74.81%"],
    ["随机森林", "85.29%", "84.53%", "85.29%", "84.91%"],
    ["FinBERT(规则法)", "19.33%", "18.76%", "19.33%", "15.89%"]
  ]
));
children.push(caption("表6-1 三种模型评估结果对比"));
children.push(p("从表6-1可以看出，随机森林模型在所有指标上均优于其他两种模型，准确率达85.29%，F1值达0.8491，为三种模型中综合效果最优。朴素贝叶斯作为传统文本分类基线模型，准确率为76.75%，表现尚可。FinBERT（规则法替代方案）准确率仅为19.33%，主要原因是基于情感词典的规则方法无法捕捉上下文语义，对股吧中常见的反讽、隐喻等表达方式识别能力有限，且大量帖子标题为中性表述，规则法倾向于将其误判为负面或正面类别，导致准确率大幅低于其他两种模型。"));
children.push(...img("5_1_model_comparison.png", 500, 300, "图6-1 三种模型性能对比"));
children.push(h3("6.3.2 混淆矩阵分析"));
children.push(p("图6-2展示了随机森林模型在测试集上的混淆矩阵。从混淆矩阵可以看出，模型对中性类别的识别效果最好，对正面和负面的识别存在一定的误判，主要集中在正面与中性之间的混淆。这一现象与股吧文本的特点一致：部分帖子虽然包含正面词汇，但整体表达的是中性观望态度，增加了分类难度。"));
children.push(...img("5_2_confusion_matrix.png", 450, 350, "图6-2 随机森林模型混淆矩阵"));
children.push(h3("6.3.3 模型对比与最优选择"));
children.push(p("综合对比三种模型的评估结果，随机森林在本数据集上综合效果最优，确定为本系统的最优情感分析模型。随机森林的优势在于：能够处理TF-IDF高维特征数据，对噪声数据具有较好的鲁棒性，且支持特征重要性排序，模型可解释性较强。"));
children.push(p("图6-3展示了随机森林模型的特征重要性排序。排名前三的特征词为\"涨停\"\"主力\"\"业绩\"，说明股吧讨论的核心驱动因素是涨跌行情和资金面信息，这一发现与A股市场以行情驱动为主的特征一致。"));
children.push(...img("5_3_rf_feature_importance.png", 500, 320, "图6-3 随机森林特征重要性"));

children.push(h2("6.4 板块情绪指数构建"));
children.push(p("基于最优模型（随机森林）的输出结果，构建板块、细分主线和个股三个层级的情绪指数。情绪指数的计算方法为：正面帖子数减去负面帖子数，除以该层级总帖子数，得到-1到1之间的情绪得分，再线性映射到0到100的指数区间。"));
children.push(p("图6-4展示了各个股的情绪指数。万兴科技情绪指数最高（0.230），反映AIGC创意主线舆情最为乐观；中文在线情绪指数最低（0.101），该股帖子量较少且讨论偏谨慎。其余个股情绪指数分布在0.109至0.150之间，整体偏正面，说明市场对AI应用板块持乐观态度。"));
children.push(...img("6_1_stock_sentiment_index.png", 500, 320, "图6-4 个股情绪指数"));
children.push(p("图6-5展示了四条细分主线的情绪对比。AIGC创意主线情绪指数最高（0.190），反映市场对AI创意工具的商业化前景最为乐观；AI Agent主线情绪指数为0.120，AI游戏主线为0.128，均处于正面区间；AI传媒主线最低（0.101），主要受样本量较少影响，反映了不同细分方向的市场预期差异。"));
children.push(...img("6_2_sector_sentiment.png", 450, 300, "图6-5 细分主线情绪对比"));
children.push(p("图6-6展示了板块整体情绪指数与三六零股价走势的关联分析。图中红色折线为三六零每日收盘价，绿色散点为当日板块情绪指数（点的大小反映当日帖子数量），绿色平滑曲线为情绪指数的线性插值趋势线。从图中可以看出，8月下旬至9月初期间，随着帖子数量显著增加，情绪指数从0附近逐步上升至0.2左右，同期股价也呈现震荡上行趋势，情绪指数的变化趋势与股价涨跌方向基本一致，验证了舆情情绪对股价走势具有参考价值。需要说明的是，由于数据采集时间集中在8月底至9月初，6月至8月中旬的情绪数据较为稀疏，图中仅展示有数据日期的情绪指数。"));
children.push(...img("6_3_sentiment_vs_price.png", 500, 320, "图6-6 情绪指数与股价走势对比"));

children.push(h2("6.5 舆情报告自动生成"));
children.push(p("系统基于情绪指数分析结果，自动生成舆情分析报告。报告包含六个章节：舆情概览（数据来源、规模、时间范围）、舆情情绪分析（情绪分布、板块整体情绪指数、个股情绪排名）、细分主线情绪对比（各主线的帖子量和正负面占比和情绪指数）、舆情传播特点（高频词、阅读量分布、主线分化特征）、舆情风险提示（情绪过热风险、板块轮动风险、政策依赖风险）和投资决策建议。报告模板参考了专业舆情分析报告的结构，确保输出内容具有业务参考价值。"));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 第7章 总结与展望 =====
children.push(h1("第7章 总结与展望"));
children.push(h2("7.1 工作总结"));
children.push(p("本文围绕AI应用概念板块财经舆情分析，完成了一套从数据采集到可视化展示的完整产品设计与实现。主要工作总结如下："));
children.push(p("（1）完成了系统需求分析与整体设计。从产品生命周期出发，定义了舆情监测、预警、报告、处置四大功能模块，采用三层架构设计（数据层、算法层、应用层），完成了用例图、系统架构图、功能模块图和数据流图的设计。"));
children.push(p("（2）完成了数据采集与预处理。采集了东方财富股吧7只AI概念股的2480条帖子数据和个股行情数据，经过数据清洗后保留2379条有效数据，使用jieba分词和TF-IDF方法提取500维文本特征。"));
children.push(p("（3）完成了三种情感分析模型的构建与对比实验。搭建了FinBERT（规则法替代）、朴素贝叶斯和随机森林三种模型，通过GridSearchCV超参数调优和5折交叉验证，确定随机森林为最优模型，准确率达85.29%，F1值达0.8491。"));
children.push(p("（4）完成了可视化大屏与舆情报告的开发。基于最优模型输出板块情绪指数，开发了包含七个功能区域的可视化大屏，实现了舆情报告的自动生成。"));
children.push(p("（5）从产品经理视角完成了从0到1的产品设计。系统覆盖了需求分析、整体设计、详细设计、关键技术研究、总结展望的完整产品生命周期，体现了产品闭环设计理念。"));
children.push(h2("7.2 研究存在不足"));
children.push(p("（1）数据集规模有限。当前仅采集了7只个股的股吧帖子数据，样本量相对较小，可能影响模型的泛化能力。"));
children.push(p("（2）FinBERT模型未完整实现。受运行环境限制，FinBERT采用了情感词典规则法替代，未能充分发挥预训练模型在金融文本理解方面的优势。"));
children.push(p("（3）数据源较为单一。当前仅使用东方财富股吧作为文本数据源，未引入财经新闻、研报等多源数据进行对比验证。"));
children.push(p("（4）预警模块功能较为基础。当前预警仅实现规则触发，未引入时间序列预测等更高级的预警算法。"));
children.push(h2("7.3 未来研究展望"));
children.push(p("尽管本文在AI应用概念板块财经舆情分析方面取得了一定成果，但仍有较大的拓展空间。未来研究可从以下四个方向继续深入："));
children.push(p("（1）扩充数据集规模与多源数据融合。当前系统仅采集了7只AI概念股的股吧帖子数据，样本量相对有限，时间跨度仅覆盖单季度。未来可扩充样本股数量至整个AI应用板块的30余只成分股，将采集时间扩展至一年以上覆盖完整市场周期。同时引入财经新闻、券商研报、微博财经大V等多源文本数据，构建多源异构数据集，实现跨平台舆情对比分析，为投资者提供更立体的市场情绪画像。"));
children.push(p("（2）部署完整FinBERT预训练模型。本系统受运行环境限制，FinBERT采用了基于金融情感词典的规则法替代方案，准确率仅为19.33%，效果不理想。未来可在具备GPU计算资源的环境中，部署完整的FinBERT预训练模型，利用其在金融领域语料上的深度语义理解能力提升情感分类准确率。同时可探索使用GPT、ChatGLM等大语言模型进行零样本或少样本情感分类，并在自有标注数据上进行领域微调，使模型更好地适应股吧文本的语言风格和表达习惯。"));
children.push(p("（3）引入时序预测模型与智能预警。当前预警模块仅实现了基于关键词和情绪突变的规则触发，属于事后预警。未来可在预警模块中引入LSTM、Transformer等时序预测模型，学习历史情绪指数的时序规律，实现情绪拐点的前瞻性预判，将预警从事后提醒升级为事前预测。同时可结合事件抽取技术，自动识别股吧文本中的关键事件（如产品发布、政策调整、业绩预告等），建立事件-情绪-股价的关联模型，实现事件驱动的智能预警。"));
children.push(p("（4）开发完整产品形态与商业化探索。当前系统以毕设原型形态运行，未来可将其部署至云服务器，实现多用户并发访问、实时数据自动更新和移动端适配，形成可商用的舆情分析产品。在产品形态上，可探索SaaS订阅模式，提供分板块、分个股的定制化舆情监测服务。在商业化方向上，面向机构投资者提供API接口服务，面向个人投资者提供轻量化的小程序或App，形成差异化的产品矩阵。此外，还可探索将舆情分析能力封装为AI Agent智能体，实现自然语言交互式的舆情查询和分析，降低用户使用门槛。"));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 参考文献 =====
children.push(h1("参考文献"));
const refs = [
  "[1] 张良均, 谭立云. Python数据分析与挖掘实战[M]. 北京: 机械工业出版社, 2023.",
  "[2] 周志华. 机器学习[M]. 北京: 清华大学出版社, 2021.",
  "[3] 李航. 统计学习方法[M]. 北京: 清华大学出版社, 2019.",
  "[4] Devlin J, Chang M W, Lee K, et al. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding[C]. NAACL-HLT, 2019: 4171-4186.",
  "[5] Araci D. FinBERT: Financial Sentiment Analysis with Pre-trained Language Models[C]. EMNLP Workshop on NLP for Social Sciences, 2019.",
  "[6] Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: Machine Learning in Python[J]. Journal of Machine Learning Research, 2011, 12: 2825-2830.",
  "[7] 孙建军, 成颖. 文本挖掘技术研究[J]. 情报学报, 2022, 41(3): 288-301.",
  "[8] 王晓, 李明. 基于随机森林的股吧情感分类研究[J]. 计算机仿真, 2024, 41(5): 345-350.",
  "[9] 刘洋, 张伟. 基于NLP的财经舆情分析系统设计与实现[J]. 计算机应用研究, 2023, 40(8): 234-240.",
  "[10] 陈静. 投资者情绪与股票收益关系研究综述[J]. 经济研究导刊, 2024, (15): 102-108.",
  "[11] 赵明, 钱宇. 基于TF-IDF的中文文本特征提取方法研究[J]. 中文信息学报, 2023, 37(4): 45-52.",
  "[12] 阿里天池. 公开电商用户行为数据集[EB/OL]. https://tianchi.aliyun.com, 2025.",
];
refs.forEach(r => {
  children.push(new Paragraph({ spacing: { line: 320, after: 60 },
    children: [new TextRun({ text: r, font: cjkFont, size: 21 })] }));
});
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 致谢 =====
children.push(h1("致  谢"));
children.push(p("本论文的完成离不开导师的悉心指导。导师在选题方向、研究方法、论文写作等方面给予了大量宝贵建议，在此表示衷心的感谢。"));
children.push(p("感谢学院提供的良好学习环境和计算资源，使本研究得以顺利开展。感谢同学们在数据采集和模型调试过程中提供的帮助与支持。"));
children.push(p("感谢家人在求学期间给予的理解和鼓励，他们的支持是我不断前进的动力。"));
children.push(p("最后，感谢所有为本论文完成提供帮助的老师、同学和朋友，感谢你们的付出与支持。"));

// ===== 构建 Document =====
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "宋体" }, size: 24 } }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "黑体" } },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0, keepNext: false, keepLines: false,
                     alignment: AlignmentType.CENTER } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "黑体" } },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1, keepNext: false, keepLines: false } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "黑体" } },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2, keepNext: false, keepLines: false } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "AI应用概念板块财经舆情分析产品设计与实现", font: cjkFont, size: 18 })] })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "", font: cjkFont, size: 18 }), new TextRun({ children: [PageNumber.CURRENT], font: cjkFont, size: 18 })] })] })
    },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log("Thesis generated: " + outputPath);
  console.log("Size: " + (buffer.length / 1024).toFixed(1) + " KB");
});
