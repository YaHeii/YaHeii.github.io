---
title: agent学习
date: 2025-04-28
tags: agent
cover: ../pic/agent/agent.png
label: 最近在学习大模型相关的知识，大致的学习路线就是，首先从做一个agent开始起步，然后再使用LLaMA等开源大模型，做一个自己的大模型，然后再考虑多模型协同的工作。
---


## Agent工作逻辑

以AutoGPT为例子，记录一下Agent的工作逻辑

### 1. 什么是像 AutoGPT 这样的 Agent 框架？

它们是**高级自动化系统**，基本逻辑是：

- 不是简单「单轮提问-回答」
- 而是**根据任务自己制定计划**，**分步行动**，**多轮决策**，直到任务完成。普通的大模型是通过一轮轮的问答来实现最终的任务的但是创建一个合适的Agent可以实现自己想目标，自己想策略，自己执行，自己检查。

###  2. AutoGPT类 Agent 的运行框架核心步骤

 它们基本遵循下面这个 **循环逻辑**：
   
```
(1) 接收目标
用户给一个高层目标，比如：
- "写一份关于人工智能历史的详细报告，并生成成 Word 文档。"


 (2) 自主规划
Agent自己思考出**计划 (Plan)**，比如：

- 查询人工智能历史资料
- 按时间线整理事件
- 写成条理清晰的段落
- 格式化成Word文档


 (3) 行动(Action)
Agent根据计划，开始一步步执行：
- 调用搜索引擎 API
- 分析网页内容
- 写文档
- 保存文件

每一步都是自己调用工具、处理结果！


(4) 观察(Observation)
每次行动后，会自己**检查行动结果**：
- 成功了？继续下一步
- 失败了？重新想方法
- 信息不够？再去找资料

(5) 决策(Thinking)
根据观察结果，决定：
- 修改计划
- 补充信息
- 结束任务

**这就是所谓的：自主决策、自主行动循环。** 
```

###  3. 它们内部通常包括哪些模块？

| 模块 | 功能 |
|:--|:--|
| Memory（记忆） | 记录任务过程，避免忘记之前做过什么 |
| Planning（规划） | 自动分解任务成小步骤 |
| Tools（工具链） | 能用的外部接口（如Web搜索、文件系统、数据库等） |
| Reasoning（推理） | 分析当前状况，决定下一步怎么做 |
| Critic（自我评估） | 检查结果，判断是否需要修正 |

---
###  4. 模型的参数设置
1. Temparature 
   简单来说，temperature 的参数值越小，模型就会返回越确定的一个结果。如果调高该参数值，大语言模型可能会返回更随机的结果，也就是说这可能会带来更多样化或更具创造性的产出。（调小temperature）实质上，你是在增加其他可能的 token 的权重。在实际应用方面，对于质量保障（QA）等任务，我们可以设置更低的 temperature 值，以促使模型基于事实返回更真实和简洁的结果。 对于诗歌生成或其他创造性任务，适度地调高 temperature 参数值可能会更好。
2. top_p 
    同样，使用 top_p（与 temperature 一起称为核采样（nucleus sampling）的技术），可以用来控制模型返回结果的确定性。如果你需要准确和事实的答案，就把参数值调低。如果你在寻找更多样化的响应，可以将其值调高点。

    使用Top P意味着只有词元集合（tokens）中包含top_p概率质量的才会被考虑用于响应，因此较低的top_p值会选择最有信心的响应。这意味着较高的top_p值将使模型考虑更多可能的词语，包括不太可能的词语，从而导致更多样化的输出。

    一般建议是改变 Temperature 和 Top P 其中一个参数就行，不用两个都调整。
3. MAX Length 
   您可以通过调整 max length 来控制大模型生成的 token 数。指定 Max Length 有助于防止大模型生成冗长或不相关的响应并控制成本。
4. stop sequence 
   这同样是一种控制模型响应长度和结构的另外一种方法
5. Frequency Penalty
   是对下一个生成的token进行惩罚，控制重复数量。
6. Presence Penalty
   presence penalty 也是对重复的 token 施加惩罚，但与 frequency penalty 不同的是，惩罚对于所有重复 token 都是相同的。出现两次的 token 和出现 10 次的 token 会受到相同的惩罚。 此设置可防止模型在响应中过于频繁地生成重复的词。 如果您希望模型生成多样化或创造性的文本，您可以设置更高的 presence penalty，如果您希望模型生成更专注的内容，您可以设置更低的 presence penalty。
###  5. 具体以 AutoGPT 举例（运行时流程）

```plaintext
1. 用户输入：我要了解马斯克的一生

2. AutoGPT:
    - 想一想：需要做哪些事？
    - 计划出步骤：
        ① 搜索马斯克的生平资料
        ② 按时间整理重要事件
        ③ 生成简要介绍文档

3. AutoGPT:
    - 开始第1步：调用搜索API
    - 得到网页结果

4. AutoGPT:
    - 第2步：分析网页
    - 挑出马斯克生平重要事件

5. AutoGPT:
    - 第3步：组织成文档
    - 保存成文本文件

6. AutoGPT:
    - 任务完成，提示用户
```

**这一整套都是 Agent 自己思考-执行的！**



### 一些典型Agent框架

| 项目 | 特点 | 地址 |
|:--|:--|:--|
| **AutoGPT** | 早期爆火，超全面，但偏重实验 | https://github.com/Torantulino/Auto-GPT |
| **BabyAGI** | 极简Agent，只要几百行代码，便于学习 | https://github.com/yoheinakajima/babyagi |
| **CrewAI** | 多Agent协作系统（模拟一个小团队） | https://github.com/joaomdmoura/crewAI |
| **LangChain Agent** | LangChain框架内置的Agent模块，商业项目多用 | https://docs.langchain.com/docs/modules/



