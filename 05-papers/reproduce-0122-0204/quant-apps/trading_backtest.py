"""
PredictionMarketBench + GT-Score: 量化交易Agent回测框架
基于 arXiv:2602.00133 (PredictionMarketBench) 和 arXiv:2602.00080 (GT-Score)

核心思想:
1. SWE-bench风格的标准化交易Agent评估
2. GT-Score防过拟合目标函数（替代传统Sharpe Ratio）
3. Walk-forward验证确保样本外稳健性

运行: python trading_backtest.py
输出: 回测报告、绩效指标、策略对比图
"""
import numpy as np
import json
import os
import warnings
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

warnings.filterwarnings('ignore', category=RuntimeWarning)

# ============================================================
# 1. 模拟市场数据生成（真实市场统计特征）
# ============================================================

class MarketSimulator:
    """生成具有真实市场统计特征的价格数据"""
    
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
    
    def generate_ohlcv(self, n_days=500, mu=0.0005, sigma=0.02, 
                       jump_prob=0.02, jump_size=0.05):
        """生成带有跳跃特征的OHLCV数据（模拟A股/美股特征）"""
        dates = []
        dt = datetime(2025, 1, 2)
        for _ in range(n_days):
            while dt.weekday() >= 5:  # skip weekends
                dt += timedelta(days=1)
            dates.append(dt.strftime("%Y-%m-%d"))
            dt += timedelta(days=1)
        
        # 收益率序列：正态 + 偶尔跳跃
        returns = self.rng.normal(mu, sigma, n_days)
        jumps = self.rng.choice([0, 1], size=n_days, p=[1-jump_prob, jump_prob])
        jump_magnitudes = self.rng.choice([-1, 1], size=n_days) * jump_size
        returns += jumps * jump_magnitudes
        
        # 自相关（动量效应）
        for i in range(1, n_days):
            returns[i] += 0.05 * returns[i-1]
        
        # 波动率聚集（GARCH-like）
        vol = np.ones(n_days) * sigma
        for i in range(1, n_days):
            vol[i] = 0.9 * vol[i-1] + 0.1 * abs(returns[i-1]) + 0.01 * sigma
        
        prices = [100.0]
        for r in returns[1:]:
            prices.append(prices[-1] * (1 + r))
        
        # OHLC
        opens, highs, lows, closes = [], [], [], []
        for i, p in enumerate(prices):
            daily_range = p * vol[i] * self.rng.uniform(0.5, 1.5)
            opens.append(p + self.rng.uniform(-daily_range/2, daily_range/2))
            closes.append(p * (1 + returns[i]) if i < len(returns) else p)
            highs.append(max(opens[-1], closes[-1]) + abs(self.rng.normal(0, daily_range/3)))
            lows.append(min(opens[-1], closes[-1]) - abs(self.rng.normal(0, daily_range/3)))
        
        # 成交量（对数正态 + 价格变化相关性）
        base_vol = 1e6
        volumes = base_vol * np.exp(self.rng.normal(0, 0.3, n_days))
        volumes *= (1 + 2 * abs(returns[:n_days]))  # 大波动时放量
        
        return {
            "dates": dates[:n_days],
            "open": np.array(opens[:n_days]),
            "high": np.array(highs[:n_days]),
            "low": np.array(lows[:n_days]),
            "close": np.array(prices[:n_days]),
            "volume": volumes[:n_days],
            "returns": returns[:n_days],
        }

# ============================================================
# 2. 交易策略基线（Agent架构对比）
# ============================================================

@dataclass
class Trade:
    date: str
    direction: str  # 'long' or 'short'
    entry_price: float
    exit_price: float = 0.0
    size: float = 1.0
    pnl: float = 0.0

@dataclass  
class StrategyResult:
    name: str
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)

class BaseStrategy:
    """策略基类"""
    name = "Base"
    
    def generate_signals(self, data: dict) -> np.ndarray:
        """返回信号数组: +1=做多, -1=做空, 0=空仓"""
        raise NotImplementedError

class MomentumStrategy(BaseStrategy):
    """动量策略：N日收益率>0做多，<0做空"""
    name = "Momentum-20D"
    
    def __init__(self, lookback=20, threshold=0.0):
        self.lookback = lookback
        self.threshold = threshold
    
    def generate_signals(self, data):
        prices = data["close"]
        returns = np.zeros(len(prices))
        for i in range(self.lookback, len(prices)):
            ret = (prices[i] - prices[i - self.lookback]) / prices[i - self.lookback]
            if ret > self.threshold:
                returns[i] = 1
            elif ret < -self.threshold:
                returns[i] = -1
        return returns

class MeanReversionStrategy(BaseStrategy):
    """均值回归策略：偏离布林带时反向交易"""
    name = "MeanReversion-BB"
    
    def __init__(self, window=20, num_std=2.0):
        self.window = window
        self.num_std = num_std
    
    def generate_signals(self, data):
        prices = data["close"]
        signals = np.zeros(len(prices))
        for i in range(self.window, len(prices)):
            window = prices[i-self.window:i]
            mean = np.mean(window)
            std = np.std(window)
            upper = mean + self.num_std * std
            lower = mean - self.num_std * std
            if prices[i] > upper:
                signals[i] = -1  # 超买做空
            elif prices[i] < lower:
                signals[i] = 1   # 超卖做多
        return signals

class GTScoreStrategy(BaseStrategy):
    """GT-Score策略：基于GT-Score目标函数的稳健策略
    GT-Score = mean(return) / std(return) * stability_factor
    其中 stability_factor 惩罚收益分布的不稳定性
    """
    name = "GT-Score-Robust"
    
    def __init__(self, short_window=10, long_window=50, stability_weight=0.3):
        self.short_window = short_window
        self.long_window = long_window
        self.stability_weight = stability_weight
    
    def generate_signals(self, data):
        prices = data["close"]
        signals = np.zeros(len(prices))
        
        for i in range(self.long_window, len(prices)):
            # 短期动量
            short_ret = (prices[i] - prices[i - self.short_window]) / prices[i - self.short_window]
            # 长期趋势
            long_ret = (prices[i] - prices[i - self.long_window]) / prices[i - self.long_window]
            
            # GT-Score: 稳定性加权的信号
            recent_returns = np.diff(prices[i-self.long_window:i+1]) / prices[i-self.long_window:i]
            mean_ret = np.mean(recent_returns)
            std_ret = np.std(recent_returns)
            
            # 稳定性因子：收益一致性
            positive_ratio = np.mean(recent_returns > 0)
            stability = min(positive_ratio, 1 - positive_ratio) * 2  # 0-1范围
            
            gt_score = (mean_ret / (std_ret + 1e-8)) * (1 + self.stability_weight * stability)
            
            if gt_score > 0.05:
                signals[i] = 1
            elif gt_score < -0.05:
                signals[i] = -1
        
        return signals

# ============================================================
# 3. GT-Score 计算（防过拟合目标函数）
# ============================================================

def compute_gt_score(returns: np.ndarray, n_folds=5) -> Dict:
    """
    GT-Score: Generalization-Test Score
    核心思想：通过walk-forward验证评估策略的样本外泛化能力
    避免传统Sharpe Ratio的过拟合问题
    """
    n = len(returns)
    fold_size = n // n_folds
    
    in_sample_sharpes = []
    out_sample_sharpes = []
    stability_scores = []
    
    for fold in range(n_folds):
        # 划分训练集和测试集
        test_start = fold * fold_size
        test_end = min(test_start + fold_size, n)
        train_end = test_start
        
        if train_end < fold_size:
            continue
        
        train_start = max(0, train_end - fold_size)
        train_ret = returns[train_start:train_end]
        test_ret = returns[test_start:test_end]
        
        # 样本内Sharpe
        if len(train_ret) > 1 and np.std(train_ret) > 0:
            is_sharpe = np.mean(train_ret) / np.std(train_ret) * np.sqrt(252)
        else:
            is_sharpe = 0
        
        # 样本外Sharpe
        if len(test_ret) > 1 and np.std(test_ret) > 0:
            oos_sharpe = np.mean(test_ret) / np.std(test_ret) * np.sqrt(252)
        else:
            oos_sharpe = 0
        
        in_sample_sharpes.append(is_sharpe)
        out_sample_sharpes.append(oos_sharpe)
        
        # 稳定性：样本内外Sharpe的一致性
        if abs(is_sharpe) > 0.01:
            stability_scores.append(oos_sharpe / (is_sharpe + 1e-8))
    
    # GT-Score计算
    mean_oos = np.mean(out_sample_sharpes) if out_sample_sharpes else 0
    std_oos = np.std(out_sample_sharpes) if out_sample_sharpes else 1
    mean_stability = np.mean(stability_scores) if stability_scores else 0
    
    gt_score = mean_oos / (std_oos + 0.5) * (1 + 0.3 * min(mean_stability, 1))
    
    return {
        "gt_score": round(gt_score, 4),
        "mean_oos_sharpe": round(mean_oos, 4),
        "std_oos_sharpe": round(std_oos, 4),
        "mean_stability": round(mean_stability, 4),
        "in_sample_sharpes": [round(s, 4) for s in in_sample_sharpes],
        "out_sample_sharpes": [round(s, 4) for s in out_sample_sharpes],
        "overfitting_ratio": round(1 - mean_stability, 4) if mean_stability < 1 else 0,
    }

# ============================================================
# 4. 回测引擎
# ============================================================

class BacktestEngine:
    """简洁的回测引擎"""
    
    def __init__(self, initial_capital=1e6, commission=0.001, slippage=0.0005):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
    
    def run(self, strategy: BaseStrategy, data: dict) -> StrategyResult:
        signals = strategy.generate_signals(data)
        prices = data["close"]
        dates = data["dates"]
        
        equity = self.initial_capital
        position = 0
        equity_curve = [equity]
        trades = []
        
        for i in range(1, len(prices)):
            # 平仓
            if position != 0 and signals[i] != position:
                exit_price = prices[i] * (1 - self.slippage * np.sign(position))
                pnl = position * (exit_price - entry_price) * 100  # 每手100股
                pnl -= abs(exit_price * 100 * self.commission)  # 佣金
                equity += pnl
                trades.append(Trade(
                    date=dates[i], direction="long" if position > 0 else "short",
                    entry_price=entry_price, exit_price=exit_price, pnl=pnl
                ))
                position = 0
            
            # 开仓
            if signals[i] != 0 and position == 0:
                entry_price = prices[i] * (1 + self.slippage * np.sign(signals[i]))
                position = signals[i]
            
            # 按持仓计算浮动盈亏
            if position != 0:
                daily_ret = (prices[i] - prices[i-1]) / prices[i-1]
                equity += equity * daily_ret * position
            
            equity_curve.append(equity)
        
        # 计算绩效指标
        eq = np.array(equity_curve)
        daily_returns = np.diff(eq) / eq[:-1]
        
        result = StrategyResult(
            name=strategy.name,
            trades=trades,
            equity_curve=equity_curve,
        )
        
        total_return = (equity - self.initial_capital) / self.initial_capital
        n_years = len(prices) / 252
        
        result.metrics = {
            "total_return": round(total_return * 100, 2),
            "annual_return": round(((1 + total_return) ** (1/n_years) - 1) * 100, 2) if n_years > 0 else 0,
            "max_drawdown": round(self._max_drawdown(eq) * 100, 2),
            "sharpe_ratio": round(np.mean(daily_returns) / (np.std(daily_returns) + 1e-8) * np.sqrt(252), 4),
            "sortino_ratio": round(np.mean(daily_returns) / (np.std(daily_returns[daily_returns<0]) + 1e-8) * np.sqrt(252), 4),
            "win_rate": round(sum(1 for t in trades if t.pnl > 0) / max(len(trades), 1) * 100, 1),
            "n_trades": len(trades),
            "avg_trade_pnl": round(sum(t.pnl for t in trades) / max(len(trades), 1), 2),
            "profit_factor": round(
                sum(t.pnl for t in trades if t.pnl > 0) / max(abs(sum(t.pnl for t in trades if t.pnl < 0)), 1), 2
            ),
        }
        
        # GT-Score
        gt = compute_gt_score(daily_returns)
        result.metrics.update(gt)
        
        return result
    
    def _max_drawdown(self, equity):
        peak = np.maximum.accumulate(equity)
        drawdown = (peak - equity) / peak
        return np.max(drawdown)

# ============================================================
# 5. 主程序
# ============================================================

def main():
    print("=" * 70)
    print("PredictionMarketBench + GT-Score 量化回测框架")
    print("基于 arXiv:2602.00133 & arXiv:2602.00080")
    print("=" * 70)
    
    # 生成模拟市场数据
    sim = MarketSimulator(seed=42)
    data = sim.generate_ohlcv(n_days=500)
    print(f"\n市场数据: {data['dates'][0]} ~ {data['dates'][-1]}, {len(data['dates'])} 个交易日")
    print(f"价格范围: {data['close'].min():.2f} ~ {data['close'].max():.2f}")
    
    # 初始化回测引擎
    engine = BacktestEngine(initial_capital=1e6, commission=0.001, slippage=0.0005)
    
    # 策略对比
    strategies = [
        MomentumStrategy(lookback=20),
        MeanReversionStrategy(window=20, num_std=2.0),
        GTScoreStrategy(short_window=10, long_window=50),
    ]
    
    results = []
    print("\n" + "=" * 70)
    print("策略回测结果对比")
    print("=" * 70)
    
    for strategy in strategies:
        result = engine.run(strategy, data)
        results.append(result)
        
        print(f"\n--- {result.name} ---")
        for k, v in result.metrics.items():
            print(f"  {k:25s}: {v}")
    
    # 总结
    print("\n" + "=" * 70)
    print("GT-Score 排名（防过拟合排序）")
    print("=" * 70)
    
    ranked = sorted(results, key=lambda r: r.metrics.get("gt_score", 0), reverse=True)
    for i, r in enumerate(ranked):
        gt = r.metrics.get("gt_score", 0)
        oos = r.metrics.get("mean_oos_sharpe", 0)
        oof = r.metrics.get("overfitting_ratio", 0)
        print(f"  #{i+1} {r.name:25s}  GT={gt:+.4f}  OOS_Sharpe={oos:+.4f}  过拟合比={oof:.2%}")
    
    # 保存JSON报告
    report = {
        "benchmark": "PredictionMarketBench",
        "date": datetime.now().isoformat(),
        "market_data": {
            "period": f"{data['dates'][0]} ~ {data['dates'][-1]}",
            "n_days": len(data["dates"]),
        },
        "strategies": []
    }
    for r in results:
        report["strategies"].append({
            "name": r.name,
            "metrics": r.metrics,
            "n_trades": len(r.trades),
        })
    
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_path}")
    
    # 生成ASCII权益曲线图
    print("\n" + "=" * 70)
    print("权益曲线（归一化）")
    print("=" * 70)
    for r in results:
        eq = np.array(r.equity_curve)
        norm = eq / eq[0]
        _print_ascii_chart(norm[-50:], title=r.name, width=60)
    
    print("\n回测完成！")

def _print_ascii_chart(values, title="", width=60, height=15):
    """简单的ASCII折线图"""
    n = min(len(values), width)
    vals = values[-n:]
    vmin, vmax = vals.min(), vals.max()
    vrange = vmax - vmin if vmax != vmin else 1
    
    chart = [[" "] * n for _ in range(height)]
    
    for x, v in enumerate(vals):
        y = int((v - vmin) / vrange * (height - 1))
        y = min(y, height - 1)
        chart[height - 1 - y][x] = "*"
    
    print(f"\n  {title}")
    print(f"  {vmax:.3f} |" + "".join(chart[0]))
    mid = (vmax + vmin) / 2
    print(f"  {mid:.3f} |" + "".join(chart[height//2]))
    print(f"  {vmin:.3f} |" + "".join(chart[-1]))
    print(f"  {'':>8s} {'─' * n}")
    print(f"  {'':>8s} {'Start':<{n//2}}{'End':>{n//2}}")

if __name__ == "__main__":
    main()
