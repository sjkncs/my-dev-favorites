# 2026 年计算机国际顶会论文汇总

> 汇总日期：2026-06-11  
> 范围：CVPR 2026 / ICLR 2026 / ICML 2026 / ACL 2026 / MLSys 2026  
> 注：NeurIPS 2026 尚在审稿阶段（截稿 5 月，接收结果预计 9 月公布），暂无已公开接收论文。

---

## 一、CVPR 2026（计算机视觉与模式识别）

CVPR 2026 于 6 月在美国丹佛举行，共接收约 4,000 余篇论文。

### 1. D4RT: Unified, Fast 4D Scene Reconstruction & Tracking（最佳论文奖）
- **作者/机构**：Chuhan Zhang, Guillaume Le Moing, Skanda Koppula 等 / Google DeepMind, UCL, Oxford
- **一句话摘要**：统一的前馈 Transformer 架构，可从单段视频中联合推断深度、时空对应关系和完整相机参数，速度比传统方法快 18-300 倍。
- **原文链接**：[arXiv:2512.08924](https://arxiv.org/abs/2512.08924)
- **PDF**：[下载](https://arxiv.org/pdf/2512.08924)

### 2. TRELLIS.2: Native and Compact Structured Latents for 3D Generation（最佳学生论文奖）
- **作者/机构**：Jianfeng Xiang, Xiaoxue Chen, Sicheng Xu 等 / 清华大学、微软研究院、中国科学技术大学
- **一句话摘要**：提出 O-Voxel 结构化潜表示，实现原生 3D 大模型生成，可在 17 秒内生成超高精度 PBR 资产。
- **原文链接**：[arXiv:2512.14692](https://arxiv.org/abs/2512.14692)
- **PDF**：[下载](https://arxiv.org/pdf/2512.14692)

### 3. Molmo2: Open Weights and Data for Vision-Language Models with Video Understanding and Grounding
- **作者/机构**：Christopher Clark 等（21 位作者）/ Allen Institute for AI (AI2)
- **一句话摘要**：开源视频语言模型新家族 Molmo2，在视频理解、指向、跟踪和计数等任务上达到开源模型 SOTA 水平。
- **原文链接**：[arXiv:2601.10611](https://arxiv.org/abs/2601.10611)
- **PDF**：[下载](https://arxiv.org/pdf/2601.10611)

### 4. NitroGen: An Open Foundation Model for Generalist Gaming Agents（最佳论文荣誉提名）
- **作者/机构**：Loic Magne 等 / NVIDIA
- **一句话摘要**：基于 40,000 小时游戏视频训练的通用视觉-动作基础模型，可在 1,000 多款游戏中执行通用游戏智能体任务。
- **原文链接**：[arXiv:2601.02427](https://arxiv.org/abs/2601.02427)
- **PDF**：[下载](https://arxiv.org/pdf/2601.02427)

### 5. SAM 3D: 3Dfy Anything in Images（最佳论文荣誉提名）
- **作者/机构**：Xingyu Chen 等（22 位作者）/ Meta AI
- **一句话摘要**：基于视觉提示的 3D 物体重建生成模型，可从单张图像预测几何、纹理和布局，实现"万物 3D 化"。
- **原文链接**：[arXiv:2511.16624](https://arxiv.org/abs/2511.16624)
- **PDF**：[下载](https://arxiv.org/pdf/2511.16624)

### 6. 3DReflecNet: A Large-Scale Dataset for 3D Reconstruction of Reflective, Transparent, and Low-Texture Objects
- **作者/机构**：Zhicheng Liang 等 / 港中深 NAIS Lab
- **一句话摘要**：首个面向高反光、透明和低纹理物体的 3D 重建大规模数据集。
- **原文链接**：[arXiv:2605.10204](https://arxiv.org/abs/2605.10204)
- **PDF**：[下载](https://arxiv.org/pdf/2605.10204)

### 7. GLINT: Modeling Scene-Scale Transparency via Gaussian Radiance Transport
- **作者/机构**：Youngju Na 等 / KAIST
- **一句话摘要**：通过高斯辐射传输框架建模场景级透明效果，将出射辐射分解为界面、反射和透射分量分别重建。
- **原文链接**：[arXiv:2603.26181](https://arxiv.org/abs/2603.26181)
- **PDF**：[下载](https://arxiv.org/pdf/2603.26181)

### 8. ViT3: Unlocking Test-Time Training in Vision
- **作者/机构**：Dongchen Han, Yining Li, Tianyu Li 等 / 清华大学、阿里巴巴
- **一句话摘要**：首个纯测试时训练(TTT)视觉架构，实现线性复杂度和可并行计算，在分类、检测、分割、生成等任务上验证有效。
- **原文链接**：[arXiv:2512.01643](https://arxiv.org/abs/2512.01643)
- **PDF**：[下载](https://arxiv.org/pdf/2512.01643)

---

## 二、ICLR 2026（国际学习表征会议）

ICLR 2026 于 4 月举行，共接收约 1,200 篇论文。

### 1. Transformers are Inherently Succinct（杰出论文奖）
- **作者/机构**：Pascal Bergstraesser, Ryan Cotterell, Anthony W. Lin / ETH Zurich, MPI-SWS
- **一句话摘要**：理论证明固定精度的 Transformer 在表达能力上具有内在简洁性，从计算复杂度角度提供了 Transformer 与 RNN 相比的新视角。
- **原文链接**：[arXiv:2510.19315](https://arxiv.org/abs/2510.19315)
- **PDF**：[下载](https://arxiv.org/pdf/2510.19315)

### 2. LLMs Get Lost In Multi-Turn Conversation（杰出论文奖）
- **作者/机构**：Philippe Laban, Hiroaki Hayashi, Yingbo Zhou, Jennifer Neville / Salesforce AI Research
- **一句话摘要**：系统评估了大型语言模型在多轮对话中的退化现象，发现 LLMs 在对话早期即形成错误假设，一旦"走错路"便无法恢复。
- **原文链接**：[arXiv:2505.06120](https://arxiv.org/abs/2505.06120)
- **PDF**：[下载](https://arxiv.org/pdf/2505.06120)

### 3. Improving Language Understanding by Generative Pre-Training（时间检验奖，GPT-1）
- **作者/机构**：Alec Radford, Karthik Narasimhan / OpenAI
- **一句话摘要**：OpenAI 初代 GPT 论文，首次提出生成式预训练（GPT）范式，奠定了后续 GPT 系列及大语言模型时代的基础。

### 4. Identity-Free Deferral For Unseen Experts
- **作者/机构**：Joshua Strong 等 / Cornell University
- **一句话摘要**：提出无身份识别 deferral (IFD) 方法，使 AI 系统在无法识别专家身份时仍能可靠地选择 defer，提升泛化能力。
- **原文链接**：[arXiv:2502.10533](https://arxiv.org/abs/2502.10533)
- **PDF**：[下载](https://arxiv.org/pdf/2502.10533)

---

## 三、ICML 2026（国际机器学习大会）

ICML 2026 将于 7 月在韩国首尔举行，已公布 Oral 和 Spotlight 论文。

### 1. OPUS: Towards Efficient and Principled Data Selection in Large Language Model Pre-training in Every Iteration（Oral）
- **作者/机构**：Shaobo Wang, Xuan Ouyang, Tianyi Xu, Yuzheng Hu 等
- **一句话摘要**：提出在 LLM 预训练的每一次迭代中进行高效数据选择的方法，通过将候选数据的有效更新投影到目标方向，显著提升预训练效率。
- **原文链接**：[arXiv:2602.05400](https://arxiv.org/abs/2602.05400)
- **PDF**：[下载](https://arxiv.org/pdf/2602.05400)

### 2. daVinci-Dev: Agent-native Mid-training for Software Engineering（Oral）
- **作者/机构**：Ji Zeng 等 / 上海交大 GAIR-NLP
- **一句话摘要**：建立面向软件工程智能体的数据合成原则和训练方法，使大语言模型在智能体环境中实现高效的中期训练。
- **原文链接**：[arXiv:2601.18418](https://arxiv.org/abs/2601.18418)
- **PDF**：[下载](https://arxiv.org/pdf/2601.18418)

### 3. Do We Need Adam? Surprisingly Strong and Sparse Reinforcement Learning with SGD in LLMs（Oral）
- **作者/机构**：Sagnik Mukherjee, Lifan Yuan, Pavan Jayasinha, Dilek Hakkani-Tuer, Hao Peng
- **一句话摘要**：挑战 Adam 优化器在 LLM 强化学习中的主导地位，证明 SGD 全量微调仅更新不到 0.02% 的参数即可达到 surprisingly strong 的稀疏强化学习效果。
- **原文链接**：[arXiv:2602.07729](https://arxiv.org/abs/2602.07729)
- **PDF**：[下载](https://arxiv.org/pdf/2602.07729)

### 4. VALUEFLOW: Toward Pluralistic and Steerable Value-based Alignment in Large Language Models（Spotlight）
- **作者/机构**：Woojin Kim 等 / 首尔国立大学 AIDAS Lab
- **一句话摘要**：首个统一的价值对齐框架，覆盖价值提取、评估和定向引导，支持校准强度控制，实现多元可操控的价值对齐。
- **原文链接**：[arXiv:2602.03160](https://arxiv.org/abs/2602.03160)
- **PDF**：[下载](https://arxiv.org/pdf/2602.03160)

### 5. PhotoAgent: Agentic Photo Editing with Exploratory Visual Aesthetic Planning（Oral）
- **作者/机构**：Mingde Yao 等 / 港中文 MMLab、上海 AI Lab、东京科学大学
- **一句话摘要**：将自主图像编辑建模为长程决策问题，通过树搜索推理用户审美意图并规划多步编辑动作。
- **原文链接**：[arXiv:2602.22809](https://arxiv.org/abs/2602.22809)
- **PDF**：[下载](https://arxiv.org/pdf/2602.22809)

### 6. Are VLMs Seeing or Just Saying? Uncovering the Illusion of Visual Perception in Multimodal LLMs（Oral）
- **作者/机构**：Chufan Shi, Cheng Yang, Jiaqi Wang 等
- **一句话摘要**：揭示多模态大语言模型中的视觉感知幻觉，发现模型在图像内容被交换后仍坚持错误判断，且自我反思无法修正。
- **原文链接**：[arXiv:2605.15864](https://arxiv.org/abs/2605.15864)
- **PDF**：[下载](https://arxiv.org/pdf/2605.15864)

### 7. RoboMME: Benchmarking and Understanding Memory for Robotic Generalist Policies（Spotlight）
- **作者/机构**：Yinpei Dai 等
- **一句话摘要**：首个针对机器人通才策略记忆的系统性基准测试，评估和揭示机器人智能体在记忆机制上的能力与局限。
- **原文链接**：[arXiv:2603.04639](https://arxiv.org/abs/2603.04639)
- **PDF**：[下载](https://arxiv.org/pdf/2603.04639)

### 8. Maximum Likelihood Reinforcement Learning（Oral）
- **作者/机构**：Fahim Tajwar 等 / Zanette Labs, UC Berkeley
- **一句话摘要**：提出最大似然强化学习框架，为离线 RL 和在线 RL 提供新的理论基础和算法统一视角。
- **原文链接**：[ICML 2026 Oral](https://icml.cc/virtual/2026/oral/71072)
- **PDF**：[下载](https://arxiv.org/pdf/2603.03480)

---

## 四、ACL 2026（计算语言学协会年会）

ACL 2026 将于 7 月在美国圣地亚哥举行。

### 1. Towards Intrinsic Interpretability of Large Language Models: A Survey of Design Principles and Architectures
- **作者/机构**：Yutong Gao, Qinglin Meng, Yuan Zhou, Liangming Pan / 北京大学 PILLAR Group
- **一句话摘要**：首个系统梳理大语言模型内在可解释性设计原则与架构的综述，提出从模型结构层面实现可解释性的新视角。
- **原文链接**：[arXiv:2604.16042](https://arxiv.org/abs/2604.16042)
- **PDF**：[下载](https://arxiv.org/pdf/2604.16042)

### 2. Words that Make SE: 代码切换(Code-Switching)暴露 LLM 安全漏洞
- **作者/机构**：Rajvee Sheth 等 / IIT Gandhinagar
- **一句话摘要**：发现大语言模型在代码切换（混合语言）场景下会出现安全对齐失效，单个中文字词即可触发安全漏洞。

### 3. Jailbreak Foundry: From Papers to Runnable Attacks for Reproducible Benchmarking
- **作者/机构**：Zhicheng Fang 等
- **一句话摘要**：将越狱攻击论文转化为可复现的可运行攻击的系统框架，推动越狱研究的可重复基准测试。
- **原文链接**：[GitHub](https://github.com/OpenSQZ/Jailbreak-Foundry)

### 4. Mitigating Reward Hacking in RLHF via Bayesian Non-negative Reward Modeling
- **作者/机构**：Zhibin Duan 等
- **一句话摘要**：通过贝叶斯非负奖励建模缓解 RLHF 中的奖励黑客问题，提升大模型对齐的稳定性和可靠性。

---

## 五、MLSys 2026（机器学习与系统大会）

MLSys 2026 于 5 月在美国华盛顿州举行。

### 1. LEANN: A Low-Storage Vector Index（最佳研究论文奖）
- **作者/机构**：Yifei Wang 等 / CMU, Zhihao Jia 团队
- **一句话摘要**：创新向量数据库索引方法，在保证高质量向量搜索的同时仅使用传统方法一小部分的存储开销。
- **原文链接**：[arXiv:2506.08276](https://arxiv.org/abs/2506.08276)
- **PDF**：[下载](https://arxiv.org/pdf/2506.08276)

### 2. ExecuTorch: A Unified PyTorch Solution to Run ML Models On-Device（最佳产业论文奖）
- **作者/机构**：Mergen Nachin, Digant Desai, Sicheng Stephen Jia 等 / Meta (PyTorch 团队)
- **一句话摘要**：统一的 PyTorch 原生端侧推理解决方案，支持在手机、嵌入式设备等边缘设备上高效运行机器学习模型。
- **原文链接**：[arXiv:2605.08195](https://arxiv.org/abs/2605.08195)
- **PDF**：[下载](https://arxiv.org/pdf/2605.08195)

---

## 趋势总结

2026 年上半年 AI 研究极为活跃，以下几个方向尤为突出：

1. **大模型效率与训练**：OPUS（数据选择）、Do We Need Adam?（优化器）、LEANN（向量索引）
2. **多模态与视觉语言模型**：Molmo2（视频 VLM）、SAM 3D（3D 重建）、Are VLMs Seeing or Just Saying?（VLM 幻觉）
3. **AI Agent**：NitroGen（游戏智能体）、daVinci-Dev（软件工程智能体）、PhotoAgent（视觉编辑智能体）
4. **安全与对齐**：VALUEFLOW（价值对齐）、Jailbreak Foundry（越狱基准）
5. **3D 视觉与生成**：D4RT（4D 重建）、TRELLIS.2（3D 生成）、GLINT（透明材质）
6. **理论与可解释性**：Transformers are Inherently Succinct（理论）、Intrinsic Interpretability（可解释性）
