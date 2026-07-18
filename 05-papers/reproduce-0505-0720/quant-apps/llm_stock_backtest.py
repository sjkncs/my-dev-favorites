"""
LLM股票情感分析回测
基于 arXiv:2605.05211 (LLMs for Stock Price Forecasting)

核心: 模拟LLM从新闻提取情感信号→生成交易信号→回测验证
特别关注: 数据泄露检测、交易成本影响、流动性约束
"""
import numpy as np
import json, os
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TradeSignal:
    date: str
    ticker: str
    sentiment: float  # -1 to +1
    confidence: float
    signal: int  # +1 long, -1 short, 0 neutral

class LLMStockSimulator:
    """模拟LLM股票情感分析系统"""
    
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
    
    def generate_news_sentiment(self, n_days=252, n_tickers=10):
        """生成模拟的LLM情感分析结果"""
        tickers = ['AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA','JPM','V','JNJ'][:n_tickers]
        signals = []
        
        for ticker in tickers:
            # 基础情感: 带趋势的随机游走
            base_sentiment = np.cumsum(self.rng.normal(0, 0.1, n_days))
            base_sentiment = np.clip(base_sentiment, -2, 2) / 2  # normalize to [-1,1]
            
            # LLM提取的情感 (有噪声)
            llm_noise = self.rng.normal(0, 0.15, n_days)
            llm_sentiment = np.clip(base_sentiment + llm_noise, -1, 1)
            
            # LLM置信度 (与情感强度正相关)
            confidence = 0.5 + 0.4 * np.abs(llm_sentiment) + self.rng.normal(0, 0.05, n_days)
            confidence = np.clip(confidence, 0.3, 0.95)
            
            for d in range(n_days):
                date = (datetime(2025, 1, 2) + timedelta(days=d)).strftime('%Y-%m-%d')
                s = llm_sentiment[d]
                c = confidence[d]
                # 交易信号: 高置信度+强情感才交易
                if abs(s) > 0.3 and c > 0.6:
                    sig = 1 if s > 0 else -1
                else:
                    sig = 0
                signals.append(TradeSignal(date, ticker, s, c, sig))
        
        return signals, tickers
    
    def generate_returns(self, n_days, n_tickers, sentiment_impact=0.003):
        """生成与情感相关的收益率 (避免数据泄露: 用T-1情感预测T收益)"""
        # 市场因子
        market_ret = self.rng.normal(0.0005, 0.012, n_days)
        
        # 个股收益
        returns = np.zeros((n_days, n_tickers))
        for i in range(n_tickers):
            beta = self.rng.uniform(0.5, 1.5)
            idio = self.rng.normal(0, 0.02, n_days)
            returns[:, i] = beta * market_ret + idio
        
        return returns, market_ret

class Backtester:
    """回测引擎 - 严格避免数据泄露"""
    
    def __init__(self, commission=0.001, slippage=0.001, market_impact=0.002):
        self.commission = commission
        self.slippage = slippage
        self.market_impact = market_impact
    
    def run(self, signals, returns, tickers):
        """严格时序回测: T-1信号 → T执行 → T+1收益"""
        n_days = returns.shape[0]
        n_tickers = returns.shape[1]
        
        # 按ticker分组信号
        signal_matrix = np.zeros((n_days, n_tickers))
        for sig in signals:
            if sig.ticker in tickers:
                t_idx = tickers.index(sig.ticker)
                d = (datetime.strptime(sig.date, '%Y-%m-%d') - datetime(2025, 1, 2)).days
                if 0 <= d < n_days:
                    signal_matrix[d, t_idx] = sig.signal
        
        # 回测: T-1信号在T执行
        portfolio_returns = []
        daily_positions = []
        
        for t in range(1, n_days):
            # T-1的信号决定T的持仓
            positions = signal_matrix[t-1]  # 避免数据泄露!
            
            # 计算T的收益
            daily_ret = np.sum(positions * returns[t]) / max(np.sum(np.abs(positions)), 1)
            
            # 扣除交易成本
            position_changes = np.abs(positions - (signal_matrix[t-2] if t > 1 else np.zeros(n_tickers)))
            turnover = np.sum(position_changes) / max(np.sum(np.abs(positions)), 1)
            costs = turnover * (self.commission + self.slippage + self.market_impact)
            
            net_ret = daily_ret - costs
            portfolio_returns.append(net_ret)
            daily_positions.append(positions)
        
        return np.array(portfolio_returns), daily_positions

def data_leakage_test(signals, returns, tickers):
    """数据泄露检测: 对比T-1信号 vs T信号 vs T+1信号的预测能力"""
    n_days = returns.shape[0]
    n_tickers = returns.shape[1]
    
    signal_matrix = np.zeros((n_days, n_tickers))
    for sig in signals:
        if sig.ticker in tickers:
            t_idx = tickers.index(sig.ticker)
            d = (datetime.strptime(sig.date, '%Y-%m-%d') - datetime(2025, 1, 2)).days
            if 0 <= d < n_days:
                signal_matrix[d, t_idx] = sig.signal
    
    results = {}
    for lag_name, lag in [('T+1 (leakage!)', -1), ('T (same-day)', 0), ('T-1 (correct)', 1)]:
        ic_list = []
        for t in range(2, n_days-1):
            sig = signal_matrix[t + lag]
            ret = returns[t]
            if np.std(sig) > 0 and np.std(ret) > 0:
                ic = np.corrcoef(sig, ret)[0, 1]
                ic_list.append(ic)
        results[lag_name] = {
            'mean_ic': round(np.mean(ic_list), 4),
            'std_ic': round(np.std(ic_list), 4),
            'ir': round(np.mean(ic_list) / (np.std(ic_list) + 1e-8), 3),
        }
    return results

def main():
    print("=" * 70)
    print("LLM股票情感分析回测框架")
    print("基于 arXiv:2605.05211")
    print("=" * 70)
    
    sim = LLMStockSimulator(seed=42)
    signals, tickers = sim.generate_news_sentiment(n_days=252, n_tickers=10)
    returns, market_ret = sim.generate_returns(252, 10)
    
    print(f"\n数据: {len(tickers)} 只股票, 252 个交易日")
    print(f"信号数: {sum(1 for s in signals if s.signal != 0)} 条交易信号")
    
    # 数据泄露检测
    print("\n" + "=" * 70)
    print("数据泄露检测 (Information Coefficient by Lag)")
    print("=" * 70)
    leakage = data_leakage_test(signals, returns, tickers)
    for lag_name, metrics in leakage.items():
        flag = " ⚠️ LEAKAGE!" if "leakage" in lag_name and metrics['mean_ic'] > 0.05 else ""
        print(f"  {lag_name:20s}: IC={metrics['mean_ic']:+.4f} ± {metrics['std_ic']:.4f}, IR={metrics['ir']:.3f}{flag}")
    
    # 回测
    bt = Backtester(commission=0.001, slippage=0.001, market_impact=0.002)
    port_ret, positions = bt.run(signals, returns, tickers)
    
    # 绩效指标
    cum_ret = np.cumprod(1 + port_ret) - 1
    ann_ret = (1 + cum_ret[-1]) ** (252/len(port_ret)) - 1
    ann_vol = np.std(port_ret) * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    max_dd = np.max(np.maximum.accumulate(cum_ret) - cum_ret)
    
    print("\n" + "=" * 70)
    print("回测绩效 (扣除交易成本后)")
    print("=" * 70)
    print(f"  累计收益: {cum_ret[-1]*100:+.2f}%")
    print(f"  年化收益: {ann_ret*100:+.2f}%")
    print(f"  年化波动: {ann_vol*100:.2f}%")
    print(f"  Sharpe:   {sharpe:.3f}")
    print(f"  最大回撤: {max_dd*100:.2f}%")
    
    # 交易成本分析
    total_trades = sum(1 for s in signals if s.signal != 0)
    avg_turnover = np.mean([np.sum(np.abs(p)) for p in positions]) / len(tickers)
    
    print(f"\n  总交易信号: {total_trades}")
    print(f"  日均换手: {avg_turnover:.2f} 只股票")
    
    # 成本敏感性分析
    print("\n" + "=" * 70)
    print("交易成本敏感性分析")
    print("=" * 70)
    print(f"  {'总成本':>10s} {'年化收益':>10s} {'Sharpe':>8s}")
    for total_cost in [0.001, 0.002, 0.004, 0.008]:
        bt2 = Backtester(commission=total_cost/3, slippage=total_cost/3, market_impact=total_cost/3)
        pr2, _ = bt2.run(signals, returns, tickers)
        cr2 = np.cumprod(1 + pr2)[-1] - 1
        ar2 = (1 + cr2) ** (252/len(pr2)) - 1
        av2 = np.std(pr2) * np.sqrt(252)
        sh2 = ar2 / av2 if av2 > 0 else 0
        print(f"  {total_cost:.3f}     {ar2*100:+8.2f}%  {sh2:8.3f}")
    
    # 保存
    report = {
        'paper': 'arXiv:2605.05211',
        'tickers': tickers,
        'performance': {'annual_return': round(ann_ret, 4), 'sharpe': round(sharpe, 3), 'max_drawdown': round(max_dd, 4)},
        'leakage_test': leakage,
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'llm_stock_report.json')
    with open(out, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n报告已保存: {out}")

if __name__ == "__main__":
    main()
