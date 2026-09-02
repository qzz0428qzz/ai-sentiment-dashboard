"""
FinBERT 情感分析模型
对股吧评论进行正面/负面/中性分类
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np


class FinBERTSentiment:
    def __init__(self):
        model_name = "yiyanghkust/finbert-tone"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ["正面", "负面", "中性"]

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1).numpy()[0]
        label_idx = np.argmax(scores)
        return {
            "label": self.labels[label_idx],
            "score": float(scores[label_idx]),
            "scores": {self.labels[i]: float(scores[i]) for i in range(len(self.labels))},
        }

    def predict_batch(self, texts):
        results = []
        for text in texts:
            results.append(self.predict(text))
        return results


if __name__ == "__main__":
    analyzer = FinBERTSentiment()
    test_text = "讯飞大模型又要放大招了，这次看涨"
    result = analyzer.predict(test_text)
    print(f"文本: {test_text}")
    print(f"结果: {result}")
