"""Generate blueprint images for Feb 5-17 papers"""
import requests, json, base64, os, time, sys

API_KEY = "sk-vpBVC7bc3t9dDAVMPprGsxW4fEgQtuzn2lkMgrGW7SpQGRel"
BASE = "https://lanyiapi.com/v1"
IMG_DIR = "E:/my-dev-favorites/05-papers/reproduce-0205-0217/images"
os.makedirs(IMG_DIR, exist_ok=True)

PAPERS = [
    ("nanbeige", "Nanbeige4.1-3B Small General Model",
     ["Combined reward modeling", "Complexity-aware RL", "Turn-level supervision", "Tool calling 600+ turns", "3B parameter core", "Benchmark evaluator"]),
    ("glm5", "GLM-5 Agentic Engineering 754B",
     ["Creation phase", "Optimization phase", "Concurrent reward training", "Decoupled architecture", "Code generator", "Application builder"]),
    ("rarl", "RARL Reward Modeling for RL Reasoning",
     ["Process rewards", "Outcome rewards", "Consistency rewards", "Sequential incentive chain", "Anti-reward-hacking", "Hallucination reducer"]),
    ("optimal_length", "Optimal Reasoning Length Control",
     ["Length sampler", "Performance monitor", "Mode answer tracker", "Dispersion analyzer", "Early stopping", "Token budget"]),
    ("self_evolving", "Self-evolving Embodied AI",
     ["Skill acquisition", "Memory reorganization", "Policy adaptation", "Body model update", "Goal evolution", "Environment interaction"]),
    ("vit5", "ViT-5 Vision Transformer Mid-2020s",
     ["Native multimodal input", "Improved attention", "Pixel-to-token", "Training stabilizer", "Multi-scale features", "Downstream heads"]),
    ("step35", "Step 3.5 Flash 11B Active MoE",
     ["Interleaved 3:1 attention", "Sliding window layers", "Full attention layers", "Multi-token prediction", "MoE router", "196B total 11B active"]),
    ("symmetry", "Symmetry in Language Statistics",
     ["Language data", "Symmetry detector", "Embedding projector", "Circle patterns", "Linear patterns", "Translational invariance"]),
]

def gen_image(prompt, filename):
    filepath = os.path.join(IMG_DIR, filename)
    if os.path.exists(filepath):
        print(f"  SKIP {filename}")
        return True
    resp = requests.post(f"{BASE}/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-image-2", "prompt": prompt, "n": 1,
              "size": "1536x1024", "response_format": "b64_json"},
        timeout=300)
    data = resp.json()
    if "data" in data and data["data"]:
        img = base64.b64decode(data["data"][0]["b64_json"])
        with open(filepath, "wb") as f:
            f.write(img)
        print(f"  OK: {filename} ({len(img)//1024}KB)")
        return True
    print(f"  Error: {str(data)[:200]}")
    return False

success = 0
for i, (pid, title, components) in enumerate(PAPERS):
    fname = f"{pid}.png"
    print(f"[{i+1}/{len(PAPERS)}] {fname}")
    sys.stdout.flush()
    comp_list = ", ".join(components)
    prompt = f"""Engineering blueprint technical architecture diagram.
Title: {title}
Components: {comp_list}
Style: Dark navy background (#0a1628), cyan/teal line art (#00d4ff), white text labels, 
engineering schematic aesthetic, grid lines in subtle dark blue, rectangular modules with 
rounded corners, data flow arrows (cyan), performance metrics annotations.
ALL TEXT IN ENGLISH only, no Chinese characters. Clean professional style."""
    if gen_image(prompt, fname):
        success += 1
    time.sleep(3)
    sys.stdout.flush()

print(f"\nDone! {success}/{len(PAPERS)} blueprints.")
