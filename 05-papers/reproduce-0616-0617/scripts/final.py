"""Final assembly: generate missing image + all explanations + MD + HTML + copy to repo"""
import json, base64, os, time, requests, re, shutil

API_KEY = "sk-vpBVC7bc3t9dDAVMPprGsxW4fEgQtuzn2lkMgrGW7SpQGRel"
API_BASE = "https://lanyiapi.com/v1"
BASE = r"C:\Users\Lenovo\.qoderwork\workspace\mqi7df873xfl6gf5\outputs\paper-reproduce"
IMG_DIR = os.path.join(BASE, "images")
REPO = r"E:\my-dev-favorites\05-papers\reproduce-0616-0617"

PAPERS = [
    {"id":"seagym","cat_zh":"Agent与多智能体","title":"SEAGym: Self-Evolving LLM Agent Evaluation","authors":"Congjie Zheng et al.","abstract":"SEAGym measures agent self-evolution across training, validation, replay, and cost records.","abstract_zh":"首个评估Agent自我进化能力的标准化环境，追踪训练/验证/回放/成本全链路。"},
    {"id":"ceo_bench","cat_zh":"Agent与多智能体","title":"Can LLMs Be CEOs? CEO-Bench","authors":"Yuyang Dai et al.","abstract":"CEO-Bench evaluates strategic resource allocation with conflicting advisor inputs. Finds single-advisor capture.","abstract_zh":"测试LLM能否做CEO级战略决策，发现'单一顾问俘获'失败模式。"},
    {"id":"dist_agent_net","cat_zh":"Agent与多智能体","title":"Distributed General-Purpose Agent Networks","authors":"Shengli Zhang et al.","abstract":"P2P agent network with semantic communication and trust mechanisms for open task execution.","abstract_zh":"P2P Agent网络架构，语义通信+信任机制实现设备间开放任务协作。"},
    {"id":"e3rl","cat_zh":"推理与强化学习","title":"E3RL: Shattering the Autoregressive Curse","authors":"Ziliang Wang et al.","abstract":"Cross-entropy grounded uncertainty to excise autoregressive reasoning defects while preserving KV cache.","abstract_zh":"用交叉熵锚定不确定性，切除自回归推理级联错误，保持KV缓存效率。"},
    {"id":"flowrag","cat_zh":"推理与强化学习","title":"FlowRAG: Frequency-Aware Graph Flow for RAG","authors":"Bihao Zhan et al.","abstract":"Quad-level heterogeneous graphs with frequency-aware flow to prune noisy RAG connections.","abstract_zh":"四层异构图+频率感知流，增强GraphRAG噪声修剪能力。"},
    {"id":"small_init","cat_zh":"推理与强化学习","title":"Small Initialization Matters for LLMs","authors":"Liangkai Hang et al.","abstract":"Small init drives low-complexity structures, improving reasoning. Challenges bigger-is-better.","abstract_zh":"反直觉发现：小初始化驱动低复杂度结构，反而提升推理能力。"},
    {"id":"deepinsight","cat_zh":"具身智能与物理AI","title":"DeepInsight: Physical AI Evaluation Stack","authors":"Siyi Li et al.","abstract":"Unified eval infrastructure from decoding to control with cross-layer diagnostic traceability.","abstract_zh":"首个Physical AI全栈评测基础设施，从解码到控制的跨层诊断可追溯。"},
    {"id":"preact","cat_zh":"具身智能与物理AI","title":"PreAct: Faster Agents on Repeated Tasks","authors":"Bojie Li","abstract":"Compiles successful runs into state-machine programs. Replay checks screen states before acting.","abstract_zh":"将成功运行编译为状态机程序，重复任务时先检查屏幕状态再行动，显著加速。"},
    {"id":"inference_compute","cat_zh":"LLM理论与分析","title":"How Inference Compute Shapes LLM Evaluation","authors":"Jessica McFadyen et al.","abstract":"Benchmarks must report capability as function of test-time compute resources.","abstract_zh":"挑战标准评测范式：模型能力应报告为测试时计算资源的函数。"},
    {"id":"code_reasoning","cat_zh":"LLM理论与分析","title":"From Brewing to Resolution: Code Reasoning Lifecycle","authors":"Siyue Chen et al.","abstract":"Studies answer brewing and resolution phases. Reveals capability variations across architectures.","abstract_zh":"揭示LLM代码推理的'酝酿'和'确定'两阶段生命周期。"},
]

def call_gpt55(prompt, max_tokens=2000):
    r = requests.post(f"{API_BASE}/chat/completions", headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
        json={"model":"gpt-5.5-openai-compact","messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens,"temperature":0.7}, timeout=120)
    return r.json()["choices"][0]["message"]["content"]

def call_image2(prompt):
    r = requests.post(f"{API_BASE}/images/generations", headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
        json={"model":"gpt-image-2","prompt":prompt,"size":"1792x1024","n":1,"response_format":"b64_json"}, timeout=180)
    d = r.json()
    if "data" in d and d["data"]:
        return base64.b64decode(d["data"][0]["b64_json"])
    return None

# ── Step 1: Generate missing image ──
missing_img = os.path.join(IMG_DIR, "code_reasoning_blueprint.png")
if not os.path.exists(missing_img):
    print("[IMG] Generating code_reasoning blueprint...")
    img_bytes = call_image2("""Technical engineering blueprint diagram for: "From Brewing to Resolution: Code Reasoning Lifecycle in LLMs"
Show two-phase pipeline: PHASE 1 "Answer Brewing" (model internally exploring code paths, shown as branching tree with dotted lines) -> PHASE 2 "Resolution" (final code answer, shown as converging solid lines). Include Transformer layer visualization. 
STYLE: Dark navy (#0a1628) background, white/cyan lines (#00d4ff), thin precise lines, dotted grid overlay, ALL text ENGLISH only. Engineering blueprint aesthetic.""")
    if img_bytes:
        with open(missing_img, "wb") as f: f.write(img_bytes)
        print(f"  -> Saved ({len(img_bytes)//1024}KB)")
else:
    print("[IMG] code_reasoning already exists")

# ── Step 2: Generate all explanations ──
print("\n=== Generating GPT-5.5 explanations ===")
explanations = {}
for p in PAPERS:
    pid = p["id"]
    print(f"  [{pid}]...", end=" ", flush=True)
    try:
        prompt = f"""你是AI研究专家，用中文(简体)为论文写深度解读(约400字)。

论文: {p['title']}
摘要: {p['abstract']}
中文概要: {p['abstract_zh']}

格式(严格按此输出):
**核心问题**: (1-2句)
**方法概述**: (3-5句)
**架构解析**:
- 要点1
- 要点2
- 要点3
**实验亮点**: (2-3个)
**对从业者的启示**: (2-3点)
**局限性**: (1-2点)"""
        explanations[pid] = call_gpt55(prompt)
        print(f"OK ({len(explanations[pid])}c)")
    except Exception as e:
        explanations[pid] = f"(生成失败: {e})"
        print(f"FAIL: {e}")
    time.sleep(0.5)

# ── Step 3: Prepare repo directory ──
print("\n=== Preparing repo directory ===")
os.makedirs(REPO, exist_ok=True)
img_repo = os.path.join(REPO, "images")
os.makedirs(img_repo, exist_ok=True)

# Copy all images to repo
for f in os.listdir(IMG_DIR):
    if f.endswith(".png"):
        shutil.copy2(os.path.join(IMG_DIR, f), os.path.join(img_repo, f))
        print(f"  -> images/{f}")

# ── Step 4: Generate category markdown files ──
print("\n=== Generating Markdown ===")
cats = {}
for p in PAPERS:
    cats.setdefault(p["cat_zh"], []).append(p)

md_all = []  # collect for single combined file too

for cat_name, papers_in_cat in cats.items():
    md = [f"# {cat_name} — arXiv论文复现 (2026-06-16 & 06-17)\n"]
    md.append(f"> GPT-5.5 深度解读 + GPT-Image-2 工程蓝图配图\n\n")
    for p in papers_in_cat:
        pid = p["id"]
        img_file = f"{pid}_blueprint.png"
        img_path_repo = os.path.join(img_repo, img_file)
        md.append(f"---\n")
        md.append(f"## {p['title']}\n\n")
        md.append(f"**Authors**: {p['authors']}  \n")
        md.append(f"**Abstract**: {p['abstract']}\n\n")
        if os.path.exists(img_path_repo):
            md.append(f"![Blueprint](images/{img_file})\n\n")
        md.append(f"### GPT-5.5 深度解读\n\n")
        md.append(f"{explanations.get(pid, '(N/A)')}\n\n")
        md_all.append({"cat": cat_name, "paper": p, "img_file": img_file, "expl": explanations.get(pid, '(N/A)')})
    md_path = os.path.join(REPO, f"{cat_name}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"  -> {cat_name}.md")

# ── Step 5: Generate card HTML ──
print("\n=== Generating Card HTML ===")
cat_colors = {"Agent与多智能体":("#00d4ff","#0a2540"),"推理与强化学习":("#00ff88","#0a2820"),"具身智能与物理AI":("#ff6b35","#2a1a0a"),"LLM理论与分析":("#a855f7","#1a0a2e")}

cards = []
for i, m in enumerate(md_all):
    p = m["paper"]
    img_tag = ""
    img_path = os.path.join(img_repo, m["img_file"])
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            img_tag = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" alt="blueprint">'
    accent, bg = cat_colors.get(m["cat"], ("#00d4ff", "#0a1628"))
    expl = m["expl"]
    expl = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', expl)
    expl = re.sub(r'^### (.+)$', r'<h3>\1</h3>', expl, flags=re.MULTILINE)
    expl = re.sub(r'^- (.+)$', r'<li>\1</li>', expl, flags=re.MULTILINE)
    expl = expl.replace("\n\n", "<br><br>").replace("\n", "<br>")
    cards.append(f"""<div class="card" style="--accent:{accent};--bg:{bg};" onclick="this.classList.toggle('expanded')">
<div class="card-header"><span class="cat-badge">{m['cat']}</span><span class="card-num">#{i+1}</span></div>
<h2 class="paper-title">{p['title']}</h2><p class="authors">{p['authors']}</p>
<p class="abstract"><em>{p['abstract']}</em></p>{img_tag}
<div class="explanation">{expl}</div><div class="expand-hint"></div></div>""")

html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>arXiv Paper Blueprint 6.16-6.17</title><style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#080c14;color:#e0e8f0;font-family:'Cascadia Code','Consolas',monospace;padding:20px}}
.header{{text-align:center;padding:40px 20px 30px;border-bottom:1px solid #1e3a5f;margin-bottom:30px}}
.header h1{{font-size:26px;color:#00d4ff;letter-spacing:2px}}.header p{{color:#6b7fa0;margin-top:8px;font-size:13px}}
.nav{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:28px}}
.nav-btn{{padding:7px 16px;border:1px solid #1e3a5f;border-radius:18px;background:transparent;color:#8899b0;cursor:pointer;font-family:inherit;font-size:12px;transition:all .3s}}
.nav-btn:hover,.nav-btn.active{{border-color:#00d4ff;color:#00d4ff;background:rgba(0,212,255,.08)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:22px;max-width:1400px;margin:0 auto}}
.card{{background:var(--bg,#0a1628);border:1px solid #1e3a5f;border-radius:12px;padding:22px;cursor:pointer;transition:all .3s;position:relative;overflow:hidden}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--accent,#00d4ff)}}
.card:hover{{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,212,255,.1)}}
.card:not(.expanded) .explanation{{max-height:100px;overflow:hidden;position:relative}}
.card:not(.expanded) .explanation::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:50px;background:linear-gradient(transparent,var(--bg,#0a1628))}}
.card-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}}
.cat-badge{{font-size:10px;padding:3px 9px;border:1px solid var(--accent);border-radius:12px;color:var(--accent)}}
.card-num{{font-size:11px;color:#4a5f7a}}.paper-title{{font-size:15px;color:#fff;line-height:1.4;margin-bottom:6px}}
.authors{{font-size:11px;color:#6b7fa0;margin-bottom:8px}}.abstract{{font-size:12px;color:#8899b0;line-height:1.6;margin-bottom:10px}}
.card img{{width:100%;border-radius:8px;margin:12px 0;border:1px solid #1e3a5f}}
.explanation{{font-size:12px;color:#c0cde0;line-height:1.8}}
.explanation h3{{font-size:13px;color:var(--accent);margin:10px 0 5px}}.explanation strong{{color:#fff}}
.explanation li{{margin-left:18px;margin-bottom:3px}}
.expand-hint{{text-align:center;font-size:10px;color:#3a4f6a;margin-top:10px}}
.card.expanded .expand-hint::before{{content:'click to collapse'}}.card:not(.expanded) .expand-hint::before{{content:'click to expand'}}
@media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="header"><h1>arXiv Paper Blueprint</h1>
<p>2026-06-16 & 06-17 | GPT-5.5 Explanations + GPT-Image-2 Blueprints | 10 Papers, 4 Categories</p></div>
<div class="nav">
<button class="nav-btn active" onclick="f('all')">All (10)</button>
<button class="nav-btn" onclick="f('Agent与多智能体')">Agent (3)</button>
<button class="nav-btn" onclick="f('推理与强化学习')">Reasoning/RL (3)</button>
<button class="nav-btn" onclick="f('具身智能与物理AI')">Embodied (2)</button>
<button class="nav-btn" onclick="f('LLM理论与分析')">LLM Theory (2)</button>
</div><div class="grid" id="grid">{''.join(cards)}</div>
<script>function f(c){{document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));event.target.classList.add('active');document.querySelectorAll('.card').forEach(d=>{{d.style.display=(c==='all'||d.querySelector('.cat-badge').textContent===c)?'':'none'}})}}document.querySelector('.card')?.classList.add('expanded');</script></body></html>"""

html_path = os.path.join(REPO, "paper-blueprint.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"  -> paper-blueprint.html")

# Also copy to outputs
out_html = os.path.join(BASE, "paper-cards.html")
shutil.copy2(html_path, out_html)
print(f"  -> Also copied to outputs: {out_html}")

# ── Step 6: README ──
readme = """# arXiv 论文复现 — 2026-06-16 & 06-17

> GPT-5.5 深度解读 + GPT-Image-2 工程蓝图配图

## 分类

| 分类 | 论文数 | 文件 |
|------|--------|------|
| Agent与多智能体 | 3 | Agent与多智能体.md |
| 推理与强化学习 | 3 | 推理与强化学习.md |
| 具身智能与物理AI | 2 | 具身智能与物理AI.md |
| LLM理论与分析 | 2 | LLM理论与分析.md |

## 交互式卡片

打开 [paper-blueprint.html](paper-blueprint.html) 查看交互式卡片页面。

## 配图说明

所有配图由 GPT-Image-2 生成，采用工程蓝图风格（深蓝底+青白线条），标注为英文以避免中文字体问题。

## 论文列表

1. SEAGym: Self-Evolving Agent Evaluation
2. CEO-Bench: Can LLMs Be CEOs?
3. Distributed Agent Networks
4. E3RL: Autoregressive Curse
5. FlowRAG: Graph Flow
6. Small Initialization Matters
7. DeepInsight: Physical AI Stack
8. PreAct: Faster Agents
9. Inference Compute & Evaluation
10. Code Reasoning Lifecycle
"""
with open(os.path.join(REPO, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme)
print(f"  -> README.md")

print(f"\n{'='*50}")
print(f"  DONE! All files in: {REPO}")
print(f"{'='*50}")
