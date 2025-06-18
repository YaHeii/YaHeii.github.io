from datetime import time
from openai import OpenAI

API_KEY = "4a13c79e-9e69-4238-b686-41fe6584f86a"  # 请填入你的 API Key
client = OpenAI(api_key=API_KEY, base_url="https://ark.cn-beijing.volces.com/api/v3")

import os
import time # 需要导入 time 模块


# 呼叫R1模型
def call_deepseek_r1(prompt: str, max_retries: int = 3) -> str:
    if client is None:
        print("错误: API客户端未初始化。无法调用API。")
        return "Error: API client not initialized."

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-r1-250120", # 请确认模型名称正确
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in call_deepseek_r1 (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # 等待5秒后重试
            else:
                print(f"达到最大重试次数 ({max_retries})，放弃处理该Prompt。")
                # 可以选择在这里返回一个错误标识，或者抛出异常
                # raise # 如果希望调用者处理最终的错误
                return f"处理失败：达到最大重试次数，错误信息: {e}" # 返回错误信息

def process_directory(root_dir):
    """
    遍历指定根目录及其子目录，处理所有 .md 文件，并生成新的输出文件。

    Args:
        root_dir (str): 开始遍历的根目录路径。
    """
    if not os.path.isdir(root_dir):
        print(f"错误：指定的根目录不存在或不是一个目录: {root_dir}")
        return

    print(f"开始处理目录及其子目录，根目录: {root_dir}")

    # os.walk 会遍历 root_dir 下的所有目录和文件
    for dirpath, dirnames, filenames in os.walk(root_dir):
        print(f"进入目录: {dirpath}")

        # 遍历当前目录下的所有文件
        for filename in filenames:
            # 检查文件是否是 .md 文件
            # 同时排除我们即将生成的新文件，避免重复处理
            if filename.endswith(".md") and not filename.endswith("_output.md"):
                input_filename = filename
                input_path = os.path.join(dirpath, input_filename)

                # 构建输出文件路径
                # 在原文件名前加上后缀，保留 .md 扩展名
                name, ext = os.path.splitext(input_filename) # 分割文件名和扩展名
                output_filename = f"{name}_r1_output{ext}" # 例如：原文件 `doc.md` -> 输出 `doc_r1_output.md`
                output_path = os.path.join(dirpath, output_filename)

                # 可选：检查输出文件是否已存在，如果存在则跳过处理该输入文件
                # 如果希望每次都重新生成，可以注释掉这部分
                # if os.path.exists(output_path):
                #     print(f"  输出文件已存在，跳过处理输入文件: {input_path}")
                #     continue

                print(f"  发现需要处理的 .md 文件: {input_path}")

                try:
                    # 读取输入文件内容
                    with open(input_path, "r", encoding="utf-8") as f:
                        input_content = f.read().strip()

                    # 构建发送给API的Prompt
                    # 将文件内容与固定的指令拼接起来
                    prompt_instructions = '''

你将接收一份用户提供的markdown格式的C++学习博客草稿。这份草稿可能存在结构不清晰、内容不完整、缺乏标题和排版不佳等问题。你的任务是按照以下详细步骤，对草稿进行分析、完善和格式化，最终输出一份结构清晰、内容准确、排版美观的markdown格式博客文章。

请严格按照以下步骤执行，并使用markdown格式输出最终结果。**特别注意：任何数学公式或科学符号请使用LaTeX格式，并用'$'（行内公式）或'$$'（块级公式）包裹。除了公式，请勿在其他地方使用LaTeX语法。**

**COT (Chain of Thought) 执行步骤：**

1.  **第一步：结构分析与概述**
    * 首先，请对提供的markdown草稿进行整体结构分析。描述当前内容的组织方式（即使是混乱的），尝试理解作者当前想要表达的核心主题和大致的学习路径（如果能看出来的话）。
    * 概述当前草稿的撰写思路和核心内容。
    * 列出草稿当前的、大致的大纲（即使是扁平或零散的结构）。这一步旨在展示你理解了原始输入的内容布局。

2.  **第二步：知识性评估**
    * 仔细审阅内容，指出其中存在的知识性错误（包括概念不清、代码错误等）。请具体说明错误点。
    * 评估知识结构的完整性。指出逻辑不连贯或遗漏的关键知识点。

3.  **第三步：内容完善与分节**
    * 基于上述分析，对文章内容进行完善和补充，填补知识空白，修正错误。
    * 将完善后的内容合理地划分成不同的章节，使其结构清晰。

4.  **第四步：添加标题**
    * 为每一个划分出的章节起一个恰当、概括性强的标题。

5.  **第五步：生成最终Markdown**
    * 将完善后的、带有标题的分节内容整合生成最终的markdown格式输出。请确保排版整洁，符合markdown规范，且公式使用LaTeX格式。

请按照以上步骤，逐步分析、完善并输出最终的markdown博客文章。
                    '''
                    prompt = input_content + prompt_instructions

                    # 调用 DeepSeek-R1 API
                    print(f"调用 DeepSeek-R1 处理文件: {input_filename}")
                    api_response_content = call_deepseek_r1(prompt)

                    # 写入API返回的结果到新的文件
                    if api_response_content.startswith("处理失败"):
                        print(f"文件 {input_filename} 处理失败，结果不写入文件。")
                    else:
                         with open(output_path, "w", encoding="utf-8") as f:
                            f.write(api_response_content)
                         print(f"    处理完成，结果已保存到: {output_path}")

                except Exception as e:
                    # 捕获文件读写等异常
                    print(f"  处理文件 {input_path} 时发生意外错误: {e}")

# --- 主执行块 ---
if __name__ == "__main__":
    # 定义您希望开始处理的根目录
    # 例如：处理当前脚本所在的目录及其子目录，可以使用 '.'
    # 例如：处理指定路径下的目录，可以使用 '/path/to/your/root/directory'
    starting_directory = '.' # 将 '.' 替换为您的实际根目录路径

    process_directory(starting_directory)
    print("所有指定目录下的 .md 文件处理完成。")