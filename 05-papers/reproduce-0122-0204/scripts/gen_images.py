"""Phase 2: Generate GPT-Image-2 blueprint diagrams for 12 papers"""
import requests, json, base64, os, time, sys

API_KEY = "sk-vpBVC7bc3t9dDAVMPprGsxW4fEgQtuzn2lkMgrGW7SpQGRel"
BASE = "https://lanyiapi.com/v1"
IMG_DIR = "E:/my-dev-favorites/05-papers/reproduce-0122-0204/images"
os.makedirs(IMG_DIR, exist_ok=True)

PAPERS = [
    ("dist_role_debate", "Dynamic Role Assignment for Multi-Agent Debate",
     ["Meta-debate pre-evaluation", "Pitch generation", "Peer scoring", "Role assignment", "Debate execution", "Result aggregation"]),
    ("mattrl", "MATTRL: Multi-Agent Test-Time RL",
     ["Agent pool", "RL selector", "Debate protocol", "Textual memory", "Consensus mechanism", "Answer output"]),
    ("pred_market_bench", "PredictionMarketBench",
     ["Market data", "Task definition", "Agent interface", "Execution engine", "Backtest evaluator", "Metrics dashboard"]),
    ("int_credit_assign", "InT: Self-Proposed Interventions",
     ["Reasoning chain", "Self-evaluator", "Intervention proposer", "Credit assigner", "Policy update", "Output correction"]),
    ("pragpo", "PrAg-PO: Prompt Augmented GRPO",
     ["Prompt templates", "Template augmenter", "GRPO trainer", "Format reward", "Policy model", "Math solver"]),
    ("equiform", "EquiForm: SE(3)-Equivariant Policy",
     ["3D point cloud", "Geometric denoiser", "SE(3) encoder", "Contrastive alignment", "Policy network", "Robot actions"]),
    ("zest", "ZEST: Zero-shot Skill Transfer",
     ["Sim environment", "Skill encoder", "Domain randomizer", "Transfer module", "Real robot", "Dynamic execution"]),
    ("reasoning_guessing", "Reasoning or Guessing Analysis",
     ["Reasoning model", "Probe layer 1", "Probe layer 2", "Failure detector", "Guessing classifier", "Fix module"]),
    ("scaling_embed", "Scaling Embeddings vs Experts",
     ["MoE router", "Expert pool", "Embedding layer 30B", "Attention blocks", "Output head", "Benchmark eval"]),
    ("gt_score", "GT-Score Anti-Overfitting",
     ["Strategy returns", "Walk-forward split", "In-sample eval", "Out-sample eval", "Stability scorer", "GT-Score output"]),
    ("llm_sentiment", "LLM Sentiment for Stocks",
     ["News feed", "LLM analyzer", "Multi-dim scoring", "Signal aggregator", "Trading engine", "P&L tracker"]),
    ("quant_eval", "QuantEval Benchmark",
     ["Knowledge QA", "Numerical reasoning", "Code generation", "Backtest executor", "Scoring engine", "Human comparison"]),
]

def generate_image(prompt, filename):
    filepath = os.path.join(IMG_DIR, filename)
    if os.path.exists(filepath):
        print(f"  SKIP {filename} (exists)")
        return True
    
    resp = requests.post(f"{BASE}/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-image-2", "prompt": prompt, "n": 1,
              "size": "1536x1024", "response_format": "b64_json"},
        timeout=300)
    data = resp.json()
    if "data" in data and data["data"]:
        img_bytes = base64.b64decode(data["data"][0]["b64_json"])
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        print(f"  Saved: {filename} ({len(img_bytes)//1024}KB)")
        return True
    print(f"  Error: {str(data)[:200]}")
    return False

success = 0
for i, (pid, title, components) in enumerate(PAPERS):
    fname = f"{pid}.png"
    print(f"[{i+1}/12] Blueprint: {fname}")
    sys.stdout.flush()
    
    comp_list = ", ".join(components)
    prompt = f"""Engineering blueprint technical architecture diagram.

Title: {title}
Components to show: {comp_list}

Style requirements:
- Dark navy background (hex #0a1628)
- Cyan/teal line art (hex #00d4ff) for connections and borders
- White text labels for component names
- Engineering schematic aesthetic with grid lines
- Rectangular modules with rounded corners
- Data flow arrows (cyan) between components
- Performance metrics as annotations
- ALL TEXT IN ENGLISH only, no Chinese characters
- Clean vector-like precision, professional engineering blueprint style
- 1536x1024 resolution"""
    
    if generate_image(prompt, fname):
        success += 1
    time.sleep(3)
    sys.stdout.flush()

print(f"\nDone! {success}/12 blueprints generated.")
