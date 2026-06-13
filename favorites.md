# 我的开发收藏夹

> 每日更新的效率小技巧 & 热门开源仓库收藏  
> 最后更新：2026-06-13

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
