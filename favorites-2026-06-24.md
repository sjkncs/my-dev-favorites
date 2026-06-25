# 我的开发收藏夹

> 每日更新的效率小技巧 & 热门开源仓库收藏  
> 最后更新：2026-06-24

---

## 效率小技巧

### 1. fd —— find 的 Rust 替代品
- **用途**：秒级模糊查找文件
- **亮点**：默认忽略 `.git` 和 `node_modules`，支持正则和模糊匹配
- **示例**：`fd "config.*ts"` 一敲就出结果
- **搭配**：和 `ripgrep`（`rg`）组合使用，文件检索效率翻倍
- **安装**：`cargo install fd-find` 或包管理器直接装

### 2. ripgrep（rg）—— grep 的极速替代品
- **用途**：代码搜索
- **亮点**：Rust 编写，自动忽略 `.gitignore` 文件，多线程并行搜索
- **示例**：`rg "TODO" --type js`
- **搭配**：和 `fd` 组合使用

---

## 热门开源仓库

### 1. OpenDevin-Next
- **做什么**：AI 自动重构代码，识别潜在隐患
- **为什么有趣**：从"AI 玩具"进化成实用开发工具，能帮你在重构时少踩坑
- **Stars**： trending 🔥

### 2. LocalLLM-Runtime
- **做什么**：本地运行 70B 大模型，榨干硬件性能
- **为什么有趣**：不用云端 API，完全本地推理，隐私+省钱双收
- **Stars**： trending 🔥

### 3. Hono-X
- **做什么**：基于 Web 标准的高性能前端框架
- **为什么有趣**：秒级启动，响应极快，适合边缘部署
- **Stars**： trending 🔥

### 4. Odysseus（PewDiePie 手搓 AI 工作台）
- **做什么**：自托管 AI 工作台，把 ChatGPT、Claude 等所有 AI 订阅塞进一个本地界面统一管理，还能跑本地大模型
- **为什么有趣**：YouTube 顶流 PewDiePie 随手搓出来的工具，4 天狂揽 5 万多 GitHub Star，比很多创业公司产品还火
- **Stars**： 50k+ 🔥

---

## 技术冷知识

### 世界上第一个 bug 真的是只虫子
1947 年 9 月，Grace Hopper 在 Harvard Mark II 计算机的继电器触点里发现了一只烤焦的飞蛾，导致机器故障。她把飞蛾尸体贴在工作日志上，写着："First actual case of bug being found." 那只飞蛾的遗体现在还在美国国家历史博物馆里躺着呢，堪称史上最知名的"背锅侠"。

---

## 程序员梗/名言

> "My code doesn't work, I don't know why. My code works, I don't know why."

---

## 更新日志

| 日期 | 新增内容 |
|------|---------|
| 2026-06-11 | 初始创建：fd、ripgrep 技巧 + OpenDevin-Next、LocalLLM-Runtime、Hono-X 仓库 |
| 2026-06-11 | 追加：Odysseus（PewDiePie）+ 第一个 bug 冷知识 + 程序员梗 |
| 2026-06-11 | 新增：消费品牌 AI 工具调研（瑞幸/喜茶/奈雪/星巴克/肯德基/麦当劳/海底捞等） |
| 2026-06-11 | 新增：2026 年 AI/半导体/芯片/股市新闻汇总（1-6月） |
| 2026-06-11 | 新增：2026 年顶会论文汇总（CVPR/ICLR/ICML/ACL/MLSys） |
| 2026-06-12 | 每日更新：科技新闻（芯片出口管制/苹果Siri+Gemini/Anthropic S-1/SpaceX IPO）、消费品牌AI（千问App Agent生态/美团LongCat-2.0/喜茶ChatBI）、股市行情、8篇arXiv新论文、四问深度分析、仪表盘重建 |
| 2026-06-13 | 每日更新：SpaceX史上最大IPO/苹果WWDC Siri+Gemini/Anthropic秘密S-1/英伟达SK海力士合作/华为昇腾获大厂订单/美国芯片出口新规、A股突破4000点、7篇arXiv新论文、4个GitHub热门仓库、8项四问深度分析、Excel+仪表盘重建 |
| 2026-06-14 | 补全：5个GitHub热门仓库（iptv-org/freeCodeCamp/pytest/swc/chatwoot）、6条科技新闻（韩国AI半导体/燧原科技IPO/WSTS预测）、股市行情、3项四问深度分析 |
| 2026-06-15 | 每日更新：韩国8000亿韩元AI半导体计划/国产AI芯片巨头IPO上会/WSTS预测半导体市场增长90%/蜜雪冰城进军纽约/瑞幸杀入茶饮赛道/千问App月活破亿、A股沪指4052点、7篇arXiv新论文（PP-OCRv6/SENTINEL/HYDRA-X等）、5个GitHub Trending仓库、8项四问深度分析、Excel+仪表盘重建 |
| 2026-06-18 | 每日更新：半导体股蒸发1.3万亿/英特尔18A至强6+/Claude Opus 4.8超GPT-5.5/Anthropic 9650亿融资/Gemini 3.5 Pro 200万Token、A股创业板+科创板双创历史新高(科创50+3.84%)/成交额破3万亿/美联储按兵不动、8篇arXiv论文(OmniAgent/ROGUE/BitsMoE等)、5个GitHub Trending仓库已fork(opencode/kilocode/dify/ragflow/goose)、6项四问深度分析 |
| 2026-06-22 | 每日更新：科创板第五套标准扩围AI大模型/智谱股价大涨40%市值破万亿港元/MiniMax涨20%/AI芯片需求拉动韩国出口、A股沪指大涨1.78%突破4160点/港股AI大模型股逆势走强、8篇arXiv论文(Agent自进化/偏见传播/跨设备恢复等)、4个GitHub Trending仓库(deer-flow/OpenMontage/palmier-pro/codebase-memory-mcp)、7项四问深度分析、Excel+仪表盘重建 |
| 2026-06-23 | 每日更新：AI飞轮驱动半导体上行周期/标普500首站7000点/英伟达11连涨/港股科技股回调、A股沪指4200点+0.90%/创业板4410+1.18%、8篇arXiv论文(LLM-as-Code/DiT-Reward/AdamW重尾噪声等)、3个GitHub Trending仓库(OpenClaw/Langflow/Open WebUI)、6项四问深度分析、Excel+仪表盘重建 |
| 2026-06-24 | 每日更新：美股芯片股重挫纳指跌2%/费城半导体暴跌8%/英伟达跌4%美光跌13%、AI安全赛道成稀缺投资(CrowdStrike八次创新高)、港股半导体逆势走强(华虹宏力+16%中芯国际+8%)、A股券商板块逆势飘红、霸王茶姬北美首店+冰淇淋vs蜜雪冰城竞争、8篇arXiv论文(OpenThoughts-Agent/World Models/可塑性丧失等)、3个GitHub仓库、6项四问深度分析 |
