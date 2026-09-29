---
name: knowledge-agent-playbook
description: Use when building, running or auditing a personal/AI-agent knowledge base — screening external material before citing it, reading multi-part series completely, turning an archive into a queryable graph, and keeping long task chains from silently dropping work. Five practices, each with the operational test that makes it enforced rather than aspirational.
---

# 一个称职知识智能体的五本武功秘笈 · knowledge-agent-playbook

## 先摆关键判据（别先看方法）

**知识库的价值，取决于哪一件事：是"存了多少"，还是"每一条能不能回溯"。**

* 如果答案是**前者** —— **一个灌内容的爬虫就够了。**
* 如果答案是**后者** —— **这件事的性质就变了：做的不是内容收集，而是证据管理。**

⭐ 本文五个方法**只对后者有意义**。

---

## 五个方法各防一类事故

| 方法 | 它防什么 |
|:--|:--|
| **一、引用驱动验证** | 把**转述**当事实 |
| **二、系列化读取** | 把**抽样**当全貌 |
| **三、延伸阅读成图** | 把**堆料**当知识 |
| **四、持续检查机制** | 把**中断**当结束 |
| **五、双层信息过滤** | 把"**引用是真的**"当成"**可以放心用**" |

⭐⭐ **共同点**：**把判断从"依赖临场记忆"搬到"机械约束"上。**

> 不靠"记得核"，靠**四件必查 ＋ 出处等级写进档**；
> 不靠"尽量读全"，靠**三个计数分开记（总／取回／通读）**；
> 不靠"应该连起来想"，靠**索引强制归属 ＋ 查重三步**；
> 不靠"下决心不半途停"，靠**待办落盘 ＋ 守卫拒绝执行 ＋ 定时审计出数**；
> 不靠"自己注意点"，靠**位置感知的预扫 ＋ 成对判据**。

---

## 遇到什么情况用哪一本

| 你现在的处境 | 用哪个 | 去哪读 |
|:--|:--|:--|
| 拿到一篇二手材料，准备引用 | **方法一** | `references/method-1-citation-verification.md` |
| 手里这篇像是连载里的第 10 集 | **方法二** | `references/method-2-series-reading.md` |
| 库里东西越来越多，但说不清"几个来源指向同一判断" | **方法三** | `references/method-3-knowledge-graph.md` |
| 长任务链总是跑到一半就"收尾" | **方法四** | `references/method-4-continuous-checking.md` |
| 引用核过是真的，但总觉得哪里不对 | **方法五** | `references/method-5-dual-layer-filter.md` |
| 要判断**一个号**值不值得长期追 | **方法五 §5.3** | 同上 |
| 想找速查表 | — | `references/quick-reference.md` |

---

## 每个方法的最小必做动作

### 方法一（引用验证）
⭐ **凡带"有出处的机构数字"，当场回原文核四件**：
**发布时间 / 样本性质与规模 / 数据截止年份 / 一手机构页。**
⭐ **等级与"未核"写进档**，⛔ 不是留在记忆里。

### 方法二（系列化读取）
⭐ **先拉全系列再下判断**；默认 **10 篇上限**；⭐ **"总／取回／通读"三个计数写进档**。

### 方法三（知识图谱）
⭐ **索引归属强制**（分区是必填参数，⛔ 不给"追加到末尾"模式）＋ ⭐ **查重三步**。

### 方法四（持续检查）
⭐ **待办落盘 ＋ 守卫拦截 ＋ 定时审计**；落地顺序 **③→②→④→①**。
⭐ **守卫必须"拒绝执行"，不能"打印结论"。**

### 方法五（双层过滤）
⭐ 先跑预扫 `python3 scripts/scan.py <file>`，⭐ **然后人工读到结尾** —— **两条都过才算过**。
⭐ **两把尺子分开量**：**归属归事实，疗效归证据**。

---

## ⛔ 纪律（写死，跨五个方法通用）

1. ⛔ **未核的数字一律不许引用**；无出处数字一律标「**未核**」。
2. ⛔ **不用动机否定事实**，也不用"引用是真的"洗白动机。
3. ⛔ **不拿频次当可信度** —— "出现次数多"只是"投喂得多"。
4. ⛔ **不拿阅读量、更新频率、排版当判据**。
5. ⛔ **"已取回" ≠ "已读完"** —— 说不清三个数，别说"读完了"。
6. ⚠️ **验收要盯后果，不盯格式**；**撤回配置 ≠ 撤回生效**。
7. ⚠️ **工具会有漏报也会误报**，产出是**初筛**，终审归人。

---

## ⭐ 最贵的一句话（整套的地基）

> **一个机制的"通过测试"，不等于它"做对了事"。要盯后果，不要盯格式。**

---

## 支持文件

```
.
├── README.md
├── SKILL.md                                  本文件
├── scripts/
│   └── scan.py                               方法五的扫描器（零依赖）
├── references/
│   ├── quick-reference.md                    ⭐ 五本速查表
│   ├── method-1-citation-verification.md
│   ├── method-2-series-reading.md
│   ├── method-3-knowledge-graph.md
│   ├── method-4-continuous-checking.md
│   └── method-5-dual-layer-filter.md
└── examples/
    └── sample_article.txt
```
