"""
MoE效率对比分析
基于 arXiv:2602.10604 (Step 3.5 Flash) 和 arXiv:2601.21204 (Scaling Embeddings)

核心思想:
1. MoE架构中交错注意力 vs 全注意力的效率-效果权衡
2. 激活参数比例对推理延迟和吞吐的影响
3. 嵌入扩展 vs 专家扩展的计算效率对比
4. 多Token预测的吞吐提升量化

运行: python moe_efficiency.py
"""
import numpy as np
import json
import os
from dataclasses import dataclass
from typing import List, Dict

# ============================================================
# 1. MoE模型模拟器
# ============================================================

@dataclass
class MoEConfig:
    name: str
    total_params_b: float      # 总参数(十亿)
    active_params_b: float     # 激活参数(十亿)
    n_experts: int
    n_active_experts: int
    embedding_dim: int
    attention_type: str        # 'full', 'sliding', 'interleaved'
    multi_token_pred: int      # 多Token预测数
    sliding_ratio: float       # 滑窗注意力占比

class MoESimulator:
    """模拟MoE模型的推理性能"""
    
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
        # 基准: 全注意力Dense模型，每B参数约 2ms/token (A100)
        self.base_latency_per_b = 2.0  # ms per billion active params per token
        self.base_throughput = 500     # tokens/s per billion active params (A100)
    
    def compute_latency(self, config: MoEConfig, seq_len: int = 2048) -> Dict:
        """计算推理延迟"""
        # 基础延迟(仅与激活参数相关)
        base_lat = config.active_params_b * self.base_latency_per_b
        
        # 注意力延迟
        if config.attention_type == "full":
            attn_factor = 1.0
        elif config.attention_type == "sliding":
            attn_factor = 0.4  # 滑窗注意力约快60%
        elif config.attention_type == "interleaved":
            # 交错: sliding_ratio的层用滑窗(快), 其余用全注意力(慢)
            attn_factor = config.sliding_ratio * 0.4 + (1 - config.sliding_ratio) * 1.0
        else:
            attn_factor = 1.0
        
        # 序列长度影响 (全注意力O(n²), 滑窗O(n*w))
        if config.attention_type == "full":
            seq_factor = (seq_len / 2048) ** 1.8  # 近似二次
        else:
            seq_factor = (seq_len / 2048) ** 1.1  # 近似线性
        
        total_latency = base_lat * attn_factor * seq_factor
        
        # 多Token预测提升
        if config.multi_token_pred > 1:
            # 多Token预测减少step数但增加每step计算
            step_reduction = 1.0 / config.multi_token_pred
            compute_overhead = 1.0 + 0.1 * (config.multi_token_pred - 1)
            effective_latency = total_latency * step_reduction * compute_overhead
        else:
            effective_latency = total_latency
        
        return {
            "name": config.name,
            "latency_ms_per_token": round(effective_latency, 2),
            "time_to_first_token_ms": round(effective_latency * 1.5, 2),  # prefill overhead
            "tokens_per_second": round(1000 / max(effective_latency, 0.01), 1),
            "seq_len": seq_len,
        }
    
    def compute_throughput(self, config: MoEConfig, batch_size: int = 32) -> Dict:
        """计算吞吐"""
        base_tp = self.base_throughput / config.active_params_b
        # 批处理增益（亚线性）
        batch_gain = batch_size ** 0.7
        effective_tp = base_tp * batch_gain
        
        # 多Token预测
        if config.multi_token_pred > 1:
            effective_tp *= config.multi_token_pred * 0.85  # 85%效率
        
        # 注意力效率
        if config.attention_type == "interleaved":
            effective_tp *= 1.0 + config.sliding_ratio * 0.5
        
        memory_per_request = config.active_params_b * 2  # GB (FP16)
        max_batch = int(80 / max(memory_per_request, 1))  # A100 80GB
        
        return {
            "name": config.name,
            "tokens_per_second_batch": round(effective_tp * batch_size, 0),
            "effective_batch_size": batch_size,
            "max_batch_a100": max_batch,
            "memory_per_request_gb": round(memory_per_request, 1),
        }
    
    def estimate_capability(self, config: MoEConfig) -> Dict:
        """估算模型能力（基于scaling laws简化版）"""
        # 基础能力与总参数对数关系
        base_score = 50 + 15 * np.log10(config.total_params_b + 1)
        
        # MoE路由效率
        expert_efficiency = min(config.n_active_experts / max(config.n_experts * 0.1, 1), 1.0)
        
        # 嵌入维度影响
        embed_bonus = np.log10(config.embedding_dim / 1024 + 1) * 5
        
        # 注意力质量
        if config.attention_type == "interleaved":
            attn_quality = 0.95 + config.sliding_ratio * 0.03
        elif config.attention_type == "sliding":
            attn_quality = 0.88
        else:
            attn_quality = 1.0
        
        capability = base_score * expert_efficiency * attn_quality + embed_bonus
        
        return {
            "name": config.name,
            "estimated_benchmark_score": round(capability, 1),
            "components": {
                "base": round(base_score, 1),
                "expert_efficiency": round(expert_efficiency, 3),
                "embed_bonus": round(embed_bonus, 1),
                "attn_quality": round(attn_quality, 3),
            }
        }

# ============================================================
# 2. 模型配置（真实+虚构对比）
# ============================================================

CONFIGS = [
    # Step 3.5 Flash 风格
    MoEConfig("Step3.5-Flash(11B-active)", 196, 11, 64, 4, 8192, 
              "interleaved", 2, 0.75),
    # 同参数但全注意力
    MoEConfig("Step3.5-FullAttn", 196, 11, 64, 4, 8192, 
              "full", 1, 0.0),
    # 同参数但无多Token预测
    MoEConfig("Step3.5-NoMTP", 196, 11, 64, 4, 8192, 
              "interleaved", 1, 0.75),
    # Dense对照 (同激活参数)
    MoEConfig("Dense-11B", 11, 11, 1, 1, 4096, 
              "full", 1, 0.0),
    # Dense大模型 (同总参数)
    MoEConfig("Dense-196B", 196, 196, 1, 1, 8192, 
              "full", 1, 0.0),
    # 嵌入扩展版 (2601.21204的发现)
    MoEConfig("Embed-Scaled(30B-embed)", 196, 11, 32, 4, 16384, 
              "interleaved", 2, 0.75),
    # 专家扩展版 (传统MoE)
    MoEConfig("Expert-Scaled(128experts)", 196, 11, 128, 4, 4096, 
              "interleaved", 2, 0.75),
    # Nanbeige4.1 风格 (小模型)
    MoEConfig("Nanbeige-3B", 3, 3, 1, 1, 4096, 
              "full", 1, 0.0),
]

# ============================================================
# 3. 对比分析
# ============================================================

def run_comparison(sim: MoESimulator):
    """运行完整对比分析"""
    
    print("=" * 70)
    print("MoE效率对比分析")
    print("基于 arXiv:2602.10604 (Step 3.5 Flash)")
    print("=" * 70)
    
    # 延迟对比
    print("\n[1] 推理延迟对比 (seq_len=2048)")
    print("-" * 70)
    print(f"  {'模型':30s} {'ms/token':>10s} {'TTFT(ms)':>10s} {'tok/s':>8s}")
    print(f"  {'─'*60}")
    
    latency_results = []
    for config in CONFIGS:
        lat = sim.compute_latency(config, seq_len=2048)
        latency_results.append(lat)
        print(f"  {lat['name']:30s} {lat['latency_ms_per_token']:>10.2f} "
              f"{lat['time_to_first_token_ms']:>10.1f} {lat['tokens_per_second']:>8.1f}")
    
    # 吞吐对比
    print(f"\n[2] 吞吐量对比 (batch_size=32, A100)")
    print("-" * 70)
    print(f"  {'模型':30s} {'tok/s(batch)':>12s} {'显存(GB)':>10s} {'最大batch':>10s}")
    print(f"  {'─'*65}")
    
    throughput_results = []
    for config in CONFIGS:
        tp = sim.compute_throughput(config, batch_size=32)
        throughput_results.append(tp)
        print(f"  {tp['name']:30s} {tp['tokens_per_second_batch']:>12.0f} "
              f"{tp['memory_per_request_gb']:>10.1f} {tp['max_batch_a100']:>10d}")
    
    # 能力估算
    print(f"\n[3] 能力估算 (简化Scaling Law)")
    print("-" * 70)
    print(f"  {'模型':30s} {'预估分数':>10s} {'基础':>6s} {'专家效率':>8s} {'嵌入加成':>8s}")
    print(f"  {'─'*65}")
    
    capability_results = []
    for config in CONFIGS:
        cap = sim.estimate_capability(config)
        capability_results.append(cap)
        c = cap["components"]
        print(f"  {cap['name']:30s} {cap['estimated_benchmark_score']:>10.1f} "
              f"{c['base']:>6.1f} {c['expert_efficiency']:>8.3f} {c['embed_bonus']:>8.1f}")
    
    # 效率-能力帕累托分析
    print(f"\n[4] 效率-能力帕累托前沿")
    print("-" * 70)
    
    combined = []
    for lat, tp, cap in zip(latency_results, throughput_results, capability_results):
        efficiency_score = cap["estimated_benchmark_score"] / max(lat["latency_ms_per_token"], 0.01)
        combined.append({
            "name": lat["name"],
            "score": cap["estimated_benchmark_score"],
            "latency": lat["latency_ms_per_token"],
            "throughput": tp["tokens_per_second_batch"],
            "efficiency": round(efficiency_score, 2),
        })
    
    combined.sort(key=lambda x: x["efficiency"], reverse=True)
    print(f"  {'排名':>4s} {'模型':30s} {'能力':>6s} {'延迟':>8s} {'效率分':>8s}")
    print(f"  {'─'*60}")
    for i, c in enumerate(combined):
        marker = " ★" if i == 0 else ""
        print(f"  {i+1:>4d} {c['name']:30s} {c['score']:>6.1f} "
              f"{c['latency']:>7.2f}ms {c['efficiency']:>8.2f}{marker}")
    
    # 关键发现
    print(f"\n[5] 关键发现")
    print("-" * 70)
    
    flash = next(c for c in combined if "Flash" in c["name"])
    full = next(c for c in combined if "FullAttn" in c["name"])
    dense196 = next(c for c in combined if "Dense-196B" in c["name"])
    embed = next(c for c in combined if "Embed" in c["name"])
    expert = next(c for c in combined if "Expert" in c["name"])
    
    speedup = full["latency"] / flash["latency"]
    print(f"  1. 交错注意力 vs 全注意力: 速度提升 {speedup:.1f}x, "
          f"能力差距 {abs(flash['score'] - full['score']):.1f}分")
    
    vs_dense = flash["throughput"] / dense196["throughput"]
    print(f"  2. MoE(11B激活) vs Dense(196B): 吞吐 {vs_dense:.1f}x, "
          f"能力差距 {abs(flash['score'] - dense196['score']):.1f}分")
    
    embed_vs_expert = embed["score"] - expert["score"]
    print(f"  3. 嵌入扩展 vs 专家扩展: 能力差距 {embed_vs_expert:+.1f}分 "
          f"(嵌入{'更优' if embed_vs_expert > 0 else '更差'})")
    
    # 保存报告
    report = {
        "paper": "arXiv:2602.10604 & arXiv:2601.21204",
        "configs": [{"name": c.name, "total_b": c.total_params_b, 
                     "active_b": c.active_params_b, "attn": c.attention_type}
                    for c in CONFIGS],
        "latency": latency_results,
        "throughput": throughput_results,
        "capability": capability_results,
        "efficiency_ranking": combined,
    }
    
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "moe_efficiency_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_path}")

# ============================================================
# 4. 主程序
# ============================================================

def main():
    sim = MoESimulator(seed=42)
    run_comparison(sim)
    print("\n分析完成！")

if __name__ == "__main__":
    main()
