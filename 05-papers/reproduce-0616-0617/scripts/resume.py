"""Resume script: generate remaining papers + all markdown + HTML"""
import json, base64, os, sys, time, requests, re

API_KEY = "sk-vpBVC7bc3t9dDAVMPprGsxW4fEgQtuzn2lkMgrGW7SpQGRel"
API_BASE = "https://lanyiapi.com/v1"
BASE = r"C:\Users\Lenovo\.qoderwork\workspace\mqi7df873xfl6gf5\outputs\paper-reproduce"
IMG_DIR = os.path.join(BASE, "images")
MD_DIR = os.path.join(BASE, "markdown")

PAPERS = [
    {"id":"seagym","cat":"Agent & Multi-Agent","cat_zh":"Agent与多智能体","title":"SEAGym: Self-Evolving LLM Agent Evaluation","authors":"Congjie Zheng et al.","abstract":"Develops SEAGym environment to measure agent harness updates. Tracks evolution across training, validation, replay, and cost records dynamically.","why_interesting":"First standardized benchmark for self-evolving agents."},
    {"id":"ceo_bench","cat":"Agent & Multi-Agent","cat_zh":"Agent与多智能体","title":"Can LLMs Be CEOs? CEO-Bench","authors":"Yuyang Dai et al.","abstract":"Introduces CEO-Bench evaluating strategic resource allocation with conflicting advisor inputs. Identifies single-advisor capture.","why_interesting":"Tests whether LLMs can make high-stakes strategic decisions."},
    {"id":"dist_agent_net","cat":"Agent & Multi-Agent","cat_zh":"Agent与多智能体","title":"Distributed General-Purpose Agent Networks","authors":"Shengli Zhang et al.","abstract":"Proposes P2P agent network architecture with semantic communication and trust mechanisms.","why_interesting":"Envisions distributed AI agent collaboration like computing networks."},
    {"id":"e3rl","cat":"Reasoning & RL","cat_zh":"推理与强化学习","title":"E³RL: Shattering the Autoregressive Curse","authors":"Ziliang Wang et al.","abstract":"Handles autoregressive cascades via cross-entropy grounded uncertainty. Preserves KV cache efficiency.","why_interesting":"Attacks fundamental error cascade in autoregressive reasoning."},
    {"id":"flowrag","cat":"Reasoning & RL","cat_zh":"推理与强化学习","title":"FlowRAG: Frequency-Aware Graph Flow for RAG","authors":"Bihao Zhan et al.","abstract":"Enhances GraphRAG with quad-level heterogeneous graphs and frequency-aware flow modules.","why_interesting":"Upgrades GraphRAG with frequency-aware flow for noise pruning."},
    {"id":"small_init","cat":"Reasoning & RL","cat_zh":"推理与强化学习","title":"Small Initialization Matters for LLMs","authors":"Liangkai Hang et al.","abstract":"Small initialization drives low-complexity structures improving reasoning. Challenges bigger-is-better.","why_interesting":"Counter-intuitive: smaller init = better reasoning."},
    {"id":"deepinsight","cat":"Embodied & Physical AI","cat_zh":"具身智能与物理AI","title":"DeepInsight: Physical AI Evaluation Stack","authors":"Siyi Li et al.","abstract":"Unified infrastructure evaluating Physical AI from decoding to control with cross-layer traceability.","why_interesting":"First unified eval framework for entire Physical AI stack."},
    {"id":"preact","cat":"Embodied & Physical AI","cat_zh":"具身智能与物理AI","title":"PreAct: Faster Agents on Repeated Tasks","authors":"Bojie Li","abstract":"Compiles successful agent runs into state-machine programs. Replay checks screen states before acting.","why_interesting":"Bridges learning-to-do and doing-faster."},
    {"id":"inference_compute","cat":"LLM Theory & Analysis","cat_zh":"LLM理论与分析","title":"How Inference Compute Shapes LLM Evaluation","authors":"Jessica McFadyen et al.","abstract":"Performance sensitivity to inference compute budgets. Benchmarks should report capability as function of test-time resources.","why_interesting":"Challenges standard benchmark paradigm."},
    {"id":"code_reasoning","cat":"LLM Theory & Analysis","cat_zh":"LLM理论与分析","title":"From Brewing to Resolution: Code Reasoning Lifecycle","authors":"Siyue Chen et al.","abstract":"Studies answer brewing and resolution phases in code reasoning. Reveals capability variations across architectures.","why_interesting":"Opens the black box of LLM code reasoning phases."},
]

def call_gpt55(prompt, max_tokens=2500):
    resp = requests.post(f"{API_BASE}/chat/completions",
        headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
        json={"model":"gpt-5.5-openai-compact","messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens,"temperature":0.7},timeout=120)
    return resp.json()["choices"][0]["message"]["content"]

def call_image2(prompt, size="1792x1024"):
    resp = requests.post(f"{API_BASE}/images/generations",
        headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
        json={"model":"gpt-image-2","prompt":prompt,"size":size,"n":1,"response_format":"b64_json"},timeout=180)
    data = resp.json()
    if "data" in data and data["data"]:
        return base64.b64decode(data["data"][0]["b64_json"])
    print(f"  Image error: {str(data)[:300]}")
    return None

# Check which images already exist
existing = set(f.replace("_blueprint.png","") for f in os.listdir(IMG_DIR) if f.endswith(".png"))
print(f"Existing images: {existing}")

explanations = {}

for paper in PAPERS:
    pid = paper["id"]
    print(f"\n[{pid}]")

    # Generate explanation
    print("  -> GPT-5.5 explanation...")
    try:
        prompt = f"""你是AI研究专家。用中文(简体)为以下论文写深度解读(约500字)。

论文: {paper['title']}
摘要: {paper['abstract']}
亮点: {paper['why_interesting']}

格式:
**核心问题**: (1-2句)
**方法概述**: (3-5句,解释关键技术)
**架构解析**: (3-5个要点,分步解析)
**实验亮点**: (2-3个亮点)
**对从业者的启示**: (2-3点)
**局限性**: (1-2点)"""
        explanations[pid] = call_gpt55(prompt)
        print(f"  -> OK ({len(explanations[pid])} chars)")
    except Exception as e:
        explanations[pid] = f"(生成失败: {e})"
        print(f"  -> FAILED: {e}")

    # Generate image if not exists
    img_path = os.path.join(IMG_DIR, f"{pid}_blueprint.png")
    if pid not in existing:
        print("  -> GPT-Image-2 blueprint...")
        try:
            img_prompt = f"""Technical engineering blueprint diagram for AI paper: "{paper['title']}"
Abstract: {paper['abstract']}
STYLE: Dark navy background (#0a1628), white/cyan lines (#00d4ff, #ffffff), thin precise lines, subtle dotted grid overlay, ALL text in ENGLISH only. Professional technical blueprint aesthetic.
Show: system architecture/algorithm pipeline with labeled components, directional arrows for data flow, input->processing->output. Title bar at top. Clean, information-dense."""
            img_bytes = call_image2(img_prompt)
            if img_bytes:
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
                print(f"  -> Saved ({len(img_bytes)//1024}KB)")
            else:
                print("  -> None returned")
        except Exception as e:
            print(f"  -> FAILED: {e}")
    else:
        print("  -> Image already exists, skipping")
    time.sleep(1)

# ── Generate Markdown files ──
print("\n=== Markdown ===")
os.makedirs(MD_DIR, exist_ok=True)
cats = {}
for p in PAPERS:
    cats.setdefault(p["cat_zh"], []).append(p)

for cat_name, papers_in_cat in cats.items():
    md = [f"# {cat_name}\n"]
    for p in papers_in_cat:
        pid = p["id"]
        img_path = os.path.join(IMG_DIR, f"{pid}_blueprint.png")
        md.append(f"---\n## {p['title']}\n")
        md.append(f"**Authors**: {p['authors']}\n")
        md.append(f"**Why Interesting**: {p['why_interesting']}\n\n")
        if os.path.exists(img_path):
            rel = os.path.relpath(img_path, MD_DIR).replace("\\","/")
            md.append(f"![Blueprint]({rel})\n\n")
        md.append(f"### GPT-5.5 Deep Explanation\n{explanations.get(pid,'(N/A)')}\n\n")
    md_path = os.path.join(MD_DIR, f"{cat_name.replace(' ','_').replace('&','')}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"  -> {md_path}")

# ── Generate Card HTML ──
print("\n=== Card HTML ===")
cat_colors = {"Agent与多智能体":("#00d4ff","#0a2540"),"推理与强化学习":("#00ff88","#0a2820"),"具身智能与物理AI":("#ff6b35","#2a1a0a"),"LLM理论与分析":("#a855f7","#1a0a2e")}

cards = []
for i, p in enumerate(PAPERS):
    pid = p["id"]
    img_path = os.path.join(IMG_DIR, f"{pid}_blueprint.png")
    img_tag = ""
    if os.path.exists(img_path):
        with open(img_path,"rb") as f:
            img_tag = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" style="width:100%;border-radius:8px;margin:12px 0;border:1px solid #1e3a5f;">'
    accent, bg = cat_colors.get(p["cat_zh"],("#00d4ff","#0a1628"))
    expl = explanations.get(pid,"(N/A)")
    expl = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', expl)
    expl = re.sub(r'^### (.+)$', r'<h3>\1</h3>', expl, flags=re.MULTILINE)
    expl = re.sub(r'^## (.+)$', r'<h2>\1</h2>', expl, flags=re.MULTILINE)
    expl = re.sub(r'^- (.+)$', r'<li>\1</li>', expl, flags=re.MULTILINE)
    expl = expl.replace("\n\n","<br><br>").replace("\n","<br>")

    cards.append(f"""<div class="card" style="--accent:{accent};--bg:{bg};" onclick="this.classList.toggle('expanded')">
<div class="card-header"><span class="cat-badge">{p['cat_zh']}</span><span class="card-num">#{i+1}</span></div>
<h2 class="paper-title">{p['title']}</h2>
<p class="authors">{p['authors']}</p>
<p class="abstract"><em>{p['abstract']}</em></p>
{img_tag}
<div class="explanation">{expl}</div>
<div class="expand-hint"></div>
</div>""")

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>arXiv Paper Blueprint - 6.16 & 6.17</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#080c14;color:#e0e8f0;font-family:'Cascadia Code','Consolas',monospace;padding:20px}}
.header{{text-align:center;padding:40px 20px 30px;border-bottom:1px solid #1e3a5f;margin-bottom:30px}}
.header h1{{font-size:26px;color:#00d4ff;letter-spacing:2px}}
.header p{{color:#6b7fa0;margin-top:8px;font-size:13px}}
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
.card-num{{font-size:11px;color:#4a5f7a}}
.paper-title{{font-size:15px;color:#fff;line-height:1.4;margin-bottom:6px}}
.authors{{font-size:11px;color:#6b7fa0;margin-bottom:8px}}
.abstract{{font-size:12px;color:#8899b0;line-height:1.6;margin-bottom:10px}}
.explanation{{font-size:12px;color:#c0cde0;line-height:1.8}}
.explanation h2{{font-size:15px;color:#fff;margin:14px 0 6px;border-bottom:1px solid #1e3a5f;padding-bottom:3px}}
.explanation h3{{font-size:13px;color:var(--accent);margin:10px 0 5px}}
.explanation strong{{color:#fff}}
.explanation li{{margin-left:18px;margin-bottom:3px}}
.expand-hint{{text-align:center;font-size:10px;color:#3a4f6a;margin-top:10px}}
.card.expanded .expand-hint::before{{content:'click to collapse'}}
.card:not(.expanded) .expand-hint::before{{content:'click to expand'}}
@media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="header"><h1>arXiv Paper Blueprint</h1>
<p>2026-06-16 & 06-17 | GPT-5.5 Explanations + GPT-Image-2 Blueprints | 10 Papers, 4 Categories</p></div>
<div class="nav">
<button class="nav-btn active" onclick="filter('all')">All (10)</button>
<button class="nav-btn" onclick="filter('Agent与多智能体')">Agent (3)</button>
<button class="nav-btn" onclick="filter('推理与强化学习')">Reasoning/RL (3)</button>
<button class="nav-btn" onclick="filter('具身智能与物理AI')">Embodied (2)</button>
<button class="nav-btn" onclick="filter('LLM理论与分析')">LLM Theory (2)</button>
</div>
<div class="grid" id="grid">{''.join(cards)}</div>
<script>
function filter(c){{document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));event.target.classList.add('active');document.querySelectorAll('.card').forEach(d=>{{d.style.display=(c==='all'||d.querySelector('.cat-badge').textContent===c)?'':'none'}})}}
document.querySelector('.card')?.classList.add('expanded');
</script></body></html>"""

html_path = os.path.join(BASE, "paper-cards.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"  -> {html_path}")
print("\nDONE!")
