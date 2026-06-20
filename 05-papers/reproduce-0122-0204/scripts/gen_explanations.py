"""Generate explanations incrementally, saving after each paper"""
import requests, json, os, time, sys

API_KEY = "sk-vpBVC7bc3t9dDAVMPprGsxW4fEgQtuzn2lkMgrGW7SpQGRel"
BASE = "https://lanyiapi.com/v1"
OUT_FILE = "E:/my-dev-favorites/05-papers/reproduce-0122-0204/explanations.json"

# Load existing explanations
if os.path.exists(OUT_FILE):
    with open(OUT_FILE, "r", encoding="utf-8") as f:
        explanations = json.load(f)
else:
    explanations = {}

PAPERS = [
    ("dist_role_debate", "2601.17152", "Dynamic Role Assignment for Multi-Agent Debate",
     "Meta-Debate framework: evaluates participants via pitches and peer evaluations to assign optimal agent roles before the main debate. Two-phase approach significantly outperforms random or uniform assignment.",
     "Meta-debate pre-evaluation, Customized pitch generation, Peer scoring, Dynamic role optimization"),
    ("mattrl", "2601.09667", "MATTRL: Collaborative Multi-Agent Test-Time RL for Reasoning",
     "Test-time RL system assembling specialized agents for multi-round debates with structured textual memories. Bypasses costly pre-training. Improved correctness on medical, math, education benchmarks.",
     "Test-time agent assembly, Structured textual memory, Multi-round debate protocol, RL-guided agent selection"),
    ("pred_market_bench", "2602.00133", "PredictionMarketBench: SWE-bench for Trading Agents",
     "Standardized benchmark inspired by SWE-bench for evaluating AI trading agents on prediction markets. Enables reproducible backtesting and comparison of agent architectures.",
     "SWE-bench style evaluation, Prediction market backtesting, Agent architecture comparison, Standardized financial tasks"),
    ("int_credit_assign", "2601.14209", "InT: Self-Proposed Interventions for Credit Assignment in LLM Reasoning",
     "Models evaluate their own logic and suggest targeted fixes for credit assignment. ~14% accuracy improvement on math benchmarks.",
     "Self-evaluation of reasoning steps, Intervention proposals, Credit assignment without external reward, 14 percent math accuracy boost"),
    ("pragpo", "2602.03190", "PrAg-PO: Prompt Augmentation Scales up GRPO Training",
     "Prompt template augmentation with template-specific format rewards to improve diversity and prevent early training collapse during GRPO RL fine-tuning for math reasoning.",
     "Prompt template augmentation, Template-specific format rewards, Prevents training collapse, GRPO diversity enhancement"),
    ("equiform", "2601.17486", "EquiForm: Noise-Robust SE(3)-Equivariant Policy Learning from 3D Point Clouds",
     "Geometric denoising module and contrastive equivariant alignment objective. 17.2 percent improvement in simulation, 28.1 percent in real-world robotic manipulation under noise and occlusion.",
     "SE(3) equivariant architecture, Geometric denoising module, Contrastive equivariant alignment, Robust to sensor noise"),
    ("zest", "2602.00401", "ZEST: Zero-shot Embodied Skill Transfer for Athletic Robot Control",
     "Zero-shot transfer of athletic skills to physical robots without real-world fine-tuning. Bridges sim-to-real gap for highly dynamic maneuvers.",
     "Zero-shot sim-to-real transfer, Athletic skill encoding, Domain randomization, No real-world fine-tuning"),
    ("reasoning_guessing", "2601.10679", "Are Your Reasoning Models Reasoning or Guessing? Mechanistic Analysis",
     "Hierarchical reasoning models often guess rather than genuinely reason. Three failure modes: broken foundational assumptions, sudden accuracy jumps, entrapment in incorrect states.",
     "Three failure modes, Guessing vs reasoning distinction, Dataset expansion fix, Training randomization remedy"),
    ("scaling_embed", "2601.21204", "Scaling Embeddings Outperforms Scaling Experts in Language Models",
     "Expanding embedding dimensions outperforms increasing expert counts in MoE. LongCat-Flash-Lite 68.5B total params with 3B active, over 30B in embeddings.",
     "Embedding over Expert scaling, MoE compute budget allocation, 68.5B total 3B active, 30B parameter embeddings"),
    ("gt_score", "2602.00080", "GT-Score: Robust Objective Function for Reducing Overfitting in Trading Strategies",
     "Novel objective metric preventing algorithmic trading strategies from overfitting to noise. More robust than standard return-based optimization.",
     "Anti-overfitting objective, Robust to market noise, Alternative to Sharpe optimization, Walk-forward validation"),
    ("llm_sentiment", "2602.00086", "Impact of LLM News Sentiment Analysis on Stock Price Movement Prediction",
     "Quantifies how LLM-based news sentiment improves stock price prediction. Measures incremental alpha from advanced text parsers vs traditional NLP.",
     "LLM sentiment as alpha signal, Incremental prediction power, LLM vs traditional NLP, News-driven trading signals"),
    ("quant_eval", "2601.08689", "QuantEval: Benchmark for Financial Quantitative Tasks in LLMs",
     "Benchmark evaluating AI on factual knowledge, numerical reasoning, and trading code generation. Built-in backtesting environment.",
     "Three-dimensional evaluation, Backtesting-as-evaluation, Code generation for trading, AI vs human quant comparison"),
]

def call_gpt(prompt):
    resp = requests.post(f"{BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-5.5", "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 2500, "temperature": 0.7},
        timeout=300)
    data = resp.json()
    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"]
    print(f"  Error: {str(data)[:200]}")
    return None

for i, (pid, arxiv, title, summary, ideas) in enumerate(PAPERS):
    if pid in explanations:
        print(f"[{i+1}/12] SKIP {pid} (already done)")
        continue
    
    print(f"[{i+1}/12] Generating: {title[:50]}...")
    sys.stdout.flush()
    
    prompt = f"""你是一位资深AI研究员，请用中文对以下论文进行深度解读。

论文标题: {title}
arXiv: {arxiv}
摘要: {summary}
关键创新点: {ideas}

请按以下结构组织（每个部分3-5句话）：
1. 一句话总结
2. 核心动机
3. 方法详解（用类比和直觉）
4. 关键创新点解析
5. 实验亮点
6. 局限与展望
7. 对开发者的启发

用markdown格式。"""
    
    exp = call_gpt(prompt)
    if exp:
        explanations[pid] = exp
        print(f"  OK ({len(exp)} chars)")
        # Save incrementally
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(explanations, f, ensure_ascii=False, indent=2)
    else:
        print(f"  FAILED")
    sys.stdout.flush()
    time.sleep(2)

print(f"\nDone! {len(explanations)}/12 explanations saved.")
