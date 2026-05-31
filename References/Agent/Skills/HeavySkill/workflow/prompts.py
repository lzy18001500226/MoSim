"""Prompt templates for HeavySkill sequential deliberation."""

from typing import List


SUMMARY_PROMPT_GENERAL_EN = """
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
- If it's a complex reasoning task, such as logical reasoning, mathematical reasoning, coding competitions, or common-sense reasoning problems, etc., you NEED to carefully analyze the thinkers' responses. After analysis, you need to provide a solution that can resolve the query.
- If none of the above applies, you can decide whether you need to analyze the situation carefully based on the actual circumstances. If you are really unsure, you can choose one of these thinkers' responses as a backup plan, but it should be emphasized that this is a last resort and should not be used as a general practice.

Last but not least:
- Please note that you DO NOT simply concate together or list all the thinkers' outputs. Your role and goal are the same as these thinkers, i.e., ultimately answer the query. The difference between you and these thinkers is that you can conduct some analysis based on their responses, summarize or select the best response for the user.
- You need to consider language consistency. Your analysis and final output responses must be consistent with the language type of the given query. For example, if the query and each thinker are primarily in Chinese, then your analysis and responses must also be primarily in Chinese, too. If the query and each thinker are primarily in English, then your analysis and responses must also be primarily in English, too. By the way, if the language of the query and each thinker's response is inconsistent, then you MUST maintain consistency with the language type of the given query.
- Your final output response DO NOT contain any analysis of these thinkers. Your final response must be a response to the given query, must follow the requirements and instructions in the query, and the style and format of the output must be consistent with those of the thinkers.
""".strip()


SUMMARY_PROMPT_GENERAL_CN = """
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


SUMMARY_PROMPT_STEM = """
You are a great reasoner.
Here is a problem, and multiple thinkers attempt to give their thought processes independently.
Each thinker has written its own thought process towards the final answer. Each thinker is encouraged to take the other thinkers' progress into account to reach the final answer.

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
- You need to consider language consistency. Your analysis and final output responses must be consistent with the language type of the given query. For example, if the query and each thinker are primarily in Chinese, then your analysis and responses must also be primarily in Chinese, too. If the query and each thinker are primarily in English, then your analysis and responses must also be primarily in English, too. By the way, if the language of the query and each thinker's response is inconsistent, then you MUST maintain consistency with the language type of the given query.
For the output format of your final answer after the summary, you should follow the similar format with thinkers:
- If the problem is mathematics or STEM and most thinkers have put the answer within boxed, your final answer after the summary should within boxed too.
- If the problem is code contest and most thinkers have put the result code within a block like "```", your final answer should also within the block.
- Your final output response DO NOT contain any analysis of these thinkers. Your final response must be a response to the given query, must follow the requirements and instructions in the query, and the style and format of the output must be consistent with those of the thinkers.
""".strip()


PROMPT_REGISTRY = {
    "general": {"en": SUMMARY_PROMPT_GENERAL_EN, "cn": SUMMARY_PROMPT_GENERAL_CN},
    "stem": {"en": SUMMARY_PROMPT_STEM, "cn": SUMMARY_PROMPT_STEM},
}


def format_thinkers_prompt(trajectories: List[str]) -> str:
    """Format a list of reasoning trajectories into the thinker block."""
    parts = []
    for i, traj in enumerate(trajectories, 1):
        parts.append(f"# ----- Thinker #{i} -----\n\n{traj}\n")
    return "\n".join(parts)


def build_summary_prompt(
    query: str,
    trajectories: List[str],
    prompt_type: str = "general",
    language: str = "en",
) -> str:
    """Build the full summary prompt from query and parallel trajectories."""
    lang = language if language in ("en", "cn") else "en"
    template = PROMPT_REGISTRY.get(prompt_type, PROMPT_REGISTRY["general"])
    prompt_template = template.get(lang, template["en"])

    response_prompt = format_thinkers_prompt(trajectories)
    return prompt_template.replace("{problem}", query).replace("{response_prompt}", response_prompt)
