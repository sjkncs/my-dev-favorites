"""
Paper Reproduction Script: GPT-5.5 + GPT-Image-2
Generates deep explanations + engineering blueprint diagrams for arXiv papers
"""
import json, base64, os, sys, time, requests

API_KEY = "sk-vpBVC7bc3t9dDAVMPprGsxW4fEgQtuzn2lkMgrGW7SpQGRel"
API_BASE = "https://lanyiapi.com/v1"
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")
MD_DIR = os.path.join(os.path.dirname(__file__), "markdown")

# ── Paper Database ──
PAPERS = [
    # ═══ Category 1: Agent & Multi-Agent Systems ═══
    {
        "id": "seagym", "cat": "Agent & Multi-Agent", "cat_zh": "Agent与多智能体",
        "title": "SEAGym: An Evaluation Environment for Self-Evolving LLM Agents",
        "authors": "Congjie Zheng, Chuanyi Xue, Bin Liang, Jun Yang, Changshui Zhang",
        "abstract": "Develops SEAGym environment to measure agent harness updates. Tracks evolution across training, validation, replay, and cost records dynamically.",
        "why_interesting": "First standardized benchmark for self-evolving agents. Measures not just final accuracy but HOW the agent improves over time.",
    },
    {
        "id": "ceo_bench", "cat": "Agent & Multi-Agent", "cat_zh": "Agent与多智能体",
        "title": "Can LLMs Be CEOs? Benchmarking Strategic Resource Reallocation",
        "authors": "Yuyang Dai, Xueqing Peng, Lingfei Qian, Zhuohan Xie",
        "abstract": "Introduces CEO-Bench evaluating strategic resource allocation with conflicting advisor inputs. Identifies failure modes like single-advisor capture in multi-role settings.",
        "why_interesting": "Tests whether LLMs can make high-stakes strategic decisions like a CEO. Reveals critical 'single-advisor capture' failure mode.",
    },
    {
        "id": "dist_agent_net", "cat": "Agent & Multi-Agent", "cat_zh": "Agent与多智能体",
        "title": "Distributed General-Purpose Agent Networks",
        "authors": "Shengli Zhang, Deen Ma, Zibin Lin, Taotao Wang",
        "abstract": "Proposes architecture for peer-to-peer agent networks. Emphasizes semantic communication and trust mechanisms for open task execution between devices.",
        "why_interesting": "Envisions a future where AI agents on different devices collaborate like a distributed computing network, not just client-server.",
    },
    # ═══ Category 2: Reasoning & RL ═══
    {
        "id": "e3rl", "cat": "Reasoning & RL", "cat_zh": "推理与强化学习",
        "title": "E\u00b3RL: Shattering the Autoregressive Curse for LLMs",
        "authors": "Ziliang Wang, Kang An, Faqiang Qian et al.",
        "abstract": "Proposes E3RL to handle autoregressive cascades in reasoning. Grounds uncertainty in cross-entropy to excise defects while preserving KV cache efficiency.",
        "why_interesting": "Attacks the fundamental 'error cascade' problem in autoregressive reasoning. Cross-entropy based uncertainty grounding is elegant and practical.",
    },
    {
        "id": "flowrag", "cat": "Reasoning & RL", "cat_zh": "推理与强化学习",
        "title": "FlowRAG: Frequency-Aware Multi-Granularity Graph Flow",
        "authors": "Bihao Zhan, Zongsheng Cao, Jie Zhou, Bo Zhang, Liang He",
        "abstract": "Enhances GraphRAG with quad-level heterogeneous graphs. Routes relevance through frequency-aware flow modules to prune noisy connections.",
        "why_interesting": "Upgrades GraphRAG from simple graph traversal to frequency-aware flow. The quad-level graph structure captures both fine and coarse semantic relationships.",
    },
    {
        "id": "small_init", "cat": "Reasoning & RL", "cat_zh": "推理与强化学习",
        "title": "Small Initialization Matters for Large Language Models",
        "authors": "Liangkai Hang, Junjie Yao, Zhiyu Li et al.",
        "abstract": "Shows parameter initialization scale determines training and capacity. Small initialization drives low-complexity structures improving reasoning capabilities.",
        "why_interesting": "Counter-intuitive finding: smaller initialization = better reasoning. Challenges the 'bigger is better' assumption in LLM training.",
    },
    # ═══ Category 3: Embodied & Physical AI ═══
    {
        "id": "deepinsight", "cat": "Embodied & Physical AI", "cat_zh": "具身智能与物理AI",
        "title": "DeepInsight: Unified Evaluation Infrastructure Across Physical AI Stack",
        "authors": "Siyi Li, Chunyu Sun, Jiahao Zhang et al.",
        "abstract": "Offers unified infrastructure evaluating Physical AI stacks from decoding to control. Preserves heterogeneity while enabling cross-layer diagnostic traceability.",
        "why_interesting": "First unified evaluation framework for the entire Physical AI stack. Enables apples-to-apples comparison across different embodied AI systems.",
    },
    {
        "id": "preact", "cat": "Embodied & Physical AI", "cat_zh": "具身智能与物理AI",
        "title": "PreAct: Computer-Using Agents that Get Faster on Repeated Tasks",
        "authors": "Bojie Li",
        "abstract": "Allows agents to compile successful runs into state-machine programs. Replay checks screen states before acting, speeding up repeated tasks significantly.",
        "why_interesting": "Bridges the gap between 'learning to do' and 'doing faster'. The state-machine compilation idea is directly applicable to production agent systems.",
    },
    # ═══ Category 4: LLM Theory & Analysis ═══
    {
        "id": "inference_compute", "cat": "LLM Theory & Analysis", "cat_zh": "LLM理论与分析",
        "title": "How Inference Compute Shapes Frontier LLM Evaluation",
        "authors": "Jessica McFadyen, Ole Jorgensen, Harry Coppock et al.",
        "abstract": "Analyzes performance sensitivity to inference compute budgets. Argues benchmarks must report capability as function of available test-time resources.",
        "why_interesting": "Challenges the standard benchmark paradigm. A model's 'capability' depends on how much compute you give it at inference time.",
    },
    {
        "id": "code_reasoning", "cat": "LLM Theory & Analysis", "cat_zh": "LLM理论与分析",
        "title": "From Brewing to Resolution: Internal Lifecycle of Code Reasoning in LLMs",
        "authors": "Siyue Chen, Yifu Guo, Yuquan Lu et al.",
        "abstract": "Studies internal code reasoning lifecycle involving answer brewing and resolution phases. Diagnostic framework reveals capability variations across Transformer architectures.",
        "why_interesting": "Opens the black box of LLM code reasoning. The 'brewing' vs 'resolution' phase distinction explains why some models appear to 'think' before answering.",
    },
]

def call_gpt55(prompt, max_tokens=2000):
    """Call GPT-5.5 for text generation"""
    resp = requests.post(
        f"{API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-5.5-openai-compact",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0.7
        }, timeout=120
    )
    return resp.json()["choices"][0]["message"]["content"]

def call_image2(prompt, size="1792x1024"):
    """Call GPT-Image-2 for diagram generation"""
    resp = requests.post(
        f"{API_BASE}/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-image-2",
            "prompt": prompt,
            "size": size,
            "n": 1,
            "response_format": "b64_json"
        }, timeout=180
    )
    data = resp.json()
    if "data" in data and len(data["data"]) > 0:
        return base64.b64decode(data["data"][0]["b64_json"])
    print(f"  Image API error: {json.dumps(data, indent=2)[:500]}")
    return None

def generate_explanation(paper):
    """Generate detailed Chinese explanation using GPT-5.5"""
    prompt = f"""You are an expert AI researcher explaining a paper to a Chinese-speaking engineer.
Generate a DEEP explanation in Chinese (简体中文) for the following paper.

Paper: {paper['title']}
Authors: {paper['authors']}
Abstract: {paper['abstract']}
Why Interesting: {paper['why_interesting']}

Please provide:
1. **核心问题** (1-2 sentences): What fundamental problem does this paper solve?
2. **方法概述** (3-5 sentences): How does it work? Explain the key technical innovation clearly.
3. **架构解析** (3-5 bullet points): Break down the system architecture or algorithm pipeline step by step.
4. **实验亮点** (2-3 points): What are the most impressive or surprising experimental results?
5. **对从业者的启示** (2-3 points): What should engineers/researchers learn from this?
6. **局限性** (1-2 points): What are the main limitations or open questions?

Keep it technical but accessible. Use analogies where helpful. Total ~600 words in Chinese."""
    return call_gpt55(prompt, max_tokens=3000)

def generate_diagram(paper):
    """Generate engineering blueprint style diagram using GPT-Image-2"""
    prompt = f"""Create a technical engineering blueprint diagram for the AI research paper:
"{paper['title']}"

Abstract: {paper['abstract']}

STYLE REQUIREMENTS (STRICT):
- Dark navy/black background (#0a1628)
- White and cyan/light blue lines and text (#00d4ff, #ffffff)
- Thin precise lines, engineering blueprint aesthetic
- Clean geometric shapes, grid overlay (subtle dotted grid)
- ALL text labels in ENGLISH ONLY (no Chinese characters)
- Professional technical diagram look, like an architectural blueprint
- Include directional arrows showing data/information flow

CONTENT REQUIREMENTS:
- Show the system architecture or algorithm pipeline
- Label each component/module clearly in English
- Show input -> processing -> output flow
- Include key equations or metrics if applicable
- Add a title bar at top with paper short name
- Keep it clean and information-dense without clutter"""
    return call_image2(prompt)

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)

    results = {}
    current_cat = ""

    for i, paper in enumerate(PAPERS):
        cat = paper["cat"]
        if cat != current_cat:
            current_cat = cat
            print(f"\n{'='*60}")
            print(f"  Category: {paper['cat_zh']}")
            print(f"{'='*60}")

        print(f"\n[{i+1}/{len(PAPERS)}] {paper['id']}: {paper['title'][:60]}...")

        # 1. Generate explanation
        print("  -> Generating explanation (GPT-5.5)...")
        try:
            explanation = generate_explanation(paper)
            print(f"  -> Explanation: {len(explanation)} chars")
        except Exception as e:
            print(f"  -> Explanation FAILED: {e}")
            explanation = f"(GPT-5.5 generation failed: {e})"

        # 2. Generate diagram
        print("  -> Generating blueprint diagram (GPT-Image-2)...")
        try:
            img_bytes = generate_diagram(paper)
            img_path = os.path.join(IMG_DIR, f"{paper['id']}_blueprint.png")
            if img_bytes:
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
                print(f"  -> Diagram saved: {img_path} ({len(img_bytes)//1024}KB)")
            else:
                img_path = None
                print("  -> Diagram generation returned None")
        except Exception as e:
            print(f"  -> Diagram FAILED: {e}")
            img_path = None

        results[paper["id"]] = {
            "paper": paper,
            "explanation": explanation,
            "img_path": img_path,
        }
        time.sleep(1)  # rate limiting

    # ── Generate Markdown files ──
    print("\n\n=== Generating Markdown files ===")
    cats = {}
    for r in results.values():
        cat = r["paper"]["cat_zh"]
        cats.setdefault(cat, []).append(r)

    for cat_name, papers_in_cat in cats.items():
        md_lines = [f"# {cat_name}\n"]
        for r in papers_in_cat:
            p = r["paper"]
            md_lines.append(f"---\n")
            md_lines.append(f"## {p['title']}\n")
            md_lines.append(f"**Authors**: {p['authors']}\n")
            md_lines.append(f"**Why Interesting**: {p['why_interesting']}\n\n")
            if r["img_path"]:
                rel_img = os.path.relpath(r["img_path"], MD_DIR).replace("\\", "/")
                md_lines.append(f"![Architecture Blueprint]({rel_img})\n\n")
            md_lines.append(f"### Deep Explanation (GPT-5.5)\n")
            md_lines.append(f"{r['explanation']}\n\n")
        md_path = os.path.join(MD_DIR, f"{cat_name.replace(' ','_').replace('&','')}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        print(f"  -> {md_path}")

    # ── Generate Card HTML ──
    print("\n=== Generating Card HTML ===")
    cards_html = []
    for i, r in enumerate(results.values()):
        p = r["paper"]
        img_tag = ""
        if r["img_path"]:
            with open(r["img_path"], "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            img_tag = f'<img src="data:image/png;base64,{img_b64}" style="width:100%;border-radius:8px;margin:12px 0;border:1px solid #1e3a5f;">'

        # Convert explanation markdown to basic HTML
        expl = r["explanation"]
        expl = expl.replace("\n### ", "\n<h3>").replace("\n## ", "\n<h2>")
        for line_new in ["</h3>", "</h2>"]:
            pass
        # Simple markdown to html
        import re
        expl = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', expl)
        expl = re.sub(r'^### (.+)$', r'<h3>\1</h3>', expl, flags=re.MULTILINE)
        expl = re.sub(r'^## (.+)$', r'<h2>\1</h2>', expl, flags=re.MULTILINE)
        expl = re.sub(r'^- (.+)$', r'<li>\1</li>', expl, flags=re.MULTILINE)
        expl = expl.replace("\n\n", "<br><br>")

        cat_colors = {
            "Agent与多智能体": ("#00d4ff", "#0a2540"),
            "推理与强化学习": ("#00ff88", "#0a2820"),
            "具身智能与物理AI": ("#ff6b35", "#2a1a0a"),
            "LLM理论与分析": ("#a855f7", "#1a0a2e"),
        }
        accent, bg = cat_colors.get(p["cat_zh"], ("#00d4ff", "#0a1628"))

        cards_html.append(f"""
        <div class="card" style="--accent:{accent};--bg:{bg};" onclick="this.classList.toggle('expanded')">
            <div class="card-header">
                <span class="cat-badge">{p['cat_zh']}</span>
                <span class="card-num">#{i+1}</span>
            </div>
            <h2 class="paper-title">{p['title']}</h2>
            <p class="authors">{p['authors']}</p>
            <p class="abstract"><em>{p['abstract']}</em></p>
            {img_tag}
            <div class="explanation">{expl}</div>
            <div class="expand-hint">click to expand/collapse</div>
        </div>""")

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>arXiv Paper Reproduction - Engineering Blueprint Style</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#080c14; color:#e0e8f0; font-family:'SF Mono','Cascadia Code','Consolas',monospace; padding:20px; }}
.header {{ text-align:center; padding:40px 20px 30px; border-bottom:1px solid #1e3a5f; margin-bottom:30px; }}
.header h1 {{ font-size:28px; color:#00d4ff; letter-spacing:2px; }}
.header p {{ color:#6b7fa0; margin-top:8px; font-size:14px; }}
.nav {{ display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin-bottom:30px; }}
.nav-btn {{ padding:8px 18px; border:1px solid #1e3a5f; border-radius:20px; background:transparent; color:#8899b0; cursor:pointer; font-family:inherit; font-size:13px; transition:all 0.3s; }}
.nav-btn:hover, .nav-btn.active {{ border-color:var(--accent,#00d4ff); color:var(--accent,#00d4ff); background:rgba(0,212,255,0.08); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(420px,1fr)); gap:24px; max-width:1400px; margin:0 auto; }}
.card {{ background:var(--bg,#0a1628); border:1px solid #1e3a5f; border-radius:12px; padding:24px; cursor:pointer; transition:all 0.3s; position:relative; overflow:hidden; }}
.card::before {{ content:''; position:absolute; top:0; left:0; right:0; height:3px; background:var(--accent,#00d4ff); }}
.card:hover {{ border-color:var(--accent,#00d4ff); transform:translateY(-2px); box-shadow:0 8px 32px rgba(0,212,255,0.1); }}
.card:not(.expanded) .explanation {{ max-height:120px; overflow:hidden; position:relative; }}
.card:not(.expanded) .explanation::after {{ content:''; position:absolute; bottom:0; left:0; right:0; height:60px; background:linear-gradient(transparent,var(--bg,#0a1628)); }}
.card-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }}
.cat-badge {{ font-size:11px; padding:3px 10px; border:1px solid var(--accent,#00d4ff); border-radius:12px; color:var(--accent,#00d4ff); }}
.card-num {{ font-size:12px; color:#4a5f7a; }}
.paper-title {{ font-size:16px; color:#ffffff; line-height:1.4; margin-bottom:8px; }}
.authors {{ font-size:12px; color:#6b7fa0; margin-bottom:10px; }}
.abstract {{ font-size:13px; color:#8899b0; line-height:1.6; margin-bottom:12px; }}
.explanation {{ font-size:13px; color:#c0cde0; line-height:1.8; }}
.explanation h2 {{ font-size:16px; color:#ffffff; margin:16px 0 8px; border-bottom:1px solid #1e3a5f; padding-bottom:4px; }}
.explanation h3 {{ font-size:14px; color:var(--accent,#00d4ff); margin:12px 0 6px; }}
.explanation strong {{ color:#ffffff; }}
.explanation li {{ margin-left:20px; margin-bottom:4px; }}
.expand-hint {{ text-align:center; font-size:11px; color:#3a4f6a; margin-top:12px; }}
.card.expanded .expand-hint::before {{ content:'click to collapse'; }}
.card:not(.expanded) .expand-hint::before {{ content:'click to expand'; }}
@media (max-width:600px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="header">
    <h1>arXiv Paper Reproduction</h1>
    <p>2026-06-16 & 06-17 | GPT-5.5 Explanations + GPT-Image-2 Blueprint Diagrams | 10 Papers, 4 Categories</p>
</div>
<div class="nav">
    <button class="nav-btn active" onclick="filterCards('all')">All</button>
    <button class="nav-btn" onclick="filterCards('Agent与多智能体')" style="--accent:#00d4ff;">Agent</button>
    <button class="nav-btn" onclick="filterCards('推理与强化学习')" style="--accent:#00ff88;">Reasoning/RL</button>
    <button class="nav-btn" onclick="filterCards('具身智能与物理AI')" style="--accent:#ff6b35;">Embodied AI</button>
    <button class="nav-btn" onclick="filterCards('LLM理论与分析')" style="--accent:#a855f7;">LLM Theory</button>
</div>
<div class="grid" id="grid">
    {''.join(cards_html)}
</div>
<script>
function filterCards(cat) {{
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    document.querySelectorAll('.card').forEach(c => {{
        if (cat === 'all' || c.querySelector('.cat-badge').textContent === cat) {{
            c.style.display = '';
        }} else {{
            c.style.display = 'none';
        }}
    }});
}}
// expand first card by default
document.querySelector('.card')?.classList.add('expanded');
</script>
</body>
</html>"""

    html_path = os.path.join(os.path.dirname(MD_DIR), "paper-cards.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  -> Card HTML: {html_path}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  DONE! Generated {len(results)} paper reproductions")
    print(f"  Images: {IMG_DIR}")
    print(f"  Markdown: {MD_DIR}")
    print(f"  Card HTML: {html_path}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
