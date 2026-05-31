"""
当模型为API时，则启动调用
"""
import os
import time
import requests
import json
from typing import Union
from transformers import AutoTokenizer

class APIAgent:

    def __init__(self,
        model_name: str = "qwen",
        api_address: str = None,
        tokenizer = None,
        info = None,
    ):
        # api_address 示例：http://33.236.12.2:8081
        self.model_name = model_name
        self.api_address = api_address
        self.tokenizer = tokenizer
        self.info = info

        self.is_new_template = True if "new_template" in self.model_name else False
        print("This model is based on {} template".format("new" if self.is_new_template else "old"))

    def generate(self,
        prompt: str,
        duplicate_n: int = 1,
        max_tokens=32768 + 16384,
        use_message=True,
    ):

        if use_message:

            message = [
                # {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]

            if "longcat-flash-thinking" in self.model_name.lower():
                if self.is_new_template:
                    # prompt = self.tokenizer.apply_chat_template(message, tokenize=False)
                    prompt = "<longcat_user>" + prompt + " /think_on <longcat_assistant>"
                else:
                    prompt = "[Round 0] USER:" + prompt + " /think_on ASSISTANT:"
            else:
                prompt = self.tokenizer.apply_chat_template(message, tokenize=False)



        all_responses = list()

        for ei in range(duplicate_n):
            if self.info is not None:
                print(f"{self.info} - api calling {self.api_address}, summary times ({ei + 1} | {duplicate_n})")
            else:
                print(f"api calling {self.api_address}, summary times ({ei + 1} | {duplicate_n})")

            data = {
                "prompt": prompt,
                # "messages": message,
                "temperature": 1.0,
                "max_new_tokens": max_tokens,
                "repetition_penalty": 1.0,
                "top_k": -1,
                "top_p": 0.95,
                # "model": self.model_name,
                # "random_seed": 0,
                # "logprobs": 2,
            }

            data_params = {
                "text": json.dumps(data)
            }

            # 发送 POST 请求
            retry_times = 5
            while retry_times > 0:
                try:
                    response = requests.post(self.api_address, json=data, timeout=(5, 600))
                    # response = requests.get(url, params=data_params)
                    response_data = response.json()
                    # print(response_data)
                    completions = response_data["completions"]
                    print("completions[0].keys()=", completions[0].keys())
                    responses = [completion["text"] for completion in completions]
                    break
                except:
                    responses = []
                    print(f"Time out. Retrying (remain {retry_times} times)")
                    retry_times -= 1

            all_responses.extend(responses)
        return all_responses


def read_json(path):
    with open(path, "r", encoding="utf-8") as fr:
        examples = json.load(fr)
    return examples

def save_json(path, example):
    with open(path, "w", encoding="utf-8") as fw:
        json.dump(example, fw)


def prompting(query, parallel_reason_content_list, language="en"):

#     prompt = """
# You are a great reasoner.
# Here is a problem, and multiple thinkers attempt to give their thought processes independently.
# Each thinker has written its own thought process towards the final answer. Each thinker is encouraged to take the other thinkers’ progress into account to reach the final answer.

# # ====== Problem ======
# {problem}
# # ====== Problem End ======

# # ====== Thinkers Thought Process ======
# {response_prompt}
# # ====== Thinkers Thought Process End ======

# Look at the above problem and thought process from each thinker, summarize from these thought processes and finally give your answer.
# Summarize their thinking on the problem and try to summarize the thinking of these thinkers. Analyze the differences in thinking between these thinkers and try to analyze and give the correct answer.
# Note:
# - It is generally believed that when most thinkers get the similar answer, the answer may be correct. But you can't do it so superficially, because the correct answer may come from very few thinkers, or even no thinker gives the correct answer. For this reason, when you summarizing, you NEED adhere to the principles of professionalism and critical thinking, carefully identify these thought processes, and give a summary and final answer.
# - If you realize that none of these thinkers have answered correctly, you can even learn from the wrong experiences in the thought process of these thinkers and re-think the given problem to give the answer you think is most correct.
# - Please DO NOT just solve the given problem independently like other thinkers, but summarize the thought process of all thinkers. In other words, you need to give the summary first, and then give the final answer, you can re-think this problem only if you realize that none of these thinkers have answered correctly.
# For the output format of your final answer after the summary, you should follow the similar format with thinkers:
# - If the problem is mathematics or STEM and most thinkers have put the answer within boxed, your final answer after the summary should within boxed too.
# - If the problem is code contest and most thinkers have put the result code within a block like "```", your final answer should also within the block.
# """.strip()
    if language == "en":
        prompt = """
You are a professional reasoner and AI assistant.

Here is a user query, and multiple thinkers attempt to give their thought processes independently. Each thinker has written its own thought response to answer the given query.

# ====== Query Start ======
{problem}
# ====== Query End ======

# ====== Thinkers Thought Response Start ======
{response_prompt}
# ====== Thinkers Thought Response End ======

Look at the above query and thought response from each thinker, your task is to carefully analyze the thought processes of different thinkers, and ultimately formulate a response that can answer a given query.
Note:
**1** You must follow the requirements and instructions given in the query. The styles and patterns from the resposnes derived from all thinkers output responses can be used as a reference.
**2** It is generally believed that when most thinkers get the similar answer, the answer may be correct. But you can't do it so superficially, because the correct answer may come from very few thinkers, or even no thinker gives the correct answer. For this reason, when you analyzing, you NEED adhere to the principles of professionalism and critical thinking, carefully identify these thought processes, and give the final answer.
**3** If you realize that none of these thinkers have answered correctly, you can even learn from the wrong experiences in the thought process of these thinkers and re-think the given problem to give the answer you think is most correct.

Before your analysis, you NEED to first determine the question type corresponding to the current query, and then analyze it accordingly.
- If it's a simple casual conversation, generally speaking, you don't need too much complex analysis and thought. You can choose the best response from these thinkers, of course, you can also refine or summarize an optimal reply based on these responses.
- If it's a complex reasoning task, such as logical reasoning, mathematical reasoning, coding competitions, or common-sense reasoning problems, etc., you NNED to carefully analyze the thinkers' responses. After analysis, you need to provide a solution that can resolve the query.
- If none of the above applies, you can decide whether you need to analyze the situation carefully based on the actual circumstances. If you are really unsure, you can choose one of these thinkers' responses as a backup plan, but it should be emphasized that this is a last resort and should not be used as a general practice.

Last but not least:
- Please note that you DO NOT simply concate together or list all the thinkers' outputs. Your role and goal are the same as these thinkers, i.e., ultimately answer the query. The difference between you and these thinkers is that you can conduct some analysis based on their responses, summarize or select the best response for the user.
- You need to consider language consistency. Your analysis and final output responses must be consistent with the language type of the given query. For example, if the query and each thinker are primarily in Chinese, then your analysis and responses must also be primarily in Chinese, too. If the query and each thinker are primarily in English, then your analysis and responses must also be primarily in English, too. By the way, if the language of the query and each thinker‘s response is inconsistent, then you MUST maintain consistency with the language type of the given query.
- Your final output response DO NOT contain any analysis of these thinkers. Your final response must be a response to the given query, must follow the requirements and instructions in the query, and the style and format of the output must be consistent with those of the thinkers.
""".strip()

    elif language == "cn":
        prompt = """
你是一位专业的人工智能助手。

这里有一个用户输入的查询Query，多位Thinker尝试独立地给出他们的回复内容。每位Thinker都编写了自己的思考答案来回答给定的Query。

# ====== 以下是Query ======
{problem}
# ====== 以上是Query ======

# ====== 以下是Thinker回答内容 ======
{response_prompt}
# ====== 以上是Thinker回答内容 ======

请根据以上的Query以及每位Thinker的回答内容，你的任务是仔细分析不同Thinker的思考过程，并最终形成一个能够回答给定Query的回复。

注意：
**1** 你必须遵循Query中给出的要求和说明，最终回复的形式和格式需要与所有Thinker保持一致。
**2** 一般情况下，当大多数Thinker得到相似的答案时，该答案可能是合理的，但你不能如此肤浅地进行分析，因为正确的答案有时候也会出现在极少数的Thinker，甚至可能根本没有Thinker能够给出正确答案。因此，在分析时，你需要遵循专业精神和批判性思维的原则，仔细识别这些Thinker的思考过程，并给出最终答案。
**3** 如果你发现这些Thinker都没有给出正确答案，你甚至可以从他们错误的思考过程中吸取教训，重新思考给定的Query，从而给出你认为最合理的答案。

在进行分析之前，你需要先确定当前Query对应的问题类型，然后据此进行分析。
- 如果是简单的日常对话或闲聊，一般来说，你不需要进行太多复杂的分析和思考。你可以从这些Thinker中选择最佳答案，当然，你也可以根据这些答案提炼或总结出一个最佳回复。
- 如果是复杂的推理任务，例如逻辑推理、数学推理、编程竞赛或常识推理题等，你需要仔细分析Thinker的回答。分析之后，你需要提供一个能够解决对应Query的方案。
- 如果以上情况都不适用，你可以根据实际情况决定是否需要仔细分析。如果你实在难以分析或回答，你可以选择其中一个Thinker的回答作为备选方案，但需要强调的是，这只是最后的手段，不应作为常规做法。

最后需要再次强调：
- 请注意，你不能简单地将所有Thinker的输出结果拼接在一起或列出。你的角色和目标与这些Thinker是相同的，即最终回答Query。你与这些Thinker的区别在于，你可以根据他们的回答进行一些分析，总结或选择最佳答案供用户参考。
- 你需要考虑语言一致性。你的分析和最终输出的答案必须与给定Query的语言类型保持一致。例如，如果Query和每位Thinker的回复主要使用中文，那么你的分析和回答也必须主要使用中文。如果Query和每位Thinker的回复主要使用英文，那么你的分析和回答也必须主要使用英文。另外，如果问题和每位Thinker的回答使用的语言不一致，那么你必须与给定问题的语言类型保持一致。
- 你的最终回答不得包含对这些Thinker的任何分析。你的最终回答必须是对Query的回答，必须遵循Query中涉及到的一些要求和说明，并且输出的风格和格式必须与Thinker的风格和格式保持一致。
""".strip()

    response_prompt = ""
    for ei, response in enumerate(parallel_reason_content_list):
        response_prompt += "# ----- Thinker #{} -----\n\n{}\n\n".format(ei + 1, response)
    prompt = prompt.replace("{problem}", query).replace("{response_prompt}", response_prompt)

    # prompt = "<|im_start|>user:\n{prompt}\n<|im_end|>\n\n<|im_start|>assistant:".format(prompt=prompt)

    return prompt


if __name__ == "__main__":

    # tokenizer = AutoTokenizer.from_pretrained("/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/pre-trained-lm/LongCat-Flash-Thinking-new_template_oss_62w")
    tokenizer = AutoTokenizer.from_pretrained("/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/pre-trained-lm/LongCat-Flash-Thinking-new_template-1206")
    # tokenizer = AutoTokenizer.from_pretrained("/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/pre-trained-lm/LongCat-Flash-Thinking-old_template")
    # tokenizer = AutoTokenizer.from_pretrained("/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/pre-trained-lm/DeepSeek-R1-Distill-Qwen-7B")


    # api_address = "http://33.236.0.14:8080" # flash-thinking final merge
    api_address = "http://33.235.9.48:8080"



    model_name = "longcat-flash-thinking_new_template"
    # model_name = "closeai-openai-claude-sonnet-4-5-20250929-thinking"
    # model_name = "gpt-5-high"
    # model_name = "grok4"
    # model_name = "gemini3"
    # model_name = "deepseek-v3.2"
    # model_name = "glm4.6"
    # model_name = "kimi-k2-thinking"


    use_message = True
    # use_message = False

    # data = read_json("/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/project/o1_reasoning/o1-parallel/data/eval_results/parallel_summary_tir_platform_longcat_flash_thinking_2601/origin_ifeval_full_[think-merge-1228_merge_compress_v3_0105_128gbs_0106_recipe4-avg-general-ckpt_-1-k-8]_[summary-LongCat-Flash-Thinking-new_template_final_merge-k-4]_Pass-Prompt_Shuffle-All-AnswerClipped.json") # ifeval
    data = read_json("/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/project/o1_reasoning/o1-parallel/data/eval_results/parallel_summary_tir_platform_longcat_flash_thinking_2601/Arena_Hard_V2_[think-merge-1228_merge_compress_v3_0105_128gbs_0106_recipe4-avg-general-ckpt_-1-k-8]_[summary-LongCat-Flash-Thinking-new_template_final_merge-k-4]_Pass-Prompt_Shuffle-All-AnswerClipped.json") # arenha
    # data = read_json("/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/project/o1_reasoning/o1-parallel/data/eval_results/parallel_summary/AMO_Bench_v1_CH_[think-rft_continued_0107_mix_data_2x_search_amo_eval-ckpt_00000389-k-32]_[summary-LongCat-Flash-Thinking-new_template_heavy_math-k-4]_Pass-Prompt_Shuffle-All-AnswerClipped.json")
    data_keys = list(data.keys())
    task_name = data_keys[0]

    index = 38
    query = data[task_name][index]["query"]
    target = data[task_name][index]["target"]
    parallel_reason_content = data[task_name][index]["parallel_reason_content"]
    target = data[task_name][index]["target"]

    prompt = prompting(query, parallel_reason_content, "cn")


    # api_agent = APIAgent("longcat_flash_thinking_new_template", api_address, tokenizer=tokenizer)

    api_agent = APIAgent(model_name, api_address, tokenizer=tokenizer)

    # prompt = "Let $N$ be the greatest four-digit positive integer with the property that whenever one of its digits is changed to $1$, the resulting number is divisible by $7$. Let $Q$ and $R$ be the quotient and remainder, respectively, when $N$ is divided by $1000$. Find $Q+R$."

    # prompt = construct_prompt()
    # print(prompt)
    # assert 1>2
    # prompt = """You are a great reasoner. \nHere is a problem, and multiple thinkers attempt to give their thought processes independently. \nEach thinker has written its own thought process towards the final answer. Each thinker is encouraged to take the other thinkers\u2019 progress into account to reach the final answer.\n\n# ====== Problem ======\nConsider the paths of length $16$ that follow the lines from the lower left corner to the upper right corner on an $8\\times 8$ grid. Find the number of such paths that change direction exactly four times, as in the examples shown below.\n[asy] size(10cm); usepackage(\"tikz\");label(\"\\begin{tikzpicture}[scale=.5]\\draw(0,0)grid(8,8);\\draw[line width=2,red](0,0)--(2,0)--(2,3)--(5,3)--(5,8)--(8,8);\\end{tikzpicture}\",origin); label(\"\\begin{tikzpicture}[scale=.5]\\draw(0,0)grid(8,8);\\draw[line width=2,red](0,0)--(0,3)--(3,3)--(3,5)--(8,5)--(8,8);\\end{tikzpicture}\",E); [/asy]\n# ====== Problem End ======\n\n# ====== Thinkers Thought Process ======\n# ----- Thinker #1 -----\n\nEvery path of length \\(16\\) from \\((0,0)\\) to \\((8,8)\\) must consist of exactly eight steps to the right (R) and eight steps upward (U).  \nA \u201cchange of direction\u2019\u2019 occurs whenever the path switches from R to U or from U to R.  \n\nIf a path changes direction exactly four times, then it has  \n\n\\[\n\\text{#runs}= \\text{#changes}+1 = 5\n\\]\n\nconsecutive blocks of the same step.  \nThe blocks must alternate, so the path is of one of the two possible patterns  \n\n\\[\n\\text{R\u2013U\u2013R\u2013U\u2013R}\\qquad\\text{or}\\qquad\\text{U\u2013R\u2013U\u2013R\u2013U}.\n\\]\n\n---\n\n### 1.  Paths that start with a right step  \n\nIn the pattern R\u2013U\u2013R\u2013U\u2013R there are three horizontal runs and two vertical runs.  \n\n* The three horizontal runs have positive lengths that sum to \\(8\\).  \n  The number of ordered compositions of \\(8\\) into \\(3\\) positive parts is  \n\n  \\[\n  \\binom{8-1}{3-1}= \\binom{7}{2}=21 .\n  \\]\n\n* The two vertical runs have positive lengths that sum to \\(8\\).  \n  The number of ordered compositions of \\(8\\) into \\(2\\) positive parts is  \n\n  \\[\n  \\binom{8-1}{2-1}= \\binom{7}{1}=7 .\n  \\]\n\nHence there are \\(21\\times7=147\\) monotone paths of this type.\n\n---\n\n### 2.  Paths that start with an up step  \n\nThe pattern U\u2013R\u2013U\u2013R\u2013U is symmetric: now there are two horizontal runs and three vertical runs.  \nThe same counting gives another \\(7\\times21=147\\) paths.\n\n---\n\n### 3.  Total\n\nThe two families are disjoint, so the total number of length\u201116 monotone paths with exactly four direction changes is  \n\n\\[\n147+147 = 294 .\n\\]\n\n\\[\n\\boxed{294}\n\\]\n\n# ----- Thinker #2 -----\n\nThink of a monotone lattice path as a word of length \\(16\\) in the letters  \n\n\\[\nR\\;(right),\\qquad U\\;(up)\n\\]\n\nwith exactly eight \\(R\\)\u2019s and eight \\(U\\)\u2019s (to go from \\((0,0)\\) to \\((8,8)\\)).  \nA **direction change** occurs whenever two consecutive letters are different.  \nHence the number of direction changes equals\n\n\\[\n(\\text{# of runs})-1 ,\n\\]\n\nwhere a *run* is a maximal block of identical letters.\n\nExactly four direction changes \\(\\Longrightarrow\\) the word must have\n\\(5\\) runs.  \nSince the runs must alternate \\(R\\) and \\(U\\), the pattern of runs is either  \n\n\\[\nR\\;U\\;R\\;U\\;R\\qquad\\text{or}\\qquad \nU\\;R\\;U\\;R\\;U .\n\\]\n\nThus we have to split the eight \\(R\\)\u2019s and eight \\(U\\)\u2019s into positive blocks\nas follows.\n\n---\n\n### 1. Paths that start with \\(R\\)\n\n\\[\n\\begin{aligned}\nR\\text{-blocks:}&\\ a_1+a_3+a_5=8 \\quad (a_i\\ge1) ,\\\\\nU\\text{-blocks:}&\\ a_2+a_4=8 \\quad (a_i\\ge1).\n\\end{aligned}\n\\]\n\nNumber of solutions:\n\n* \\(a_1+a_3+a_5=8\\) has \\(\\binom{8-1}{3-1}= \\binom{7}{2}=21\\) solutions.\n* \\(a_2+a_4=8\\) has \\(\\binom{8-1}{2-1}= \\binom{7}{1}=7\\) solutions.\n\nHence \\(21\\times 7=147\\) paths start with \\(R\\).\n\n---\n\n### 2. Paths that start with \\(U\\)\n\nNow the roles of \\(R\\) and \\(U\\) are interchanged:\n\n\\[\n\\begin{aligned}\nU\\text{-blocks:}&\\ b_1+b_3+b_5=8 \\quad (b_i\\ge1),\\\\\nR\\text{-blocks:}&\\ b_2+b_4=8 \\quad (b_i\\ge1).\n\\end{aligned}\n\\]\n\nThe same count gives another \\(147\\) paths.\n\n---\n\n### Total\n\n\\[\n147+147 = 294.\n\\]\n\nTherefore the number of monotone paths of length \\(16\\) from the lower\u2011left\ncorner to the upper\u2011right corner of an \\(8\\times8\\) grid that change direction exactly four times is  \n\n\\[\n\\boxed{294}.\n\\]\n\n# ----- Thinker #3 -----\n\nA monotone lattice path from \\((0,0)\\) to \\((8,8)\\) consists of \\(8\\) horizontal steps (right) and \\(8\\) vertical steps (up).  \nA \u201cchange of direction\u2019\u2019 occurs when the path switches from a horizontal run to a vertical run or vice\u2011versa.\n\n---\n\n### 1.  How many runs does a path with four changes have?\n\nIf a path changes direction exactly four times, it must have  \n\n\\[\n\\text{#runs}= \\text{#changes}+1 =5 .\n\\]\n\nThus the path is a concatenation of five maximal straight segments that alternate\nhorizontal\u2013vertical\u2013horizontal\u2013vertical\u2013horizontal **or**\nvertical\u2013horizontal\u2013vertical\u2013horizontal\u2013vertical.\n\n---\n\n### 2.  Count the paths that start with a horizontal segment  \n\nPattern:  \n\n\\[\nR\\;-\\;U\\;-\\;R\\;-\\;U\\;-\\;R .\n\\]\n\nLet  \n\n\\[\na_1,a_2,a_3>0 \\qquad\\text{(lengths of the three horizontal runs)},\n\\]\n\\[\nb_1,b_2>0 \\qquad\\text{(lengths of the two vertical runs)} .\n\\]\n\nWe need  \n\n\\[\na_1+a_2+a_3=8,\\qquad b_1+b_2=8 .\n\\]\n\nThe number of ordered triples \\((a_1,a_2,a_3)\\) of positive integers summing to \\(8\\) is the number of\ncompositions of \\(8\\) into \\(3\\) parts:\n\n\\[\n\\binom{8-1}{3-1}= \\binom{7}{2}=21 .\n\\]\n\nThe number of ordered pairs \\((b_1,b_2)\\) of positive integers summing to \\(8\\) is\n\n\\[\n\\binom{8-1}{2-1}= \\binom{7}{1}=7 .\n\\]\n\nHence the number of paths that start with a horizontal step is  \n\n\\[\n21\\cdot 7 = 147 .\n\\]\n\n---\n\n### 3.  Count the paths that start with a vertical segment  \n\nBy symmetry the same count holds when the first step is vertical:\n\npattern \\(U\\!-\\!R\\!-\\!U\\!-\\!R\\!-\\!U\\) gives again  \n\n\\[\n\\binom{7}{1}\\cdot\\binom{7}{2}=147\n\\]\n\npaths.\n\n---\n\n### 4.  Total\n\n\\[\n\\boxed{147+147 = 294}\n\\]\n\nThus there are **294** monotone lattice paths of length \\(16\\) from the lower\u2011left corner to the upper\u2011right corner of an \\(8\\times8\\) grid that change direction exactly four times.\n\n# ----- Thinker #4 -----\n\nEach step of a shortest path from \\((0,0)\\) to \\((8,8)\\) is either a horizontal move \\(E\\) or a vertical move \\(N\\).  \nA path of length \\(16\\) therefore consists of exactly eight \\(E\\)\u2019s and eight \\(N\\)\u2019s.\n\n---\n\n### 1.  How many runs does a path with four direction changes have?\nA \u201cdirection change\u2019\u2019 occurs when two consecutive steps are different.  \nIf a path changes direction exactly \\(4\\) times, the steps are divided into  \n\n\\[\n\\text{#runs}=4+1=5\n\\]\n\nconsecutive maximal blocks of the same direction.\n\nBecause the runs must alternate, the pattern of directions is either  \n\n\\[\nE\\;N\\;E\\;N\\;E \\qquad\\text{or}\\qquad N\\;E\\;N\\;E\\;N .\n\\]\n\nThus one direction appears in three runs and the other in two runs.\n\n---\n\n### 2.  Distribute the eight steps of each direction among the runs  \n\n*Case 1 \u2013 start with \\(E\\):*  \n\n\\[\nE,N,E,N,E\n\\]\n\nThe three \\(E\\)-runs must contain all eight \\(E\\)-steps, each run having at least one step.  \nThe number of ways to write \\(8\\) as a sum of three positive integers is\n\n\\[\n\\binom{8-1}{3-1}=\\binom{7}{2}=21 .\n\\]\n\nThe two \\(N\\)-runs must contain the eight \\(N\\)-steps; the number of ways is\n\n\\[\n\\binom{8-1}{2-1}=\\binom{7}{1}=7 .\n\\]\n\nHence for this case there are  \n\n\\[\n21\\cdot 7 =147\n\\]\n\ndifferent paths.\n\n*Case 2 \u2013 start with \\(N\\):*  \n\nThe situation is symmetric: we again need three runs of one direction and two runs of the other, so the same count \\(147\\) arises.\n\n---\n\n### 3.  Total number of paths\n\n\\[\n147+147 = 294 .\n\\]\n\nThus the number of monotone paths of length \\(16\\) from the lower\u2011left to the upper\u2011right corner of an \\(8\\times8\\) grid that change direction exactly four times is  \n\n\\[\n\\boxed{294}.\n\\]\n\n# ----- Thinker #5 -----\n\nA monotone lattice path from \\((0,0)\\) to \\((8,8)\\) uses exactly \\(8\\) steps to the right and \\(8\\) steps upward, i.e. it has length \\(16\\).\nA **direction change** occurs whenever the path switches from a horizontal segment to a vertical one or vice\u2011versa.  \n\nIf the path changes direction \\(4\\) times, then it consists of  \n\n\\[\n\\text{#runs}=4+1=5\n\\]\n\nconsecutive \u201cruns\u2019\u2019 (segments all in the same direction).  \nThe runs must alternate between right (\\(R\\)) and up (\\(U\\)).  \nThus there are two possibilities:\n\n* start with \\(R\\): pattern \\(R-U-R-U-R\\)  \n  \u2013 three horizontal runs, two vertical runs,\n* start with \\(U\\): pattern \\(U-R-U-R-U\\)  \n  \u2013 two horizontal runs, three vertical runs.\n\n---\n\n### 1.  Paths that start with a horizontal segment  \n\nLet the lengths of the three horizontal runs be \\(a_1,a_2,a_3\\ge1\\) and the lengths of the two vertical runs be \\(b_1,b_2\\ge1\\).  \nWe need  \n\n\\[\na_1+a_2+a_3=8,\\qquad b_1+b_2=8 .\n\\]\n\nBy the stars\u2011and\u2011bars theorem, the number of positive integer solutions of  \n\n\\[\na_1+a_2+a_3=8\n\\]\n\nis \\(\\displaystyle \\binom{8-1}{3-1}=\\binom{7}{2}=21\\), and for  \n\n\\[\nb_1+b_2=8\n\\]\n\nit is \\(\\displaystyle \\binom{8-1}{2-1}=\\binom{7}{1}=7\\).\n\nHence the number of such paths is  \n\n\\[\n21\\cdot 7 = 147 .\n\\]\n\n---\n\n### 2.  Paths that start with a vertical segment  \n\nNow we have two horizontal runs and three vertical runs, the same counting applies:\n\n\\[\n\\text{horizontal: } r_1+r_2=8 \\;\\Rightarrow\\; \\binom{7}{1}=7,\n\\qquad\n\\text{vertical: } u_1+u_2+u_3=8 \\;\\Rightarrow\\; \\binom{7}{2}=21 .\n\\]\n\nThus we again obtain \\(7\\cdot21=147\\) paths.\n\n---\n\n### Total\n\n\\[\n147\\;(\\text{start }R) \\;+\\;147\\;(\\text{start }U) = 294 .\n\\]\n\n\\[\n\\boxed{294}\n\\]\n\n# ----- Thinker #6 -----\n\nEach step of the path is either a right\u2013move \\(R\\) or an up\u2013move \\(U\\).  \nA path of length \\(16\\) from \\((0,0)\\) to \\((8,8)\\) must contain exactly eight \\(R\\)\u2019s\nand eight \\(U\\)\u2019s.\n\nA \u201cchange of direction\u2019\u2019 occurs when the path switches from a block of\nconsecutive \\(R\\)\u2019s to a block of consecutive \\(U\\)\u2019s or vice\u2011versa.  \nIf there are exactly four changes, the step\u2011string consists of five blocks:\n\n\\[\n\\underbrace{R\\ldots R}_{\\text{block }1}\\,\n\\underbrace{U\\ldots U}_{\\text{block }2}\\,\n\\underbrace{R\\ldots R}_{\\text{block }3}\\,\n\\underbrace{U\\ldots U}_{\\text{block }4}\\,\n\\underbrace{R\\ldots R}_{\\text{block }5}\n\\qquad\\text{or}\\qquad\nU\\,R\\,U\\,R\\,U .\n\\]\n\nThus we have two cases.\n\n---\n\n### 1.  Paths that start with a right move  \n\nThe pattern is \\(R\\,U\\,R\\,U\\,R\\).  \nLet the lengths of the three \\(R\\)-blocks be \\(r_1,r_2,r_3\\) \\((r_i\\ge1)\\) and\nthe lengths of the two \\(U\\)-blocks be \\(u_1,u_2\\) \\((u_i\\ge1)\\).  \nWe need  \n\n\\[\nr_1+r_2+r_3=8,\\qquad u_1+u_2=8 .\n\\]\n\nThe number of compositions of \\(8\\) into three positive parts is\n\\(\\displaystyle\\binom{8-1}{3-1}=\\binom{7}{2}=21\\);  \nthe number of compositions of \\(8\\) into two positive parts is\n\\(\\displaystyle\\binom{8-1}{2-1}=\\binom{7}{1}=7\\).\n\nHence the number of paths of this type is  \n\\(21\\times7=147\\).\n\n---\n\n### 2.  Paths that start with an up move  \n\nNow the pattern is \\(U\\,R\\,U\\,R\\,U\\).  \nExactly the same counting applies: the three \\(U\\)-blocks sum to \\(8\\) and the\ntwo \\(R\\)-blocks sum to \\(8\\).  \nThus we again obtain \\(21\\times7=147\\) paths.\n\n---\n\n### Total\n\n\\[\n147+147 = 294 .\n\\]\n\nTherefore the number of monotone lattice paths from the lower\u2011left corner to the\nupper\u2011right corner of an \\(8\\times8\\) grid that change direction exactly four\ntimes is  \n\n\\[\n\\boxed{294}.\n\\]\n\n# ----- Thinker #7 -----\n\nThe path must consist only of steps to the right (east) and upward (north), because any step left or down would make the total length exceed the minimum possible length \\(8+8=16\\).\n\nIf the path changes direction exactly four times, then it has  \n\n\\[\n\\text{segments}=4+1=5\n\\]\n\nalternating horizontal and vertical segments.  \nIt must therefore be of one of the two possible types  \n\n* \\(E\\!-\\!N\\!-\\!E\\!-\\!N\\!-\\!E\\)  (starts east, ends east)  \n* \\(N\\!-\\!E\\!-\\!N\\!-\\!E\\!-\\!N\\)  (starts north, ends north).\n\n---\n\n### Counting the paths that start east\n\nLet the three horizontal segments have lengths \\(a_1,a_3,a_5\\) and the two vertical segments have lengths \\(a_2,a_4\\).  \nAll lengths are positive integers and\n\n\\[\na_1+a_3+a_5=8,\\qquad a_2+a_4=8 .\n\\]\n\nThe number of ordered positive integer solutions of the first equation is the number of compositions of 8 into 3 parts:\n\n\\[\n\\binom{8-1}{3-1}=\\binom{7}{2}=21 .\n\\]\n\nThe number of ordered positive integer solutions of the second equation is the number of compositions of 8 into 2 parts:\n\n\\[\n\\binom{8-1}{2-1}=\\binom{7}{1}=7 .\n\\]\n\nThus\n\n\\[\n\\#(\\text{paths of type }E\\!-\\!N\\!-\\!E\\!-\\!N\\!-\\!E)=21\\cdot7=147 .\n\\]\n\n---\n\n### Counting the paths that start north\n\nNow the vertical segments are three and the horizontal segments are two:\n\n\\[\nb_1+b_3+b_5=8,\\qquad b_2+b_4=8 .\n\\]\n\nThe numbers of compositions are interchanged:\n\n\\[\n\\binom{7}{2}=21\\quad\\text{vertical},\\qquad\n\\binom{7}{1}=7\\quad\\text{horizontal},\n\\]\n\ngiving again \\(21\\cdot7=147\\) paths.\n\n---\n\n### Total\n\n\\[\n147+147 = 294 .\n\\]\n\nHence the number of monotone paths of length \\(16\\) from the lower\u2011left corner to the upper\u2011right corner of an \\(8\\times8\\) grid that change direction exactly four times is  \n\n\\[\n\\boxed{294}.\n\\]\n\n# ----- Thinker #8 -----\n\nThe red path must consist of horizontal (right) and vertical (up) unit steps.\nFrom \\((0,0)\\) to \\((8,8)\\) we need exactly \\(8\\) right steps and \\(8\\) up steps,\nso any monotone path has length \\(16\\).\n\nA \u201cchange of direction\u2019\u2019 occurs when a right step is followed by an up step\nor vice\u2011versa.  \nExactly four changes mean the step sequence has **five runs** of consecutive\nsteps, alternating between right and up.\n\nHence the pattern of runs is either  \n\n\\[\nR\\;U\\;R\\;U\\;R\\qquad\\text{or}\\qquad U\\;R\\;U\\;R\\;U .\n\\]\n\nIn the first case the three \\(R\\)-runs have lengths \\(r_{1},r_{2},r_{3}>0\\) with  \n\n\\[\nr_{1}+r_{2}+r_{3}=8,\n\\]\n\nand the two \\(U\\)-runs have lengths \\(u_{1},u_{2}>0\\) with  \n\n\\[\nu_{1}+u_{2}=8.\n\\]\n\nCon1, in the second case we have three \\(U\\)-runs and two \\(R\\)-runs with the\nsame equations.\n\nThe number of positive integer solutions of\n\n\\[\nr_{1}+r_{2}+r_{3}=8\n\\]\n\nis \\(\\displaystyle\\binom{8-1}{3-1}= \\binom{7}{2}=21\\).\n\nThe number of positive integer solutions of\n\n\\[\nu_{1}+u_{2}=8\n\\]\n\nis \\(\\displaystyle\\binom{8-1}{2-1}= \\binom{7}{1}=7\\).\n\nFor a fixed starting direction the number of admissible paths is therefore  \n\n\\[\n21 \\times 7 = 147.\n\\]\n\nSince the path may start either with a right step or with an up step, we double\nthis count:\n\n\\[\n2 \\times 147 = 294 .\n\\]\n\nThus there are  \n\n\\[\n\\boxed{294}\n\\]\n\nmonotone lattice paths from the lower left corner to the upper right corner of\nthe \\(8\\times 8\\) grid that change direction exactly four times.\n\n\n# ====== Thinkers Thought Process End ======\n\nLook at the above problem and thought process from each thinker, summarize from these thought processes by aggregating most probably result from most thinkers. \nPlease DO NOT just solve the given problem independently like other thinkers, but summarize the thought process of all thinkers. In other words, you need to give the summary first, and then give the final answer within \\boxed."""

    # prompt = """
    # 你好，请帮我订购一个26年1月20日由上海前往北京的机票，要求落地时间不超过下午4点。
    # """.strip()

    # prompt = """
    # 请打印出\pi的第1000000～1000100位
    # """

    # prompt = """
    # Please write a program game in H5 to support the following:
    # Vinyl simulation: drop the needle to play
    # """






    prompt = """<longcat_system># heavyclaw 🐈

You are heavyclaw, a helpful AI assistant.

## Runtime
macOS arm64, Python 3.11.14

## Workspace
Your workspace is at: /Users/jianingwang/.heavyclaw/workspace
- Long-term memory: /Users/jianingwang/.heavyclaw/workspace/memory/MEMORY.md (write important facts here)
- History log: /Users/jianingwang/.heavyclaw/workspace/memory/HISTORY.md (grep-searchable). Each entry starts with [YYYY-MM-DD HH:MM].
- Custom skills: /Users/jianingwang/.heavyclaw/workspace/skills/{skill-name}/SKILL.md

## Platform Policy (POSIX)
- You are running on a POSIX system. Prefer UTF-8 and standard shell tools.
- Use file tools when they are simpler or more reliable than shell commands.


## heavyclaw Guidelines
- State intent before tool calls, but NEVER predict or claim results before receiving them.
- Before modifying a file, read it first. Do not assume files or directories exist.
- After writing or editing a file, re-read it if accuracy matters.
- If a tool call fails, analyze the error before retrying with a different approach.
- Ask for clarification when the request is ambiguous.

Reply directly with text for conversations. Only use the 'message' tool to send to a specific chat channel.

---

## AGENTS.md

# Agent Instructions

You are a helpful AI assistant. Be concise, accurate, and friendly.

## Guidelines

- Before calling tools, briefly state your intent — but NEVER predict results before receiving them
- Use precise tense: "I will run X" before the call, "X returned Y" after
- NEVER claim success before a tool result confirms it
- Ask for clarification when the request is ambiguous
- Remember important information in `memory/MEMORY.md`; past events are logged in `memory/HISTORY.md`

## Scheduled Reminders

When user asks for a reminder at a specific time, use `exec` to run:
```
heavyclaw cron add --name "reminder" --message "Your message" --at "YYYY-MM-DDTHH:MM:SS" --deliver --to "USER_ID" --channel "CHANNEL"
```
Get USER_ID and CHANNEL from the current session (e.g., `8281248569` and `telegram` from `telegram:8281248569`).

**Do NOT just write reminders to MEMORY.md** — that won't trigger actual notifications.

## Heartbeat Tasks

`HEARTBEAT.md` is checked every 30 minutes. Use file tools to manage periodic tasks:

- **Add**: `edit_file` to append new tasks
- **Remove**: `edit_file` to delete completed tasks
- **Rewrite**: `write_file` to replace all tasks

When the user asks for a recurring/periodic task, update `HEARTBEAT.md` instead of creating a one-time cron reminder.


## SOUL.md

# Soul

I am Meituan LongCat HeavyClaw 🐈, a personal AI assistant for you.

## Personality

- Helpful and friendly
- Concise and to the point
- Curious and eager to learn

## Values

- Accuracy over speed
- User privacy and safety
- Transparency in actions

## Communication Style

- Be clear and direct
- Explain reasoning when helpful
- Ask clarifying questions when needed


## USER.md

# User Profile

Information about the user to help personalize interactions.

## Basic Information

- **Name**: (your name)
- **Timezone**: (your timezone, e.g., UTC+8)
- **Language**: (preferred language)

## Preferences

### Communication Style

- [ ] Casual
- [ ] Professional
- [ ] Technical

### Response Length

- [ ] Brief and concise
- [ ] Detailed explanations
- [ ] Adaptive based on question

### Technical Level

- [ ] Beginner
- [ ] Intermediate
- [ ] Expert

## Work Context

- **Primary Role**: (your role, e.g., developer, researcher)
- **Main Projects**: (what you're working on)
- **Tools You Use**: (IDEs, languages, frameworks)

## Topics of Interest

-
-
-

## Special Instructions

(Any specific instructions for how the assistant should behave)

---

*Edit this file to customize heavyclaw's behavior for your needs.*


## TOOLS.md

# Tool Usage Notes

Tool signatures are provided automatically via function calling.
This file documents non-obvious constraints and usage patterns.

## exec — Safety Limits

- Commands have a configurable timeout (default 60s)
- Dangerous commands are blocked (rm -rf, format, dd, shutdown, etc.)
- Output is truncated at 10,000 characters
- `restrictToWorkspace` config can limit file access to the workspace

## cron — Scheduled Reminders

- Please refer to cron skill for usage.


---

# Memory

## Long-term Memory
# Long-term Memory

This file stores important information that should persist across sessions.

## User Information

(Important facts about the user)

## Preferences

(User preferences learned over time)

## Project Context

(Information about ongoing projects)

## Important Notes

(Things to remember)

---

*This file is automatically updated by heavyclaw when important information should be remembered.*


---

# Active Skills

### Skill: memory

# Memory

## Structure

- `memory/MEMORY.md` — Long-term facts (preferences, project context, relationships). Always loaded into your context.
- `memory/HISTORY.md` — Append-only event log. NOT loaded into context. Search it with grep-style tools or in-memory filters. Each entry starts with [YYYY-MM-DD HH:MM].

## Search Past Events

Choose the search method based on file size:

- Small `memory/HISTORY.md`: use `read_file`, then search in-memory
- Large or long-lived `memory/HISTORY.md`: use the `exec` tool for targeted search

Examples:
- **Linux/macOS:** `grep -i "keyword" memory/HISTORY.md`
- **Windows:** `findstr /i "keyword" memory\HISTORY.md`
- **Cross-platform Python:** `python -c "from pathlib import Path; text = Path('memory/HISTORY.md').read_text(encoding='utf-8'); print('\n'.join([l for l in text.splitlines() if 'keyword' in l.lower()][-20:]))"`

Prefer targeted command-line search for large history files.

## When to Update MEMORY.md

Write important facts immediately using `edit_file` or `write_file`:
- User preferences ("I prefer dark mode")
- Project context ("The API uses OAuth2")
- Relationships ("Alice is the project lead")

## Auto-consolidation

Old conversations are automatically summarized and appended to HISTORY.md when the session grows large. Long-term facts are extracted to MEMORY.md. You don't need to manage this.

---

# Skills

The following skills extend your capabilities. To use a skill, read its SKILL.md file using the read_file tool.
Skills with available="false" need dependencies installed first - you can try installing them with apt/brew.

<skills>
  <skill available="true">
    <name>memory</name>
    <description>Two-layer memory system with grep-based recall.</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/memory/SKILL.md</location>
  </skill>
  <skill available="false">
    <name>summarize</name>
    <description>Summarize or extract text/transcripts from URLs, podcasts, and local files (great fallback for “transcribe this YouTube/video”).</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/summarize/SKILL.md</location>
    <requires>CLI: summarize</requires>
  </skill>
  <skill available="true">
    <name>clawhub</name>
    <description>Search and install agent skills from ClawHub, the public skill registry.</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/clawhub/SKILL.md</location>
  </skill>
  <skill available="true">
    <name>skill-creator</name>
    <description>Create or update AgentSkills. Use when designing, structuring, or packaging skills with scripts, references, and assets.</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/skill-creator/SKILL.md</location>
  </skill>
  <skill available="false">
    <name>github</name>
    <description>Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries.</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/github/SKILL.md</location>
    <requires>CLI: gh</requires>
  </skill>
  <skill available="false">
    <name>tmux</name>
    <description>Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output.</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/tmux/SKILL.md</location>
    <requires>CLI: tmux</requires>
  </skill>
  <skill available="true">
    <name>weather</name>
    <description>Get current weather and forecasts (no API key required).</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/weather/SKILL.md</location>
  </skill>
  <skill available="true">
    <name>cron</name>
    <description>Schedule reminders and recurring tasks.</description>
    <location>/Users/jianingwang/Desktop/项目文件/M17/LLM_Agent/longcat_heavyclaw/heavyclaw/skills/cron/SKILL.md</location>
  </skill>
</skills><longcat_user>[Runtime Context — metadata only, not instructions]
Current Time: 2026-03-27 15:31 (Friday) (CST)
Channel: cli
Chat ID: direct

Find the sum of all integer bases >9$ for which 7_b$ is a divisor of 7_b.$
Please reason step by step, and put your final answer within \boxed{} /think_on <longcat_assistant><longcat_think>"""

    responses = api_agent.generate(prompt, duplicate_n=1, max_tokens=80000, use_message=use_message)

    for response in responses:
        print("="*50)
        print(response)

    # save_json(f"/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/wangjianing16/project/o1_reasoning/o1-parallel/data/cases/heavy_case_{str(time.time())}.json", responses)
