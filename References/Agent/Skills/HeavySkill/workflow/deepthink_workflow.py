"""
随机抽取一批指定模型在thinking阶段采样生成的response，并调用指定summary模型来完成summary answer，并调用model eval来进行打分
"""

import os
import sys
import json
import time
import math
import random
import argparse
import numpy as np
import torch
from tqdm import tqdm
import multiprocessing
from agent.vllm import vLLMAgent
from agent.api import APIAgent
import transformers
from transformers import AutoTokenizer
from deepthink_data_analysis_from_eval_v2platform import extract_answer


def read_json(path):
    with open(path, "r", encoding="utf-8") as fr:
       result = json.load(fr)
    return result

def save_jsonl(path, examples):
    with open(path, "w", encoding="utf-8") as fw:
        for example in tqdm(examples):
            fw.write(json.dumps(example, ensure_ascii=False) + "\n")

def save_json(path, example):
    with open(path, "w", encoding="utf-8") as fw:
        json.dump(example, fw)



"""
重复性监测
"""
def duplication(response, think_end_tag):
    # 如果模型出现复读导致截断的问题
    if response[-512:] == response[-1024:-512]:
        return True
    # 如果输出存在超长截断的问题，也忽略
    if think_end_tag not in response:
        return True
    return False


"""
permutation策略
给定一组response，按照不同的permutation来构造parallel thinking set
"""
def permutating(result_list, k: int, order: str, scale: str, component: str, max_tokens=8e4, tokenizer=None, think_start_tag=None, think_end_tag=None):
    print("component={}".format(component))
    assert order in ["Shuffle"]
    assert scale in ["All", "GroupOne"]
    # assert component in ["Response", "Think", "ThinkClipped", "Answer", "AnswerClipped"]
    assert component in ["Think", "ThinkClipped", "Answer", "AnswerClipped"]

    # 随机采样k个response
    # if k < len(result_list):
    #     sampled_result_list = random.sample(result_list, k)
    # else:
    #     sampled_result_list = [i for i in result_list]

    # 随机采样k个response，需要确保采样到的response不会出现复读截断问题
    valide_result_list = list()
    for result in result_list:
        response = result["response"]
        # correctness = result["correctness"]
        # 进行复读截断监测
        if duplication(response, think_end_tag=think_end_tag):
            # 说明当前的response出现截断问题，如果出现截断则说明correctness一定为False
            continue
        valide_result_list.append(result)

    if len(valide_result_list) == 0:
        print("has no valid result, so retain the origin result.")
        valide_result_list = result_list
    if k < len(valide_result_list):
        sampled_result_list = random.sample(valide_result_list, k)
    else:
        sampled_result_list = [i for i in valide_result_list]


    """
    1. 进行统计意义上的Pass@K和Major@K计算
    """

    metric = { # 保存统计意义当前query的结果
        f"Mean@{k}": 0,
        f"Pass@{k}": 0,
        f"Major@{k}": 0,
    }


    answer2correctness = dict() # 预测的答案对应是否正确
    answer2frequency = dict() # 预测的答案对应投票数量
    answer2response_length = dict() # 预测的答案对应response的字符平均长度

    avg_acc = 0
    correctness_list = list()

    for result in sampled_result_list:
        answer = result["answer"]
        response = result["response"]
        correctness = result["correctness"]
        correctness_list.append(correctness)

        if correctness is True:
            # 只要存在一个True的，Pass@k则为1
            metric[f"Pass@{k}"] = 1
            avg_acc += 1

        if answer not in answer2correctness:
            answer2correctness[answer] = list()
        answer2correctness[answer].append(correctness)

        if answer not in answer2response_length.keys():
            answer2response_length[answer] = 0
        answer2response_length[answer] += len(response)

        if answer not in answer2frequency.keys():
            answer2frequency[answer] = 0
        answer2frequency[answer] += 1

    metric[f"Mean@{k}"] = avg_acc / len(sampled_result_list) if len(sampled_result_list) > 0 else 0

    for answer, response_length in answer2response_length.items():
        answer2response_length[answer] = response_length / answer2frequency[answer]

    # 获取投票数最多的数值
    max_frequency = max(list(answer2frequency.values()))
    # 获取所有票数都是最高的answer，并按照length排序
    candidate_answer2response_length = dict()
    for answer, frequency in answer2frequency.items():
        if frequency == max_frequency:
            candidate_answer2response_length[answer] = answer2response_length[answer]
    candidate_answer_response_length_sorted_list = list(sorted(candidate_answer2response_length.items(), key=lambda x:x[1], reverse=True))

    major_answer = candidate_answer_response_length_sorted_list[0][0]
    major_num = candidate_answer_response_length_sorted_list[0][1]

    # 判断投票的结果是否正确
    # 容易出现抽取boxed的answer相同，但是模型打分不同的情况，此时遵循最大原则，即打分0或1数量最多的作为最终correntness结果

    try:
        score_true_num = sum(answer2correctness[major_answer])
        score_false_num = len(answer2correctness[major_answer]) - sum(answer2correctness[major_answer])
    except:
        score_true_num = 0
        score_false_num = 0
    if score_true_num >= score_false_num:
        metric[f"Major@{k}"] = 1
    else:
        metric[f"Major@{k}"] = 0

    """
    2.根据permutation来构造response list
    """
    response_list = list() # 存储inference的response内容
    response2token_num = dict() # 存储inference的response token数量

    for result in sampled_result_list:
        response = result["response"]
        response2token_num[response] = result["response_token_num"]

    # 确定response的规模
    if scale == "All":
        for result in sampled_result_list:
            response = result["response"]
            response_list.append(response.strip())
    elif scale == "GroupOne":
        answer2responses = dict()
        for result in sampled_result_list:
            answer = result["answer"]
            if answer not in answer2responses.keys():
                answer2responses[answer] = list()
            answer2responses[answer].append(result["response"])

        for _, cur_response_list in answer2responses.items():
            response_list.extend(random.sample(cur_response_list, 1))

    # 确定response的来源
    total_token_num = 0 # 估计值

    if component == "Think":
        new_response_list = list()
        for response in response_list:
            if response.count(think_end_tag) == 1:
                think_content = response.split(think_end_tag)[0].replace(think_start_tag, "")
            elif response.count(think_end_tag) > 1:
                think_content = "\n".join(response.split(think_end_tag)[:-1]).replace(think_start_tag, "")
            else:
                # 说明超长截断了
                think_content = response.replace(think_start_tag, "")

            think_content = think_content.strip()

            # 通过word层面上的think content与response的占比来估计think content的token数量
            if tokenizer is None:
                think_content_split_num = len(think_content.split(" "))
                response_split_num = len(response.split(" "))
                think_content_token_num = int(response2token_num[response] * think_content_split_num / response_split_num)
                print("think_content_token_num=", think_content_token_num)
            else:
                think_content_token_num = len(tokenizer.encode(think_content))
                print("think_content_token_num=", think_content_token_num)


            total_token_num += think_content_token_num
            new_response_list.append(think_content)

        print("total_token_num=", total_token_num)
        response_list = new_response_list

    elif component == "ThinkClipped":
        # 有的think content太长了，所以对于太长的think content进行截断操作。这里默认截断采用去头法

        new_response_list = list()
        new_response_token_num_list = list()
        for response in response_list:
            if response.count(think_end_tag) == 1:
                think_content = response.split(think_end_tag)[0].replace(think_start_tag, "")
            elif response.count(think_end_tag) > 1:
                think_content = "\n".join(response.split(think_end_tag)[:-1]).replace(think_start_tag, "")
            else:
                # 说明超长截断了
                think_content = response.replace(think_start_tag, "")
            think_content = think_content.strip()


            # 通过word层面上的think content与response的占比来估计think content的token数量
            if tokenizer is None:
                think_content_split_num = len(think_content.split(" "))
                response_split_num = len(response.split(" "))
                think_content_token_num = int(response2token_num[response] * think_content_split_num / response_split_num)
            else:
                think_content_token_num = len(tokenizer.encode(think_content))

            total_token_num += think_content_token_num
            new_response_token_num_list.append(think_content_token_num)
            new_response_list.append(think_content)


        # 如果总长度依然超过max token，则超过的地方大家平摊，裁剪采用去头法
        if total_token_num > max_tokens:
            print(f"Total num {total_token_num} is exceed {max_tokens}, so need clipping ...")
            # 平摊要裁剪的token数
            cut_token_num = int((total_token_num - max_tokens) / len(sampled_result_list))
            total_token_num = 0

            for response, token_num in zip(new_response_list, new_response_token_num_list):
                # # 估计要裁剪的word数
                # response_split_word_num = len(response.split(" "))
                # cut_word_num = int(response_split_word_num / token_num * cut_token_num)
                # # 根据估计的word数进行裁剪
                # response = " ".join(response.split(" ")[cut_word_num:])
                tokens = tokenizer.encode(response)
                token_num_before_cut = len(tokens)
                tokens = tokens[cut_token_num:]
                response = tokenizer.decode(tokens)
                print("token_num: before_cut={}, after_cut={}".format(token_num_before_cut, len(tokenizer.encode(response))))

                if tokenizer is not None:
                    total_token_num += len(tokenizer.encode(response))

            if tokenizer is None:
                total_token_num = max_tokens
        else:
            for response, token_num in zip(new_response_list, new_response_token_num_list):
                print("token num: {}".format(len(tokenizer.encode(response))))


        print("total_token_num=", total_token_num)
        response_list = new_response_list

    elif component == "Answer":
        new_response_list = list()
        for response in response_list:
            if think_end_tag in response:
                answer_content = response.split(think_end_tag)[-1]
            else:
                # 说明超长截断了，此时默认取think content的内容
                answer_content = response.replace(think_start_tag, "")

            answer_content = answer_content.strip()

            # 通过word层面上的answer content与response的占比来估计answer content的token数量
            if tokenizer is None:
                answer_content_split_num = len(answer_content.split(" "))
                response_split_num = len(response.split(" "))
                answer_content_token_num = int(response2token_num[response] * answer_content_split_num / response_split_num)
                print("answer_content_token_num=", answer_content_token_num)
            else:
                answer_content_token_num = len(tokenizer.encode(answer_content))
                print("answer_content_token_num=", answer_content_token_num)

            total_token_num += answer_content_token_num
            new_response_list.append(answer_content)

        print("total_token_num=", total_token_num)
        response_list = new_response_list

    elif component == "AnswerClipped":
        new_response_list = list()
        new_response_token_num_list = list()

        for response in response_list:
            if think_end_tag in response:
                answer_content = response.split(think_end_tag)[-1]
            else:
                # 说明超长截断了，此时默认取think content的内容
                answer_content = response.replace(think_start_tag, "")
            answer_content = answer_content.strip()

            # 通过word层面上的answer content与response的占比来估计answer content的token数量
            if tokenizer is None:
                answer_content_split_num = len(answer_content.split(" "))
                response_split_num = len(response.split(" "))
                answer_content_token_num = int(response2token_num[response] * answer_content_split_num / response_split_num)
            else:
                answer_content_token_num = len(tokenizer.encode(answer_content))

            total_token_num += answer_content_token_num
            new_response_token_num_list.append(answer_content_token_num)
            new_response_list.append(answer_content)

        # 如果总长度依然超过max token，则超过的地方大家平摊，裁剪采用去头法
        if total_token_num > max_tokens:
            print(f"Total num {total_token_num} is exceed {max_tokens}, so need clipping ...")
            # 平摊要裁剪的token数
            cut_token_num = int((total_token_num - max_tokens) / k)
            total_token_num = 0

            for response, token_num in zip(new_response_list, new_response_token_num_list):
                # 估计要裁剪的word数
                # response_split_word_num = len(response.split(" "))
                # cut_word_num = int(response_split_word_num / token_num * cut_token_num)
                # # 根据估计的word数进行裁剪
                # response = " ".join(response.split(" ")[cut_word_num:])
                tokens = tokenizer.encode(response)
                token_num_before_cut = len(tokens)
                tokens = tokens[cut_token_num:]
                response = tokenizer.decode(tokens)

                print("token_num: before_cut={}, after_cut={}".format(token_num_before_cut, len(tokenizer.encode(response))))

                if tokenizer is not None:
                    total_token_num += len(tokenizer.encode(response))

            if tokenizer is None:
                total_token_num = max_tokens
        else:
            for response, token_num in zip(new_response_list, new_response_token_num_list):
                print("token num: {}".format(len(tokenizer.encode(response))))

        print("total_token_num=", total_token_num)
        response_list = new_response_list

    else:
        new_response_list = list()
        for response in response_list:
            total_token_num += response2token_num[response]
            # 将<think>和</think>都丢掉，防止这些token干扰后续模型推理
            response = response.replace(think_start_tag + "\n", "").replace(think_end_tag, "\n")
            new_response_list.append(response)

        response_list = new_response_list

    # 确定response的顺序
    if order == "Shuffle":
        indexs = [i for i in range(len(response_list))]
        random.shuffle(indexs)
        response_list = [response_list[index] for index in indexs]
        correctness_list = [correctness_list[index] for index in indexs]


    return response_list, total_token_num, metric, correctness_list


def prompting(summary_type, query, parallel_reason_content_list):
    if summary_type == "Major-Prompt":
        prompt = """
You are a great reasoner.
Here is a problem, and multiple thinkers attempt to give their thought processes independently.
Each thinker has written its own thought process towards the final answer. Each thinker is encouraged to take the other thinkers’ progress into account to reach the final answer.

# ====== Problem ======
{problem}
# ====== Problem End ======

# ====== Thinkers Thought Process ======
{response_prompt}
# ====== Thinkers Thought Process End ======

Look at the above problem and thought process from each thinker, summarize from these thought processes by aggregating most probably result from most thinkers.
Please DO NOT just solve the given problem independently like other thinkers, but summarize the thought process of all thinkers. In other words, you need to give the summary first, and then give the final answer.
For the output format of your final answer after the summary, you should follow the similar format with thinkers:
- If the problem is mathematics or STEM and most thinkers have put the answer within boxed, your final answer after the summary should within boxed too.
- If the problem is code contest and most thinkers have put the result code within a block like "```", your final answer should also within the block.
""".strip()
    elif summary_type == "Pass-Prompt":
        prompt = """
You are a great reasoner.
Here is a problem, and multiple thinkers attempt to give their thought processes independently.
Each thinker has written its own thought process towards the final answer. Each thinker is encouraged to take the other thinkers’ progress into account to reach the final answer.

# ====== Problem ======
{problem}
# ====== Problem End ======

# ====== Thinkers Thought Process ======
{response_prompt}
# ====== Thinkers Thought Process End ======

Look at the above problem and thought process from each thinker, summarize from these thought processes and finally give your answer.
Summarize their thinking on the problem and try to summarize the thinking of these thinkers. Analyze the differences in thinking between these thinkers and try to analyze which thought process is correct.
Note:
- It is generally believed that when most thinkers get the same answer, the answer may be correct. But you can't do it so superficially, because the correct answer may come from very few thinkers, or even no thinker gives the correct answer. For this reason, when you summarizing, you NEED adhere to the principles of professionalism and critical thinking, carefully identify these thought processes, and give a summary and final answer.
- If you realize that none of these thinkers have answered correctly, you can even learn from the wrong experiences in the thought process of these thinkers and re-think the given problem to give the answer you think is most correct.
- Please DO NOT just solve the given problem independently like other thinkers, but summarize the thought process of all thinkers. In other words, you need to give the summary first, and then give the final answer, you can re-think this problem only if you realize that none of these thinkers have answered correctly.
For the output format of your final answer after the summary, you should follow the similar format with thinkers:
- If the problem is mathematics or STEM and most thinkers have put the answer within boxed, your final answer after the summary should within boxed too.
- If the problem is code contest and most thinkers have put the result code within a block like "```", your final answer should also within the block.
""".strip()

    elif summary_type == "Pass-Prompt-1":
        prompt = """
You are a great reasoner.
Here is a problem, and multiple thinkers attempt to give their thought processes independently.
Each thinker has written its own thought process towards the final answer. Each thinker is encouraged to take the other thinkers’ progress into account to reach the final answer.

# ====== Problem ======
{problem}
# ====== Problem End ======

# ====== Thinkers Thought Process ======
{response_prompt}
# ====== Thinkers Thought Process End ======

Look at the above problem and thought process from each thinker, summarize from these thought processes and finally give your answer.
Summarize their thinking on the problem and try to summarize the thinking of these thinkers. Analyze the differences in thinking between these thinkers and try to analyze which thought process is correct.
Note:
- It is generally believed that when most thinkers get the same answer, the answer may be correct. But you can't do it so superficially, because the correct answer may come from very few thinkers, or even no thinker gives the correct answer. For this reason, when you summarizing, you NEED adhere to the principles of professionalism and critical thinking, carefully identify these thought processes, and give a summary and final answer.
- If you realize that none of these thinkers have answered correctly, you can even learn from the wrong experiences in the thought process of these thinkers and re-think the given problem to give the answer you think is most correct.
- Please DO NOT just solve the given problem independently like other thinkers, but summarize the thought process of all thinkers. In other words, you need to give the summary first, and then give the final answer, you can re-think this problem only if you realize that none of these thinkers have answered correctly.
- You need to consider language consistency. Your analysis and final output responses must be consistent with the language type of the given query. For example, if the query and each thinker are primarily in Chinese, then your analysis and responses must also be primarily in Chinese, too. If the query and each thinker are primarily in English, then your analysis and responses must also be primarily in English, too. By the way, if the language of the query and each thinker‘s response is inconsistent, then you MUST maintain consistency with the language type of the given query.
For the output format of your final answer after the summary, you should follow the similar format with thinkers:
- If the problem is mathematics or STEM and most thinkers have put the answer within boxed, your final answer after the summary should within boxed too.
- If the problem is code contest and most thinkers have put the result code within a block like "```", your final answer should also within the block.
""".strip()

    elif summary_type == "Pass-Prompt-2":
        prompt = """
You are a great reasoner.
Here is a problem, and multiple thinkers attempt to give their thought processes independently.
Each thinker has written its own thought process towards the final answer. Each thinker is encouraged to take the other thinkers’ progress into account to reach the final answer.

# ====== Problem ======
{problem}
# ====== Problem End ======

# ====== Thinkers Thought Process ======
{response_prompt}
# ====== Thinkers Thought Process End ======

Look at the above problem and thought process from each thinker, summarize from these thought processes and finally give your answer.
Summarize their thinking on the problem and try to summarize the thinking of these thinkers. Analyze the differences in thinking between these thinkers and try to analyze which thought process is correct.
Note:
- It is generally believed that when most thinkers get the same answer, the answer may be correct. But you can't do it so superficially, because the correct answer may come from very few thinkers, or even no thinker gives the correct answer. For this reason, when you summarizing, you NEED adhere to the principles of professionalism and critical thinking, carefully identify these thought processes, and give a summary and final answer.
- If you realize that none of these thinkers have answered correctly, you can even learn from the wrong experiences in the thought process of these thinkers and re-think the given problem to give the answer you think is most correct.
- You need to consider language consistency. Your analysis and final output responses must be consistent with the language type of the given query. For example, if the query and each thinker are primarily in Chinese, then your analysis and responses must also be primarily in Chinese, too. If the query and each thinker are primarily in English, then your analysis and responses must also be primarily in English, too. By the way, if the language of the query and each thinker‘s response is inconsistent, then you MUST maintain consistency with the language type of the given query.
For the output format of your final answer after the summary, you should follow the similar format with thinkers:
- If the problem is mathematics or STEM and most thinkers have put the answer within boxed, your final answer after the summary should within boxed too.
- If the problem is code contest and most thinkers have put the result code within a block like "```", your final answer should also within the block.
- Your final output response DO NOT contain any analysis of these thinkers. Your final response must be a response to the given query, must follow the requirements and instructions in the query, and the style and format of the output must be consistent with those of the thinkers.
""".strip()

    elif summary_type == "General-Prompt":
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

    response_prompt = ""
    for ei, response in enumerate(parallel_reason_content_list):
        response_prompt += "# ----- Thinker #{} -----\n\n{}\n\n".format(ei + 1, response)
    prompt = prompt.replace("{problem}", query).replace("{response_prompt}", response_prompt)

    # prompt = "<|im_start|>user:\n{prompt}\n<|im_end|>\n\n<|im_start|>assistant:".format(prompt=prompt)

    return prompt

def judging_prompting(problem, target, answer, group_name):

    # math类的问题
    if group_name in ["AIME2024_with_figure_duplicate_31", "AIME2025_with_figure_duplicate_31", "BeyondAIME_Fix_0702_Fork9", "HMMT_2025_dup_32"]:

        prompt = """
You are a precise mathematical answer checker. Your task is to determine whether a student's answer matches the reference answer for a given mathematical question.
**Input**
- **Question:** "{question}"
- **Reference Answer:** "{answer}"
- **Student's Answer:** "{extract_answer}"

### 1. **MATHEMATICAL EQUIVALENCE IS KEY**
- Focus on mathematical meaning, not specific format or presentation
- Examples of CORRECT equivalences:
- Reference: "a < b < c", Student: "c > b > a" → **CORRECT** (same relationship)
- Reference: "x - y + 1 = 0", Student: "x + 1 = y" → **CORRECT** (algebraically equivalent)
- Reference: "x = 2π", Student: "x = 6.283..." → **CORRECT** (numerically equivalent)
- Reference: "sin(θ) = 1/2", Student: "θ = π/6 + 2πn or θ = 5π/6 + 2πn" → **CORRECT** (if reference also shows general solution)
- But the student must show ALL equivalent solutions if multiple exist

### 2. **COMPLETENESS IS MANDATORY**
- If the reference answer contains multiple solutions/answers, the student MUST provide ALL of them
- **A partial answer is ALWAYS INCORRECT, even if what's provided is mathematically correct**
- Example: Reference "x = 2 or x = -2", Student "x = 2" → **INCORRECT** (missing x = -2)
- Example: Reference "θ = π/4, 3π/4, 5π/4, 7π/4", Student "θ = π/4, 3π/4" → **INCORRECT** (missing solutions)

### 3. **Variable Usage Restrictions**
- Student answers may ONLY contain:
- Common mathematical constants: π, e
- Variables explicitly mentioned in the question
- Standard mathematical operators and functions
- Any unauthorized variables → **INCORRECT**

### 4. **Units Policy**
- Missing units that are implied by the question context are acceptable

## Important Instructions:
- **DO NOT solve the question yourself**
- **DO NOT verify if the answers are correct solutions to the problem**
- **ONLY compare mathematical equivalence between student's answer and reference answer**
- **Accept any mathematically equivalent form or representation**

## Remember:
**INCOMPLETE = INCORRECT, regardless of partial correctness.**
**Mathematical equivalence = CORRECT, regardless of presentation format.**

## Response Format:
**Reason**:
    -Identify what's missing or incorrect
    -Provide mathematical justification
**Judgment**: [CORRECT/INCORRECT]

""".strip()

    else:
        # 其他类answer比较问题
        prompt = """
You are a great teacher, give you a question, the corresponding reference answer and a student's answer. You should check whether the student's answer is correct.
**Input**
- **Question:** "{question}"
- **Reference Answer:** "{answer}"
- **Student's Answer:** "{extract_answer}"

**Note**
1. If the question is a multi-choice problem, the reference answer may contains the option name (like "A.", "B.", "C.", "D.", "(A)", "(B)", "(C)", "(D)", etc.) and the content. If a student's answer contains the correct option or the correct content, it is marked as correct; otherwise, it is marked as incorrect.
For example:
- if reference answer is "C. 1/2*\pi", and the student's answer is "C", this means the student's answer is CORRECT, because the answer is C.
- if reference answer is "(B) 0.05", and the student's answer is "1/20", this means the student's answer is CORRECT, because the correct answer is 0.05 and student's answer is 1/20 which is equal to 0.05.
- if reference answer is "D. 10, \lambda^(3)", and the student's answer is "B", this means the student's answer is INCORRECT, because the answer is not "D".

2. If the question is not a multi-choice problem, please only match whether the student's answer is match to the reference answer.

## Response Format:
**Reason**:
    -Identify what's missing or incorrect
    -Provide mathematical justification
**Judgment**: [CORRECT/INCORRECT]
"""




    prompt = prompt.replace("{question}", problem).replace("{answer}", target).replace("{extract_answer}", answer)
    return prompt


def extract_judgment_correct(text):
    # 抽取模型model eval的结果，正确返回1，错误返回0
    keyword = 'Judgment'
    # 查找最后一个“Judgment”的索引
    last_judgment_index = text.rfind(keyword)

    if last_judgment_index == -1:
        print("未在文本中找到关键词 'Judgment'。")
        return 0

    # 提取“Judgment”之后的内容
    substring_after = text[last_judgment_index + len(keyword):]

    # 将内容转换为大写以实现不区分大小写的搜索
    substring_upper = substring_after.upper()

    # 检查“YES”或“NO”
    if 'INCORRECT' in substring_upper:
        return 0
    elif 'CORRECT' in substring_upper:
        return 1
    else:
        print("在最后一个 'Judgment' 之后未找到 'YES' 或 'NO'。")
        return 0

def show_chat_template(tokenizer, prompt, enable_chat_template=False):
    if enable_chat_template:
        message = [
            # {"role": "system", "content": "You are a helpful assistant."},
            # {"role": "system", "content": "You are an expert in mathematics and Lean 4."},
            {"role": "user", "content": prompt}
        ]
        text = tokenizer.apply_chat_template(
            message,
            tokenize=False,
            add_generation_prompt=True
        )
    else:
        text = prompt
    print(text)


def multi_call_api(summary_request_list, llm_agent, args, idx, group2summary_request, group, save_file_name):
    new_summary_request_list = list()
    for ei, request_list in enumerate(summary_request_list):
        print("batch {} - summarizing for example #{} (total: {})".format(idx, ei + 1, len(summary_request_list)))
        prompt = request_list["summary_reason_prompt"]

        if len(request_list["summary_reason_content"]) == args.summary_k:
            print("find summary content cache for example #{}, so skip.".format(ei + 1))
            continue
        if len(request_list["summary_reason_content"]) > 0:
            print("find summary content cache, but only has {} (total need {})".format(len(request_list["summary_reason_content"]), args.summary_k))
        need_summary_num = args.summary_k - len(request_list["summary_reason_content"])

        print(f"[batch {idx} - token num for summarizing: {request_list['parallel_reason_token_num']}]")
        summary_outputs = llm_agent.generate(prompt=prompt, duplicate_n=need_summary_num, max_tokens=100000)
        request_list["summary_reason_content"].extend(summary_outputs)
        new_summary_request_list.append(request_list)
        PROCESS_INFO[idx] = [len(new_summary_request_list), len(summary_request_list)]
        show_current_stage = ""
        for ei, info in enumerate(PROCESS_INFO):
            if ei == idx:
                show_current_stage += f"    - [Batch {ei}]  Finished: {info[0]}, Total: {info[1]}\n"
        print(f"============================================\n【Show Process Stage】\n{show_current_stage}\n============================================")
        # 临时存储一下该线程下的结果，防止意外
        group2summary_request[group] = new_summary_request_list

        if len(save_file_name) > 200:
            save_file_name = save_file_name[:100]
        save_json(os.path.join(args.save_dir, save_file_name.replace(".json", f".thread_{idx}.json")), group2summary_request)

    print(f"Batch {idx} is finished")
    return new_summary_request_list

PROCESS_INFO = list() # 用于全局记录每个process的进度


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--summary_model', type=str, default=None) # 用于summary的model
    arg_parser.add_argument('--summary_model_type', type=str, default=None) # summary的model的类型（vllm：使用vllm加载、api：使用API启动）
    arg_parser.add_argument('--summary_model_api_address', type=str, default=None) # 当summary的model为API时，则键入API地址（需要API Seving画布启动）
    arg_parser.add_argument('--judger_model', type=str, default=None) # 用于对summary进行model eval打分
    arg_parser.add_argument('--input_data_path', type=str, default=None) # 画布评测推理的结果（处理后）
    arg_parser.add_argument('--data_name', type=str, default=None) # 指定评测数据名称
    arg_parser.add_argument('--summary_type', type=str, default=None) # summary名称
    arg_parser.add_argument('--permutation', type=str, default="Shuffle-All-Response") # summary排列方式
    arg_parser.add_argument('--save_dir', type=str, default=None) # 结果存储位置
    arg_parser.add_argument('--think_start_tag', type=str, default="<think>")
    arg_parser.add_argument('--think_end_tag', type=str, default="</think>")
    arg_parser.add_argument('--reason_k', type=int, default=None) # reasoning过程的采样数k
    arg_parser.add_argument('--summary_k', type=int, default=4) # summary过程的采样生成数
    arg_parser.add_argument('--max_tokens', type=int, default=80000) # 最大token
    arg_parser.add_argument('--skip_summary', action='store_true') # 是否跳过summary直接进行model eval
    arg_parser.add_argument('--skip_model_eval', action='store_true') # 是否跳过model eval # 当同时设置skip_summary和skip_model_eval时，表明只为了获取采样的parallel think，summary则通过其他途径来进行

    args = arg_parser.parse_args()

    print("transformers: {}".format(transformers.__version__))

    summary_model_api_address = args.summary_model_api_address
    thread_num = 1
    summary_model_api_address_list = list()
    if summary_model_api_address is not None:
        summary_model_api_address_list = summary_model_api_address.split(",")
        thread_num = len(summary_model_api_address_list)
        print("You have set multi-process with {} threads".format(thread_num))

    data_name = args.data_name
    summary_model_name = args.summary_model.split("/")[-1] if not args.summary_model.endswith("/") else args.summary_model.split("/")[-2]
    enable_chat_template = True


    tokenizer = AutoTokenizer.from_pretrained(args.summary_model, trust_remote_code=True)

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)


    """
    读取模型预测的结果
    """
    print("[Reading Inference Information]")
    thinking_info = read_json(args.input_data_path)
    think_model_name = thinking_info["model_name"]
    thinking_results = thinking_info["results"]

    order, scale, component = args.permutation.split("-")

    group2summary_request = dict()

    # 遍历每个数据集（group），仅保留选中的数据集
    for group_name, cur_query2results in thinking_results.items():
        if group_name == data_name:
            if group_name not in group2summary_request.keys():
                group2summary_request[group_name] = list()


            query_list = list(cur_query2results.keys())
            for query, result_list in cur_query2results.items():
                problem = result_list[0]["problem"]
                target = result_list[0]["target"]
                for t in result_list:
                    assert target == t["target"]
                # 遍历每个query，随机采样k个response用于后续的summary
                cur_response_list, total_token_num, cur_metric, correctness_list = permutating(result_list, args.reason_k, order, scale, component, tokenizer=tokenizer, max_tokens=args.max_tokens, think_start_tag=args.think_start_tag, think_end_tag=args.think_end_tag)
                try:
                    parallel_reason_score_list = [int(i) for i in correctness_list]
                except:
                    parallel_reason_score_list = [0] * len(correctness_list)

                group2summary_request[group_name].append({
                    "query": query,
                    "problem": problem,
                    "target": target,
                    "parallel_reason_content": cur_response_list,
                    "parallel_reason_content_score": parallel_reason_score_list,
                    "parallel_reason_thought_num": len(cur_response_list),
                    "parallel_reason_token_num": total_token_num,
                    "parallel_reason_metric": cur_metric,
                    "summary_reason_prompt": None,
                    "summary_reason_content": list(),
                    "summary_reason_content_model_eval_score": None,
                    "summary_reason_metric": None,
                })

    print("\n====== Use for summary eval num ======")
    for group, summary_request_list in group2summary_request.items():
        print("{}:\t{}".format(group, len(summary_request_list)))

    # print("\n====== One case ======")
    # print(group2summary_request[data_name][0])

    print("[Prompting]")
    summary_prompt_dict = dict()
    for group, summary_request_list in group2summary_request.items():
        if group not in summary_prompt_dict.keys():
            summary_prompt_dict[group] = list()
        for request_list in summary_request_list:
            problem = request_list["problem"]
            parallel_reason_content = request_list["parallel_reason_content"]
            prompt = prompting(args.summary_type, problem, parallel_reason_content)
            request_list["summary_reason_prompt"] = prompt
            summary_prompt_dict[group].append(prompt)

        # print("\n====== One Prompt =======")
        # print(summary_prompt_dict[group][0])
        # show_chat_template(
        #     tokenizer=tokenizer,
        #     prompt=summary_prompt_dict[group][0],
        #     enable_chat_template=enable_chat_template,
        #     )

        print("\n[parallel response token num: {}]".format(summary_request_list[0]["parallel_reason_token_num"]))


    save_file_name = "{}_[think-{}-k-{}]_[summary-{}-k-{}]_{}_{}.json".format(
        data_name, think_model_name, args.reason_k, summary_model_name, args.summary_k, args.summary_type, args.permutation,
    )

    if len(save_file_name) >=256:
        save_file_name = save_file_name.replace(".json", "")
        save_file_name = save_file_name[:230] + ".json"

    print("save path is: ", os.path.join(args.save_dir, save_file_name))
    # 如果已经存在缓存，则直接读取
    if os.path.exists(os.path.join(args.save_dir, save_file_name)):
        print("[Find cache, now loading ...]")
        group2summary_request = read_json(os.path.join(args.save_dir, save_file_name))

    print("[Metric of Each Thinking]")
    for group, summary_request_list in group2summary_request.items():
        meank, passk, majork = 0, 0, 0
        for request_list in summary_request_list:
            meank += request_list["parallel_reason_metric"][f"Mean@{args.reason_k}"]
            passk += request_list["parallel_reason_metric"][f"Pass@{args.reason_k}"]
            majork += request_list["parallel_reason_metric"][f"Major@{args.reason_k}"]
        print(f"[{group} Parallel-Think Mean@{args.reason_k}]:\t{meank / len(summary_request_list)}")
        print(f"[{group} Parallel-Think Pass@{args.reason_k}]:\t{passk / len(summary_request_list)}")
        print(f"[{group} Parallel-Think Major@{args.reason_k}]:\t{majork / len(summary_request_list)}")


    show_one_response = True

    if not args.skip_summary:

        # 这里进行summary
        if args.summary_model_type == "vllm":
            print("[Loading Summary Model (vLLM)]")
            llm_agent = vLLMAgent(model_name_or_path=args.summary_model)


            print("Save file name: {}".format(save_file_name))

            print("[Summarizing]")
            for group, summary_request_list in group2summary_request.items():
                print("===== Group: {} =====".format(group))
                for ei, request_list in enumerate(summary_request_list):
                    print("summarizing for example #{} (total: {})".format(ei + 1, len(summary_request_list)))
                    if len(request_list["summary_reason_content"]) == args.summary_k:
                        print("find summary content cache for example #{}, so skip.".format(ei + 1))
                        continue
                    if len(request_list["summary_reason_content"]) > 0:
                        print("find summary content cache, but only has {} (total need {})".format(len(request_list["summary_reason_content"]), args.summary_k))
                    need_summary_num = args.summary_k - len(request_list["summary_reason_content"])

                    prompt = request_list["summary_reason_prompt"]
                    print(f"[token num for summarizing: {request_list['parallel_reason_token_num']}]")
                    summary_outputs = llm_agent.generate(prompts=[prompt] * need_summary_num, enable_chat_template=enable_chat_template, max_tokens=100000)
                    request_list["summary_reason_content"].extend(summary_outputs)

                    if show_one_response:
                        show_one_response = False
                        print("[Show One Response Start]")
                        print(summary_outputs[0])
                        print("[Show One Response End]")

                    print("Saving ...")
                    save_json(os.path.join(args.save_dir, save_file_name), group2summary_request)

            del llm_agent
            torch.cuda.empty_cache()

        elif args.summary_model_type == "api":
            print("[Loading Summary Model (API): {}]".format(args.summary_model_api_address))

            llm_agent = APIAgent(model_name=summary_model_name, api_address=args.summary_model_api_address, tokenizer=tokenizer)

            print("Save file name: {}".format(save_file_name))
            print("[Summarizing from API]")

            for group, summary_request_list in group2summary_request.items():
                print("[Loading Summary Model (API): {}]".format(args.summary_model_api_address))

            # llm_agent = APIAgent(model_name=summary_model_name, api_address=args.summary_model_api_address, tokenizer=tokenizer)
            llm_agent_list = list()
            for ei, summary_model_api_address in enumerate(summary_model_api_address_list):
                llm_agent = APIAgent(model_name=summary_model_name, api_address=summary_model_api_address, tokenizer=tokenizer, info="Batch {}".format(ei))
                llm_agent_list.append(llm_agent)

            print("Save file name: {}".format(save_file_name))
            print("[Summarizing from API]")


            for group, summary_request_list in group2summary_request.items():
                print("===== Group: {} =====".format(group))
                print("===== Data Split =====")
                # 将评测数据切分为thread_num份
                batch_size = int((len(summary_request_list) - 1) / thread_num) + 1
                summary_request_batch = [summary_request_list[i: i + batch_size] for i in range(0, len(summary_request_list), batch_size)]
                # 刷新进度
                PROCESS_INFO = list() # [[finish_num, total_num], ...]
                for ei, request_list in enumerate(summary_request_batch):
                    PROCESS_INFO.append([0, len(request_list)])

                with multiprocessing.Pool(processes=thread_num) as pool:
                    results = list(tqdm(pool.starmap(multi_call_api, [(chunk, llm_agent_list[idx], args, idx, group2summary_request, group, save_file_name) for idx, chunk in enumerate(summary_request_batch)]), total=len(summary_request_batch), desc="API Call进度"))

                summary_request_result_list = [request_result for request_list in results for request_result in request_list]
                assert len(summary_request_result_list) == len(summary_request_list)
                group2summary_request[group] = summary_request_result_list

                print("Saving ...")
                save_json(os.path.join(args.save_dir, save_file_name), group2summary_request)
                time.sleep(5)


        print("[Finished Summarizing, Now Saving Summarized Results]")

        save_json(os.path.join(args.save_dir, save_file_name), group2summary_request)

    if not args.skip_model_eval:
        # 如果跳过summary，相当于直接读取缓存的结果进行model eval
        if os.path.exists(os.path.join(args.save_dir, save_file_name)):
            group2summary_request = read_json(os.path.join(args.save_dir, save_file_name))
        else:
            group2summary_request = None
            raise FileNotFoundError
    else:
        print("YOU Have set skip summary and model eval, so only save sampled parallel thinking process, and all stop now.")
        save_json(os.path.join(args.save_dir, save_file_name), group2summary_request)
        sys.exit()



    print("[Loading Judger Model]")
    llm_judger = vLLMAgent(model_name_or_path=args.judger_model)
    judger_model_name = args.judger_model.split("/")[-1] if not args.judger_model.endswith("/") else args.judger_model.split("/")[-2]

    print("[Model Eval Scoing]")
    for group, summary_request_list in group2summary_request.items():
        print("===== Group: {} =====".format(group))
        for ei, request_list in enumerate(summary_request_list):
            print("model evaling for example #{} (total: {})".format(ei + 1, len(summary_request_list)))
            problem = request_list["problem"]
            target = request_list["target"]
            summary_reason_content = request_list["summary_reason_content"] # 包含多次summary的采样生成结果
            print("Judger results from platform for {} parallel thought: {}".format(args.reason_k, request_list["parallel_reason_content_score"]))

            if "summary_reason_content_model_eval_score" not in request_list.keys() or request_list["summary_reason_content_model_eval_score"] is None:
                request_list["summary_reason_content_model_eval_score"] = {}

            if judger_model_name not in request_list["summary_reason_content_model_eval_score"].keys():
                # 用于存储每个summary的model eval结果
                request_list["summary_reason_content_model_eval_score"][judger_model_name] = list()


            if "summary_reason_metric" not in request_list.keys() or request_list["summary_reason_metric"] is None:
                request_list["summary_reason_metric"] = {}
            if judger_model_name not in request_list["summary_reason_metric"].keys():
                request_list["summary_reason_metric"][judger_model_name] = {
                    f"Mean@{args.summary_k}": 0,
                    f"Pass@{args.summary_k}": 0,
                }

            # 遍历每个summary内容，进行model eval
            summary_avg_acc = 0
            summary_passk = 0
            for summary in summary_reason_content:
                if "\\boxed" in summary:
                    # 取最后一个boxed作为答案
                    answer_sequence = "\\boxed" + summary.split("\\boxed")[-1]
                    answer_sequence = extract_answer(answer_sequence)
                else:
                    # # 如果没有boxed，则取最末尾的20个word作为上下文
                    # answer_sequence = " ".join(summary.split(" ")[-20:])
                    # 如果没有boxed，则取最末尾的三段作为输入
                    summary = summary.split(args.think_end_tag)[-1]
                    answer_sequence = "\n\n".join(summary.split("\n\n")[-3:])


                # 重复judger 7次，并投票
                # 根据不同类型的任务选择不同的model eval prompt

                judger_prompt = judging_prompting(problem, target, answer_sequence, group)
                judger_outputs = llm_judger.generate(prompts=[judger_prompt] * 7, enable_chat_template=True, add_system=True, max_tokens=16384)
                # 0表示当前的summary结果错误，1表示正确
                judger_results = [extract_judgment_correct(output) for output in judger_outputs]
                # 投票，如果1的数量超过3（一共7次eval）个，则认为当前的summary正确

                print("judger results from model eval for summary ({} times): {}".format(len(judger_results), judger_results))
                if sum(judger_results) >= 4:
                    request_list["summary_reason_content_model_eval_score"][judger_model_name].append(1)
                    summary_avg_acc += 1
                    summary_passk = 1 # 只要多次summary中出现了一次正确的，passk则为1，后续不再改变
                else:
                    request_list["summary_reason_content_model_eval_score"][judger_model_name].append(0)
                    summary_avg_acc += 0

            # 当前query summary的平均acc
            summary_avg_acc = summary_avg_acc / len(summary_reason_content) if len(summary_reason_content) > 0 else 0

            request_list["summary_reason_metric"][judger_model_name] = {
                f"Mean@{args.summary_k}": summary_avg_acc,
                f"Pass@{args.summary_k}": summary_passk,
            }

            print("Saving ...")
            save_json(os.path.join(args.save_dir, save_file_name), group2summary_request)

    print("[Finished Summarizing, Now Saving Summarized Results]")

    save_json(os.path.join(args.save_dir, save_file_name), group2summary_request)
    print("Saved to {}".format(os.path.join(args.save_dir, save_file_name), group2summary_request))

    print("[Metric]")
    for group, summary_request_list in group2summary_request.items():

        # 计算对应Parallel Think本身的Pass、Major指标
        meank, passk, majork = 0, 0, 0
        for request_list in summary_request_list:
            meank += request_list["parallel_reason_metric"][f"Mean@{args.reason_k}"]
            passk += request_list["parallel_reason_metric"][f"Pass@{args.reason_k}"]
            majork += request_list["parallel_reason_metric"][f"Major@{args.reason_k}"]
        print(f"[{group} Parallel-Think Mean@{args.reason_k}]:\t{meank / len(summary_request_list)}")
        print(f"[{group} Parallel-Think Pass@{args.reason_k}]:\t{passk / len(summary_request_list)}")
        print(f"[{group} Parallel-Think Major@{args.reason_k}]:\t{majork / len(summary_request_list)}")


        meank, passk = 0, 0
        for request_list in summary_request_list:
            meank += request_list["summary_reason_metric"][judger_model_name][f"Mean@{args.summary_k}"]
            passk += request_list["summary_reason_metric"][judger_model_name][f"Pass@{args.summary_k}"]
        print(f"[{group} Summary Mean@{args.summary_k}]:\t{meank / len(summary_request_list)}")
        print(f"[{group} Summary Pass@{args.summary_k}]:\t{passk / len(summary_request_list)}")
