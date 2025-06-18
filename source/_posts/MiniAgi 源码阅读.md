---
title: MiniAgi源码阅读笔记
date: 2025-05-03
tags: Agent
cover: ../pic/MINIAGI/封面.png
label: 
---

## spinner.py
在这个文件中定义了一个光标效果
~~~
def spinner_task(self):
    while self.busy:
        sys.stdout.write(next(self.spinner_generator))
        sys.stdout.flush() #强制立即刷新
        time.sleep(self.delay) # 定义帧率
        sys.stdout.write('\b') # 光标回退， 实现覆盖字符 
        sys.stdout.flush()
~~~
~~~
def __enter__(self): # 启动动画线程
    self.busy = True
    threading.Thread(target=self.spinner_task).start()

def __exit__(self, exception, value, tb): #停止动画
    self.busy = False
    time.sleep(self.delay)
    if exception is not None:
        return False
    return True
~~~

## exceptions.py
这个文件主要是用来捕获模型输出中的异常，例如格式不对，缺字段，非json等。然后将这个异常抛回给上层进行处理。继承了python内置的Exception类
```
class InvalidLLMResponseError(Exception):
    """Exception raised when the LLM response can't be parsed.
    
    Attributes:
        None
    """

```


## commond.py
在这个文件中规定了不同命令的思考链

### 库文件说明
 1. `import subprocess`
- **作用**：用于创建子进程，执行外部命令或脚本，并获取其输入输出结果。
- **典型用途**：
  - 调用系统命令（如 `ls`, `ping`, `gcc`, `python` 等）；
  - 执行外部程序或脚本（如 shell 脚本、批处理）；
  - 控制输入输出重定向。

 2. `from io import StringIO`
- **作用**：提供一个类 `StringIO`，它创建一个内存中的**字符串缓冲区**，可像文件一样读写。
- **典型用途**：
  - 在不涉及实际文件的情况下模拟文件操作；
  - 用于测试代码中涉及文件读写的部分；
  - 捕捉输出文本（通常与 `redirect_stdout` 配合使用）。

 3. `from contextlib import redirect_stdout`
- **作用**：上下文管理器，用于**临时将标准输出重定向到指定对象**（比如 `StringIO`）。
- **典型用途**：
  - 捕捉 `print()` 语句的输出；
  - 在测试或调试中查看函数内部输出；
  - 搭配 `StringIO` 捕获控制台输出为字符串处理。

 4. `from duckduckgo_search import DDGS`
- **作用**：导入 DuckDuckGo Search 的 Python 接口 `DDGS` 类，用于**调用 DuckDuckGo 的搜索功能**。
- **典型用途**：
  - 用代码直接进行 DuckDuckGo 搜索并获取结果；
  - 抓取网页搜索摘要、链接、图像等；
  - 用于构建搜索引擎接口或信息爬取工具。

### class类说明
在execute_commond中首先将命令进行分发
```
if command == "memorize_thoughts":
    调用 Commands.memorize_thoughts(arg)
elif command == "execute_python":
    调用 Commands.execute_python(arg)
...
else:
    返回 Unknown command{commond}
如果过程中出现异常，返回异常信息
```

然后分别定义各个函数内容

## miniagi.py

### prompt设计

关于prompt的具体设计原则，会写另外一篇博客进行说明
在MiniAgi项目中prompt的设计是这样的
设计中融入了思维链、少样本提示，并且强调了自我一致性。同时，在prompt的设计中加入了自我批评*CRITIC_PROMPT*，以及记忆重整*HISTORY_SUMMARY_HINT*等。具体如下

---
 1. 角色设定（Role Conditioning）
~~~
f"You are an autonomous agent running on {operating_system}."
~~~

明确模型的“身份”：你是运行在某操作系统上的自主代理智能体；
通过设定操作系统，有利于后续与 Shell 命令、文件路径等交互时保持一致（如 Linux vs Windows）。


2. 目标导向任务（Objective Conditioning）

~~~
OBJECTIVE: {objective} (e.g. "Find a recipe for chocolate chip cookies")
~~~
- 为当前任务设定一个清晰目标，使模型行为聚焦；
- 模仿人类代理行为，把目标当成“长期任务”，以实现规划式思维。



3. 历史上下文注入（Context）
~~~
Previous steps: {context}
~~~

- 引入以往已执行的动作/观察结果，作为“记忆”或状态追踪；
- 支持多步推理和上下文保持，是链式思维（Chain-of-Thought）的关键。


4. 明确命令集（命令语言接口设计）



- 定义一个有限状态机风格的 API 接口，明确智能体能执行的动作范围；
- 强制每一步只能执行一个命令，避免无控制的自然语言混乱；
- 命令覆盖典型任务：记忆、推理、代码执行、数据处理、与用户对话、终止。


 5. 明确格式约束（动作语法模板）

~~~
<r>[YOUR_REASONING]</r><c>[COMMAND]</c>
[ARGUMENT]
~~~

- `<r>`：模型的推理或动机说明；
- `<c>`：结构化命令名称（对应预定义命令集）；
- `[ARGUMENT]`：命令参数；
- 该格式是构化动作标注，利于解析、监督、记录、回放等；
- 防止输出中出现自然语言噪声或模糊行为。


 6. 行为限制与安全提示


- 不要重复命令
- 不要链式多个命令
- Python 要以 print 输出结尾
- process_data / ingest_data 只能处理单文件
- 不搜索 GPT 已知知识


- **保证行为唯一性、可解释性、可控性**；
- 限制模型可能的幻觉或冗余行为；
- 强化对命令执行前提条件的检查（如输出格式约束）。

 7. 示例示范（Few-shot Prompting）

~~~
<r>Think about skills and interests...</r><c>memorize_thoughts</c>

<r>Search for websites...</r><c>web_search</c>
~~~
- 提供多个风格统一、结构良好的**行为范例**；
- 用作 few-shot learning 的提示模板，让模型模仿人类代理行为；
- 示例覆盖了多种命令使用方式、输入格式、常见应用。
---


### MiniAgi类
```python
class MiniAGI:
    """
    表示一个自主智能体（Agent）类。

    属性（Attributes）定义了 agent 的各种组件和运行状态。
    """

    def __init__( # 参数初始化列表
        self,
        agent_model: str,
        summarizer_model: str,
        objective: str,
        max_context_size: int,
        max_memory_item_size: int,
        debug: bool = False
    ):
        """
        构造函数：创建 MiniAGI 实例，初始化内部模型和参数。
        """

        # 初始化用于生成行为的主模型
        self.agent = ThinkGPT(
            model_name=agent_model,
            request_timeout=600,
            verbose=False
        )

        # 初始化用于生成摘要的模型
        self.summarizer = ThinkGPT(
            model_name=summarizer_model,
            request_timeout=600,
            verbose=False
        )

        # 保存目标、内存限制、是否调试等配置参数
        self.objective = objective
        self.max_context_size = max_context_size
        self.max_memory_item_size = max_memory_item_size
        self.debug = debug

        # 以下是状态相关的字符串属性，初始设为空
        self.summarized_history = ""
        self.criticism = ""
        self.thought = ""
        self.proposed_command = ""
        self.proposed_arg = ""

        # 使用 tiktoken 获取模型的 tokenizer 编码器
        self.encoding = tiktoken.encoding_for_model(self.agent.model_name)

    def __update_memory(self, action: str, observation: str, update_summary: bool = True):
        """
        内部方法：根据行动和观察结果更新记忆。

        如果 observation 太长，会先进行摘要处理。
        """
        # 如果 observation 超过允许大小，进行摘要
        if len(self.encoding.encode(observation)) > self.max_memory_item_size:
            observation = self.summarizer.chunked_summarize(
                observation, self.max_memory_item_size,
                instruction_hint=OBSERVATION_SUMMARY_HINT
            )

        # 构造新记忆格式
        if "memorize_thoughts" in action:
            new_memory = f"ACTION:\nmemorize_thoughts\nTHOUGHTS:\n{observation}\n"
        else:
            new_memory = f"ACTION:\n{action}\nRESULT:\n{observation}\n"

        # 如果需要更新摘要，调用 summarizer 的 summarize 方法
        if update_summary:
            self.summarized_history = self.summarizer.summarize(
                f"Current summary:\n{self.summarized_history}\nAdd to summary:\n{new_memory}",
                self.max_memory_item_size,
                instruction_hint=HISTORY_SUMMARY_HINT
            )

        # 将新记忆交由 agent 存储
        self.agent.memorize(new_memory)

    def __get_context(self) -> str:
        """
        内部方法：构造 agent 当前的上下文字符串。

        上下文包括摘要、最近的行为和批评。
        """
        summary_len = len(self.encoding.encode(self.summarized_history))
        criticism_len = len(self.encoding.encode(self.criticism)) if self.criticism else 0

        # 从 agent 中获取最多能容纳的最近记忆片段
        action_buffer = "\n".join(
            self.agent.remember(
                limit=32,
                sort_by_order=True,
                max_tokens=self.max_context_size - summary_len - criticism_len
            )
        )

        # 构建最终上下文字符串
        return f"SUMMARY\n{self.summarized_history}\nPREV ACTIONS:\n{action_buffer}\n{self.criticism}"

    def criticize(self) -> str:
        """
        调用模型对 agent 最近的行为进行批评。
        """
        context = self.__get_context()
        self.criticism = self.agent.predict(
            prompt=CRITIC_PROMPT.format(context=context, objective=self.objective)
        )
        return self.criticism

    def think(self):
        """
        调用模型进行推理，生成下一步操作计划。
        """

        context = self.__get_context()

        if self.debug:
            print(context)

        # 基于 prompt 和上下文生成原始响应
        response_text = self.agent.predict(
            prompt=PROMPT.format(context=context, objective=self.objective)
        )

        if self.debug:
            print(f"RAW RESPONSE:\n{response_text}")

        # 使用正则表达式提取 <r>思考</r><c>命令</c>arg
        PATTERN = r'^<r>(.*?)</r><c>(.*?)</c>\n*(.*)$'

        try:
            match = re.search(PATTERN, response_text, flags=re.DOTALL | re.MULTILINE)
            _thought = match[1]
            _command = match[2]
            _arg = match[3]
        except Exception as exc:
            raise InvalidLLMResponseError from exc

        _arg = _arg.replace("```", "")  # 去除可能的 markdown 格式符号

        # 保存模型推理结果
        self.thought = _thought
        self.proposed_command = _command
        self.proposed_arg = _arg

    def read_mind(self) -> tuple:
        """
        获取 agent 最近的思考、命令和参数。
        """
        _arg = self.proposed_arg.replace("\n", "\\n") if len(self.proposed_arg) < 64\
            else f"{self.proposed_arg[:64]}...".replace("\n", "\\n")

        return (self.thought, self.proposed_command, _arg)

    @staticmethod
    def __get_url_or_file(_arg: str) -> str:
        """
        根据参数读取 URL 或本地文件内容。
        """
        if _arg.startswith("http://") or _arg.startswith("https://"):
            with urlopen(_arg) as response:
                html = response.read()
            data = BeautifulSoup(html, features="lxml").get_text()
        else:
            with open(_arg, "r") as file:
                data = file.read()

        return data

    def __process_data(self, _arg: str) -> str:
        """
        对 URL 或文件进行处理，格式为：prompt|url或文件路径
        """
        args = _arg.split("|")
        if len(args) == 1:
            return "Invalid command. The correct format is: prompt|file or url"
        if len(args) > 2:
            return "Cannot process multiple input files or URLs. Process one at a time."

        prompt, __arg = args

        try:
            input_data = self.__get_url_or_file(__arg)
        except urllib.error.URLError as e:
            return f"Error: {str(e)}"
        except OSError as e:
            return f"Error: {str(e)}"

        if len(self.encoding.encode(input_data)) > self.max_context_size:
            input_data = self.summarizer.chunked_summarize(
                input_data, self.max_context_size,
                instruction_hint=OBSERVATION_SUMMARY_HINT
            )

        return self.agent.predict(
            prompt=f"{RETRIEVAL_PROMPT}\n{prompt}\nINPUT DATA:\n{input_data}"
        )

    def __ingest_data(self, _arg: str) -> str:
        """
        只读取 URL 或文件内容（不进行指令解析），返回文本或摘要。
        """
        try:
            data = self.__get_url_or_file(_arg)
        except urllib.error.URLError as e:
            return f"Error: {str(e)}"
        except OSError as e:
            return f"Error: {str(e)}"

        if len(self.encoding.encode(data)) > self.max_memory_item_size:
            data = self.summarizer.chunked_summarize(
                data


```
