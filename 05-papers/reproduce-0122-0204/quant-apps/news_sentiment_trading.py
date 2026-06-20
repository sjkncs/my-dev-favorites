"""
LLM新闻情感分析驱动的股价预测框架
基于 arXiv:2602.00086 (LLM News Sentiment for Stock Prediction)

核心思想:
1. 用LLM（或模拟LLM）对新闻进行多维度情感打分
2. 情感信号转化为交易特征
3. 量化LLM情感vs传统NLP情感的增量Alpha
4. 情感驱动的交易策略回测

运行: python news_sentiment_trading.py
"""
import numpy as np
import json
import os
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# ============================================================
# 1. 新闻情感分析器（模拟LLM多维度情感输出）
# ============================================================

@dataclass
class NewsItem:
    date: str
    title: str
    source: str
    sector: str
    content_snippet: str = ""

@dataclass
class SentimentScore:
    overall: float = 0.0         # -1 到 +1
    bullish_signals: float = 0.0 # 0 到 1
    bearish_signals: float = 0.0 # 0 到 1
    uncertainty: float = 0.0     # 0 到 1
    sector_impact: float = 0.0   # -1 到 +1
    confidence: float = 0.0      # 0 到 1

class LLMSentimentAnalyzer:
    """
    模拟LLM多维度情感分析（arXiv:2602.00086的核心方法）
    实际部署时替换为真实LLM API调用
    """
    
    # 金融领域关键词情感词典
    BULLISH_KEYWORDS = {
        "strong": 0.8, "growth": 0.7, "record": 0.9, "beat": 0.7, "upgrade": 0.6,
        "breakthrough": 0.8, "partnership": 0.5, "acquisition": 0.4, "innovation": 0.6,
        "expansion": 0.5, "profit": 0.6, "revenue": 0.4, "surge": 0.8, "rally": 0.7,
        "outperform": 0.7, "exceed": 0.7, "milestone": 0.6, "launch": 0.5,
        "超预期": 0.8, "增长": 0.6, "突破": 0.7, "创新": 0.6, "利好": 0.8,
        "新高": 0.7, "大涨": 0.8, "盈利": 0.5, "合作": 0.4, "扩展": 0.5,
    }
    
    BEARISH_KEYWORDS = {
        "decline": -0.7, "loss": -0.6, "miss": -0.7, "downgrade": -0.6, "risk": -0.4,
        "crisis": -0.9, "lawsuit": -0.7, "recall": -0.6, "bankruptcy": -0.95,
        "selloff": -0.8, "crash": -0.9, "warning": -0.5, "cut": -0.5, "layoff": -0.6,
        "investigation": -0.5, "penalty": -0.6, "disappoint": -0.7, "concern": -0.4,
        "下跌": -0.7, "亏损": -0.6, "风险": -0.4, "利空": -0.8, "暴跌": -0.9,
        "预警": -0.5, "调查": -0.5, "处罚": -0.6, "裁员": -0.6, "诉讼": -0.6,
    }
    
    SECTOR_KEYWORDS = {
        "AI": ["AI", "artificial intelligence", "LLM", "GPT", "agent", "AI模型", "人工智能"],
        "Tech": ["tech", "software", "semiconductor", "chip", "cloud", "科技", "芯片", "半导体"],
        "Energy": ["oil", "energy", "solar", "renewable", "能源", "新能源", "光伏"],
        "Finance": ["bank", "fintech", "trading", "金融", "银行", "支付"],
    }
    
    def analyze(self, news: NewsItem) -> SentimentScore:
        """多维度情感分析"""
        text = f"{news.title} {news.content_snippet}".lower()
        
        # 基础情感分数
        bull_score = sum(self.BULLISH_KEYWORDS.get(kw, 0) for kw in self.BULLISH_KEYWORDS if kw.lower() in text)
        bear_score = sum(self.BEARISH_KEYWORDS.get(kw, 0) for kw in self.BEARISH_KEYWORDS if kw.lower() in text)
        
        total_signal = abs(bull_score) + abs(bear_score) + 1e-8
        overall = (bull_score + bear_score) / total_signal
        overall = max(-1, min(1, overall))
        
        # 不确定性（基于矛盾信号）
        uncertainty = min(abs(bull_score), abs(bear_score)) / (total_signal / 2 + 1e-8)
        
        # 置信度（基于信号强度）
        confidence = min(total_signal / 3.0, 1.0)
        
        # 行业影响
        sector_impact = 0.0
        for sector, keywords in self.SECTOR_KEYWORDS.items():
            if any(kw.lower() in text for kw in keywords):
                sector_impact = overall * 0.8  # 行业相关性衰减
                break
        
        return SentimentScore(
            overall=round(overall, 4),
            bullish_signals=round(max(bull_score / 3.0, 0), 4),
            bearish_signals=round(max(-bear_score / 3.0, 0), 4),
            uncertainty=round(uncertainty, 4),
            sector_impact=round(sector_impact, 4),
            confidence=round(confidence, 4),
        )

class TraditionalNLPSentiment:
    """传统NLP情感分析（作为对比基线）"""
    
    POSITIVE = {"good", "great", "strong", "positive", "up", "rise", "gain",
                "好", "强", "涨", "增", "正"}
    NEGATIVE = {"bad", "poor", "weak", "negative", "down", "fall", "loss",
                "坏", "弱", "跌", "减", "负"}
    
    def analyze(self, news: NewsItem) -> float:
        text = f"{news.title} {news.content_snippet}".lower()
        pos = sum(1 for w in self.POSITIVE if w in text)
        neg = sum(1 for w in self.NEGATIVE if w in text)
        total = pos + neg + 1e-8
        return (pos - neg) / total

# ============================================================
# 2. 模拟新闻数据生成
# ============================================================

def generate_news_data(n_days=100, n_news_per_day=5, seed=42):
    """生成模拟新闻数据"""
    rng = np.random.default_rng(seed)
    
    news_templates = [
        # 利好新闻
        ("AI Agent Framework {company} Raises $500M Series C", "AI", 0.7),
        ("{company} Reports Record Q4 Revenue, Beats Estimates by 15%", "Tech", 0.8),
        ("Major Breakthrough in {sector} Technology Announced by {company}", "Tech", 0.6),
        ("{company} Forms Strategic Partnership with Leading Cloud Provider", "Tech", 0.5),
        ("Analysts Upgrade {company} to Strong Buy on AI Growth", "Tech", 0.7),
        ("{sector} Sector Hits New All-Time High on Strong Demand", "Energy", 0.6),
        ("{company} Launches Revolutionary Product, Exceeds Expectations", "Tech", 0.8),
        ("{company}盈利超预期，净利润增长40%", "Tech", 0.7),
        ("{company}获大额政府补贴，利好新能源发展", "Energy", 0.6),
        # 利空新闻
        ("{company} Misses Q4 Earnings, Revenue Declines 8%", "Tech", -0.7),
        ("Regulatory Investigation into {company}'s AI Practices", "Tech", -0.5),
        ("{company} Announces 10,000 Layoffs Amid Market Concerns", "Tech", -0.6),
        ("{sector} Stocks Selloff Continues for Third Day", "Energy", -0.8),
        ("{company} Faces Class Action Lawsuit Over Data Breach", "Tech", -0.7),
        ("Risk Warning: {sector} Bubble May Burst, Analysts Say", "Finance", -0.5),
        ("{company}产品召回事件影响扩大，股价暴跌", "Tech", -0.8),
        # 中性/矛盾新闻
        ("{company} Reports Mixed Results: Revenue Up but Margins Down", "Tech", 0.0),
        ("Analysts Divided on {company}'s AI Strategy Outlook", "Tech", 0.0),
        ("{sector} Market Uncertainty Persists as New Data Emerges", "Finance", -0.1),
    ]
    
    companies = ["OpenAI", "Google", "NVIDIA", "Meta", "Microsoft", "Amazon", 
                 "Tesla", "Apple", "ByteDance", "Alibaba", "Tencent", "Baidu"]
    sectors = ["AI", "Tech", "Energy", "Finance"]
    
    all_news = []
    base_date = datetime(2025, 6, 1)
    
    for day in range(n_days):
        dt = base_date + timedelta(days=day)
        date_str = dt.strftime("%Y-%m-%d")
        n_news = rng.integers(3, n_news_per_day + 3)
        
        for _ in range(n_news):
            template, sector, base_sentiment = rng.choice(news_templates)
            company = rng.choice(companies)
            title = template.format(company=company, sector=sector)
            
            all_news.append(NewsItem(
                date=date_str,
                title=title,
                source=rng.choice(["Reuters", "Bloomberg", "CNBC", "财联社", "WSJ"]),
                sector=sector,
                content_snippet=title,  # simplified
            ))
    
    return all_news

# ============================================================
# 3. 情感信号 → 交易策略
# ============================================================

class SentimentTradingStrategy:
    """情感驱动交易策略"""
    
    def __init__(self, analyzer, lookback=5, threshold=0.2, 
                 use_llm_features=False):
        self.analyzer = analyzer
        self.lookback = lookback
        self.threshold = threshold
        self.use_llm_features = use_llm_features
        self.name = "LLM-Sentiment" if use_llm_features else "NLP-Sentiment"
    
    def compute_daily_sentiment(self, news_by_date: Dict[str, List[NewsItem]]) -> Dict[str, float]:
        """计算每日情感分数"""
        daily_sentiment = {}
        
        for date, news_list in news_by_date.items():
            if not news_list:
                continue
            
            if self.use_llm_features:
                scores = [self.analyzer.analyze(n) for n in news_list]
                # 多维度加权
                weighted = sum(
                    s.overall * 0.4 + 
                    (s.bullish_signals - s.bearish_signals) * 0.3 +
                    s.sector_impact * 0.2 +
                    (1 - s.uncertainty) * s.confidence * 0.1
                    for s in scores
                ) / len(scores)
                daily_sentiment[date] = weighted
            else:
                scores = [self.analyzer.analyze(n) for n in news_list]
                daily_sentiment[date] = sum(scores) / len(scores)
        
        return daily_sentiment
    
    def generate_signals(self, daily_sentiment: Dict[str, float], 
                         dates: List[str]) -> np.ndarray:
        """基于情感移动平均生成交易信号"""
        sentiment_series = np.array([daily_sentiment.get(d, 0) for d in dates])
        signals = np.zeros(len(dates))
        
        for i in range(self.lookback, len(dates)):
            ma = np.mean(sentiment_series[i-self.lookback:i])
            current = sentiment_series[i]
            
            # 信号 = 当前情感 vs 近期均值 + 动量
            momentum = current - ma
            if momentum > self.threshold:
                signals[i] = 1
            elif momentum < -self.threshold:
                signals[i] = -1
        
        return signals

# ============================================================
# 4. 增量Alpha分析
# ============================================================

def compute_incremental_alpha(llm_signals, nlp_signals, returns):
    """计算LLM情感相对传统NLP的增量预测能力"""
    n = min(len(llm_signals), len(nlp_signals), len(returns))
    llm_sig = llm_signals[:n]
    nlp_sig = nlp_signals[:n]
    ret = returns[:n]
    
    # 信息系数（IC）
    ic_llm = np.corrcoef(llm_sig, ret)[0, 1] if np.std(llm_sig) > 0 else 0
    ic_nlp = np.corrcoef(nlp_sig, ret)[0, 1] if np.std(nlp_sig) > 0 else 0
    
    # 分层收益
    llm_long_ret = np.mean(ret[llm_sig > np.percentile(llm_sig, 70)])
    llm_short_ret = np.mean(ret[llm_sig < np.percentile(llm_sig, 30)])
    nlp_long_ret = np.mean(ret[nlp_sig > np.percentile(nlp_sig, 70)])
    nlp_short_ret = np.mean(ret[nlp_sig < np.percentile(nlp_sig, 30)])
    
    return {
        "ic_llm": round(ic_llm, 4),
        "ic_nlp": round(ic_nlp, 4),
        "incremental_ic": round(ic_llm - ic_nlp, 4),
        "llm_long_short_spread": round(llm_long_ret - llm_short_ret, 6),
        "nlp_long_short_spread": round(nlp_long_ret - nlp_short_ret, 6),
        "incremental_spread": round((llm_long_ret - llm_short_ret) - (nlp_long_ret - nlp_short_ret), 6),
        "llm_annualized_alpha": round((llm_long_ret - llm_short_ret) * 252 * 100, 2),
        "nlp_annualized_alpha": round((nlp_long_ret - nlp_short_ret) * 252 * 100, 2),
    }

# ============================================================
# 5. 主程序
# ============================================================

def main():
    print("=" * 70)
    print("LLM新闻情感分析 × 股价预测框架")
    print("基于 arXiv:2602.00086 (LLM News Sentiment for Stock Prediction)")
    print("=" * 70)
    
    # 生成新闻数据
    news_data = generate_news_data(n_days=100, n_news_per_day=5)
    print(f"\n新闻数据: {len(news_data)} 条, {news_data[0].date} ~ {news_data[-1].date}")
    
    # 按日期分组
    news_by_date = {}
    for n in news_data:
        if n.date not in news_by_date:
            news_by_date[n.date] = []
        news_by_date[n.date].append(n)
    
    dates = sorted(news_by_date.keys())
    
    # 生成模拟收益率（与情感有一定相关性）
    rng = np.random.default_rng(42)
    base_returns = rng.normal(0.0003, 0.015, len(dates))
    
    # 注入情感-收益相关性
    llm_analyzer = LLMSentimentAnalyzer()
    for i, d in enumerate(dates):
        if d in news_by_date:
            scores = [llm_analyzer.analyze(n) for n in news_by_date[d]]
            avg_sentiment = np.mean([s.overall for s in scores])
            base_returns[i] += avg_sentiment * 0.003  # 情感影响收益
    
    # LLM情感策略
    llm_strategy = SentimentTradingStrategy(llm_analyzer, use_llm_features=True)
    llm_daily_sentiment = llm_strategy.compute_daily_sentiment(news_by_date)
    llm_signals = llm_strategy.generate_signals(llm_daily_sentiment, dates)
    
    # 传统NLP策略
    nlp_analyzer = TraditionalNLPSentiment()
    nlp_strategy = SentimentTradingStrategy(nlp_analyzer, use_llm_features=False)
    nlp_daily_sentiment = nlp_strategy.compute_daily_sentiment(news_by_date)
    nlp_signals = nlp_strategy.generate_signals(nlp_daily_sentiment, dates)
    
    # 增量Alpha分析
    print("\n" + "=" * 70)
    print("增量Alpha分析: LLM情感 vs 传统NLP情感")
    print("=" * 70)
    
    alpha = compute_incremental_alpha(llm_signals, nlp_signals, base_returns)
    for k, v in alpha.items():
        print(f"  {k:30s}: {v}")
    
    # 情感分布统计
    print("\n" + "=" * 70)
    print("每日情感分布统计")
    print("=" * 70)
    
    llm_vals = list(llm_daily_sentiment.values())
    nlp_vals = list(nlp_daily_sentiment.values())
    
    print(f"\n  LLM情感:")
    print(f"    均值: {np.mean(llm_vals):.4f}")
    print(f"    标准差: {np.std(llm_vals):.4f}")
    print(f"    偏度: {np.mean([(v-np.mean(llm_vals))**3 for v in llm_vals]) / (np.std(llm_vals)+1e-8)**3:.4f}")
    print(f"    极值: [{min(llm_vals):.4f}, {max(llm_vals):.4f}]")
    
    print(f"\n  NLP情感:")
    print(f"    均值: {np.mean(nlp_vals):.4f}")
    print(f"    标准差: {np.std(nlp_vals):.4f}")
    print(f"    极值: [{min(nlp_vals):.4f}, {max(nlp_vals):.4f}]")
    
    # 信号质量评估
    print("\n" + "=" * 70)
    print("信号质量对比")
    print("=" * 70)
    
    for name, signals in [("LLM多维情感", llm_signals), ("传统NLP", nlp_signals)]:
        n_long = sum(signals > 0)
        n_short = sum(signals < 0)
        n_flat = sum(signals == 0)
        
        long_ret = np.mean(base_returns[signals > 0]) if n_long > 0 else 0
        short_ret = np.mean(base_returns[signals < 0]) if n_short > 0 else 0
        
        print(f"\n  {name}:")
        print(f"    做多信号: {n_long} 天, 次日收益: {long_ret*100:.4f}%")
        print(f"    做空信号: {n_short} 天, 次日收益: {short_ret*100:.4f}%")
        print(f"    空仓: {n_flat} 天")
        print(f"    多空价差: {(long_ret - short_ret)*100:.4f}%")
    
    # 保存报告
    report = {
        "title": "LLM News Sentiment vs Traditional NLP - Incremental Alpha Analysis",
        "paper": "arXiv:2602.00086",
        "period": f"{dates[0]} ~ {dates[-1]}",
        "n_news": len(news_data),
        "alpha_analysis": alpha,
        "llm_sentiment_stats": {
            "mean": round(np.mean(llm_vals), 4),
            "std": round(np.std(llm_vals), 4),
        },
        "nlp_sentiment_stats": {
            "mean": round(np.mean(nlp_vals), 4),
            "std": round(np.std(nlp_vals), 4),
        },
    }
    
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentiment_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_path}")
    print("\n分析完成！")

if __name__ == "__main__":
    main()
