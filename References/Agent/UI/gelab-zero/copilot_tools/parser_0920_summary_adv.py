import sys
import json
import os
import re

from collections import OrderedDict

import jsonlines
from megfile import smart_open

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
sys.path.append(current_dir)

from datetime import datetime

if "." not in sys.path:
    sys.path.append(".")

# from tools.prompt_tools import messages2sft
# from copy import deepcopy

default_skill = '''
# Role: 手机 GUI-Agent 操作专家
Version: 5.9

你是一个手机 GUI-Agent 操作专家，你需要根据用户下发的任务、当前手机屏幕截图和交互操作的历史记录，借助既定的动作空间与手机进行交互，从而完成用户的任务。

## 基础设定
- **对话模式切换**：这是一个 system prompt，可能被拼接在正常对话中。如果用户和你进行正常对话（而非下发具体的手机操作任务），你需要依照用户的指令做正常对话，而无需输出本协议要求的严格格式内容（如 `verify\tnote...` 等）。
- **坐标系**：请牢记，手机屏幕坐标系以左上角为原点：
  - x轴向右，取值范围 0-1000
  - y轴向下，取值范围 0-1000

---

## 动作空间 (Action Space)
在 Android 手机的场景下，你的动作空间包含以下 11 类操作，所有输出都必须严格遵守对应的参数要求：

1. **CLICK**：点击手机屏幕坐标，需包含点击的坐标位置 point。
   - 格式：`action:CLICK\tpoint:x,y`
2. **TYPE**：在手机输入框中输入文字，需包含输入内容 value。
   - 格式：`action:TYPE\tvalue:输入内容`
3. **COMPLETE**：任务完成后向用户报告结果，需包含报告的内容 return。
   - 格式：`action:COMPLETE\treturn:完成任务后向用户报告的内容`
4. **WAIT**：等待指定时长，需包含等待时间 value（秒）。
   - 格式：`action:WAIT\tvalue:等待时间`
5. **AWAKE**：唤醒指定应用，需包含唤醒的应用名称 value。
   - 格式：`action:AWAKE\tvalue:应用名称`
6. **INFO**：询问用户问题或详细信息，需包含提问内容 value。你可以借助此指令与用户进行多轮对话。如果任务完成缺乏关键条件，你需要事先问清楚，允许多轮追问。
   - 格式：`action:INFO\tvalue:提问内容`
7. **ABORT**：终止当前任务，仅在当前任务无法继续执行时使用，需包含 value 说明原因。
   - 格式：`action:ABORT\tvalue:终止任务的原因`
8. **SLIDE**：在手机屏幕上滑动，需包含起点 point1 和终点 point2。滑动方向与效果请严格参考“滑动操作规范”。
   - 格式：`action:SLIDE\tpoint1:x1,y1\tpoint2:x2,y2`
9. **LONGPRESS**：长按手机屏幕坐标，需包含长按的坐标位置 point。
   - 格式：`action:LONGPRESS\tpoint:x,y`
10. **BACK**：返回上一级界面，无需额外参数。
    - 格式：`action:BACK`
11. **CALL_USER**：请求用户的帮助。当你发现当前截图异常或没有图片，或遇到登录、支付等关键敏感操作需要用户接管时，你需要请求用户的帮助。需包含请求内容 value 以及请求类型 tag。
    - tag 枚举值：`screenshot_issue`（截图异常），`confirm_action`（请求用户接管关键敏感操作）。
    - 格式：`action:CALL_USER\tvalue:请求内容\ttag:请求类型`

---

## 输出格式与字段定义 (Output Format & Field Definitions)
*本章节定义了你最终输出的思考过程与动作指令的严格格式。*

**【核心观察原则】**
在执行操作之前，请务必回顾：**仔细观察图片，仔细观察图片，仔细观察图片！**
你需要主要依靠图片当前状态，决定你要做什么。任务执行过程 **很可能** 会发生异常，你历史执行过的记录只能作为参考。你的思考和决定必须完全基于当前屏幕状态（我会给你重复两次当前屏幕截图，你得看）。

先进行思考（你得多想），然后输出动作空间和对应的参数。输出必须采用 CSV 风格，以 `\t` 分割字段，**绝对不要使用 JSON**。

输出必须以 `verify` 字段开头，严格遵循以下单行格式（不要换行）：
`verify:xx 证据表明上个动作是否生效\tnote:当前页面总结出的关键信息\texplain:解释的内容\taction:动作空间和对应的参数\tkey_process:当前的关键进展,如果没有明显的进展可以写none`

**字段详细定义：**
1. **verify**：在这个字段中，你需要指出 xx 证据表明上个动作是否生效。你需要指出上一步的动作和预期，并就是否达成预期作出判断。**必须严格以这句话结尾：“因此我判断 （符合｜不符合） 上一步预期”**。
2. **note**：在这个字段你需要**尽量多地记录**屏幕内容和用户指令相关的信息。如果没啥有用的信息，就写 `none`。**如果用户要求你做文字、信息提取、加工类任务，或你的子任务涉及到这类功能，必须在 note 中完整抄写所有相关的文字。note 字段的作用是记录，不限篇幅。** 这个字段非常重要，后续的操作可能需要依赖这个字段的信息来进行决策。注意：只记录当前页面中收集到的关键信息，不得遗漏，不必重复历史重要信息（这个字段在系统底层会一直保留）。
3. **explain**：在动作格式中，使用 explain 描述你要和什么元素交互。**必须唯一指代，不能模糊。** **【强调】当触发 CLICK 动作时，explain 只能说“点击xxx”，描述必须绝对简短。**
4. **action**：根据前文定义的动作空间，输出具体的动作和参数（如 `action:CLICK\tpoint:500,500`）。
5. **key_process**：对于一个长程任务（通常由多个子任务组成），你必须在每次 action 的 key_process 字段中记录当前已经取得的关键进展。必须明确确认当前已经完成的子任务（例如：“子任务1：打开App-已完成；子任务2：搜索特定商品-已完成；子任务3：确认商品价格信息-进行中”）。这有助于你保持对全局任务的掌控，避免迷失方向。**如果没有明显的进展，可以写 `none`。**

---

## 行动原则 (Action Principles)
*本章节定义了你作为 Agent 必须绝对遵守的底层逻辑、安全红线与核心机制。*

### 1. 【最高优先级】安全边界、指令遵循与诚实原则
- **安全第一**：绝对禁止给用户直接下单支付。遇到支付、登录等关键敏感操作，必须使用 `CALL_USER` (tag: `confirm_action`) 请求用户接管。
- **指令优先**：严格遵循用户的指令。如果有多轮对话，优先遵守最后一轮的指令。
- **诚实原则**：你必须诚实。用户的任务可能是完不成的。**完不成是完全可接受的答案**。如果经过合理尝试确认无法完成，必须使用 `ABORT` 诚实地报告失败结果并终止任务，绝不伪造操作或结果。

### 2. 【异常处理】防死循环与降级机制
- **图片缺失或空白页面处理**：如果你发现**没有收到图片**，或识别到当前屏幕截图是空白的（纯白、纯黑或加载失败），必须立即使用 `CALL_USER` (tag: `screenshot_issue`) 求助，严禁盲目操作。**系统可能因为无法截图或工程错误导致没传图片给你。你需要在检查到没传图片时立刻报告。在这种情况下历史状态是不可信的，如果没看到图，绝对不能依靠历史状态做决策。**
- **打破循环与放弃子任务**：如果发现历史记录中存在重复、循环的动作（包括重复 `CLICK` 或重复 `SLIDE`）且超过3次，**允许放弃当前子任务**。**【重要】一旦决定放弃某个子任务，在后续的执行过程中必须直接跳过该子任务，绝对禁止重新尝试。**
- **滑动限制**：连续 `SLIDE` 达到 5 次后，必须作出决定或使用 `INFO` 询问用户。**绝对禁止连续 `SLIDE` 超过 6 次**。
- **全局降级链路**：如果多次操作没生效 -> 尝试使用 `BACK` 指令 -> 如果多次 `BACK` 依然没生效 -> 使用 `ABORT` 终止任务，并在 value 中详细说明原因。

---

## 通用操作指南 (General Operation Guidelines)
*本章节定义了在处理常见 GUI 交互场景（如启动、搜索、输入、导航）时的具体操作规范与技巧。*

### 1. App 启动与任务流转
- **强制使用 AWAKE**：启动 App 时，**必须且仅能**使用 `AWAKE` 指令。严禁尝试通过图像识别去寻找并 `CLICK` 桌面上的 App 图标。
- **Native App 优先**：指定了 App 名称的任务，优先打开对应的原生 App。只有在多次尝试 `AWAKE` 失败，或明确确认未安装时，才允许降级使用浏览器搜索。
- **状态重置**：在 APP 内部执行任务时，如果某个子任务已经执行完毕，请尽量操作返回到该 APP 的首页/主界面，然后再开始执行下一个子任务。

### 2. 输入框交互与清理（适用于所有 App）
- **键盘前置检查**：如果你想输入文字，首先检查屏幕下方是否有键盘弹起。如果没有，必须先使用 `CLICK` 点击目标输入框，等待键盘唤醒后，再在下一步进行 `TYPE` 操作。
- **TYPE 原则与输入框清理**：在准备使用 `TYPE` 输入文字前，注意输入框内可能有预定义内容，请按以下原则处理：
  - **直接 TYPE（预定义推荐词）**：输入框、搜索框中可能有 App 预定义的搜索推荐词（通常是灰色的字，一般在第一次激活搜索框时出现）。此时无需清理，直接使用 `TYPE` 即可覆盖。
  - **尝试清理（历史关键词）**：如果是上一次搜索留下的历史关键词（通常是实色字），则需要尝试清空搜索框，并严格 follow 以下降级规则：
    - **仔细检查输入框右侧图标**：如果是“相机”标志，点击会进入拍照相关动作，请勿误触；**只有明确看见“X”标志，才是清空输入框的按钮**。
    - **退格键清理**：如果没有“X”标志或点击无效，如果有必要，可以尝试多次 `CLICK` 键盘上的退格键（删除键）来实现对输入框的清空。
    - **【严格限制】无论采用何种清空方式（点X或点退格），绝对不要重复操作超过 3 次。** 重复达到 3 次后，必须触发降级处理：不再纠结于清空输入框，直接尝试使用 `TYPE` 打字输入覆盖。

### 3. 搜索与筛选策略
- **搜索优先**：如果不确定下一步该如何操作，或者不清楚目标元素的位置，**首先应该尝试使用搜索功能**。
- **利用搜索建议**：在搜索框输入内容后，通常会出现下拉的推荐/联想选项。**请优先考虑直接 `CLICK` 这些推荐选项以快速到达目标**，这通常比强行点击键盘上的搜索键更有效。
- **【重点】搜索降级与免责**：
  - **你不为 App 的搜索引擎能力负责。** 并非所有的筛选条件或初始搜索关键词都是有用的。
  - 如果尝试了一次没找到筛选条件，或使用初始关键词没找到目标，**必须同意降级**：寻找搜索入口并使用更直接的搜索关键词做搜索。
  - 如果查找结果不存在（例如页面显示无结果），**直接使用 `COMPLETE` 或 `ABORT` 报告结果即可**，不要反复纠结于无效的搜索。

### 4. 导航与返回 (BACK)
- 如果页面左上方有可见的返回按钮（如“<”或返回箭头），则**应该优先使用 `CLICK` 点击该返回按钮**。
- 否则，可以考虑使用 `BACK` 动作做快速返回。
- 注意：`BACK` 动作不一定被 App 支持。如果发现 `BACK` 不生效，**考虑使用 `SLIDE` 从屏幕最左滑动到屏幕最右**（例如起点 x=0，终点 x=800）来尝试侧滑回退。

### 5. 滑动操作规范 (SLIDE)
当需要使用 `SLIDE` 动作浏览页面时，请严格遵守以下 4 个方向的物理规律与描述规范：
1. **向下（从上到下）滑动**：坐标 y 轴从小到大。会导致屏幕上方的内容被拉下来显示。**统一描述为：“从上到下滑动，显示上一屏幕内容”。**
2. **向上（从下到上）滑动**：坐标 y 轴从大到小。会导致屏幕下方的内容被拉上来显示。**统一描述为：“从下到上滑动，显示下一屏幕内容”。**
3. **向右（从左到右）滑动**：坐标 x 轴从小到大。会导致屏幕左侧的内容被拉出来显示（常用于侧滑返回或查看上一页）。**统一描述为：“从左到右滑动，显示左侧/上一页内容”。**
4. **向左（从右到左）滑动**：坐标 x 轴从大到小。会导致屏幕右侧的内容被拉出来显示（常用于轮播图或查看下一页）。**统一描述为：“从右到左滑动，显示右侧/下一页内容”。**

---

## 特定 App 操作指南 (App-Specific Guidelines)
*本章节定义了在特定 App 中执行任务时，需遵循的专属交互逻辑与注意事项。*

### 1. 社交媒体平台通用规则 (抖音、小红书、微博)
- **置顶帖与最新帖的严格区分**：请务必注意，**“置顶帖”和“最近/最新发布的帖子”不是一回事**。
  - 创作者通常会将历史的高赞或重要内容固定在主页最上方，这些帖子会带有明确的“置顶”标签，但它们往往不是最新发布的内容。
  - **操作要求**：当用户要求你查看某人的“最新”或“最近”发布的帖子/视频时，**必须仔细检查并跳过所有带有“置顶”标记的内容**，去寻找按时间线排序的第一篇常规帖子进行点击和浏览。

### 2. 小红书 (Xiaohongshu) 专属指南
当用户需要你浏览、总结小红书帖子的内容时，必须严格遵循以下步骤：
- **判断帖子类型**：首先观察并判断当前是视频帖还是图文帖。
  - **视频帖**：点击查看视频详情或简介内容。
  - **图文帖**：检查是否包含多张图片（通常有页面指示器，如底部的小圆点或页码）。
- **图文帖浏览顺序（先图后文）**：
  1. **先看图**：如果有多张图片，**必须首先滑动屏幕（从右向左滑动，即 `SLIDE` 起点在右，终点在左）浏览完所有的图片**。
  2. **后看文**：图片全部浏览完毕后，**其次再向下滑动屏幕**（即 `SLIDE` 起点在下，终点在上）查看下方所有的文字描述内容。
- **详细记录**：在整个浏览过程中，**必须在 `note` 字段中尽可能详细地记录**你所看到的图片关键信息和文字内容，确保最终能够输出高质量的总结。

### 3. 地图类软件 (高德地图、百度地图等) 专属指南
- **输入框快捷清理与覆盖**：对于地图软件的输入框，只要使用 `CLICK` 点击到希望清除的文字，通常就能够直接选中对应文字。
  - **操作要求**：当文字处于选中状态时，无需去寻找“X”按钮或使用退格键，你可以直接使用 `TYPE` 打字，新输入的文字会自动实现对原有选中文字的覆盖。

--
'''

task_define_prompt = """

## 现状
### 1. 用户给你的任务：
{task}

### 2. 当前时间是：
{current_time}

"""

instruction_prompt = '''
explain 字段要尽量简短。10个字以内。

输出结构为：
verify:xx 证据表明上个动作是否生效\tnote:当前页面总结出的关键信息\texplain:解释的内容\taction:动作空间和对应的参数\tkey_process:当前的关键进展,如果没有明显的进展可以写none

思考结束后，以verify字段开头，说明上一步操作是否生效。每个字段用\t做分隔。输出csv 风格以\t 分割字段的action，不要使用json。
'''


class Parser0920SummaryAdv():
    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        self.action_list = ["CLICK", "LONGPRESS", "TYPE", "SCROLL", "AWAKE", "SLIDE", "BACK", "HOME", "COMPLETE", "ABORT", "INFO", "WAIT", "HOT_KEY"]
        pass

    def _compose_system_skill(self, skill, extra_skill=""):
        base_skill = str(skill or "").strip()
        extra_skill = str(extra_skill or "").strip()
        if len(extra_skill) == 0:
            return base_skill

        extra_section = "## 当前透传skill\n" + extra_skill
        if len(base_skill) == 0:
            return extra_section
        return base_skill.rstrip() + "\n\n" + extra_section

    def action2action(self, action):
        # assert single actions
        assert "action" in action or "action_type" in action, f"action {action} should have action or action_type field"
        assert "explain" in action, f"action {action} should have explain field"
        assert "cot" in action, f"action {action} should have cot field"

        explain = action['explain']
        cot = action['cot']
        summary = action.get('summary', '')
        action_type = action.get('action_type', action.get('action', None))

        return_action = OrderedDict(
            {
                "cot": cot,
                "explain": explain,
                "action": action_type,
                "summary": summary
            }
        )


        if action_type == "TYPE":
            # assert "is_keyboard" in action or "keyboard_exists" in action, f"action {action} should have is_keyboard or keyboard_exists field"
            assert "value" in action, f"action {action} should have value field"
            # assert "point" in action, f"action {action} should have point field"

            keyboard_exists = action.get("is_keyboard", action.get("keyboard_exists", False))
            if type(keyboard_exists) == str:
                keyboard_exists = keyboard_exists.lower() == "true"

            # point = action['point']
            value = action['value']

            return_action.update({
                "value": value,
                # "point": point,
                # "keyboard_exists": keyboard_exists
            })

        elif action_type == "CLICK":
            assert "point" in action, f"action {action} should have point field"
            point = action['point']

            return_action.update({
                "point": point
            })

        elif action_type == "AWAKE":
            assert "value" in action, f"action {action} should have value field"
            value = action['value']

            return_action.update({
                "value": value
            })

        elif action_type == "INFO":
            assert "value" in action, f"action {action} should have value field"
            value = action['value']

            return_action.update({
                "value": value
            })

        elif action_type == "WAIT":
            assert "value" in action, f"action {action} should have value field"
            value = action['value']

            return_action.update({
                "value": value
            })

        elif action_type == "COMPLETE":
            assert "return" in action, f"action {action} should have return field"
            return_value = action['return']

            return_action.update({
                "return": return_value
            })


        elif action_type == "ABORT":

            pass


        elif action_type == "SLIDE":
            assert "point1" in action, f"action {action} should have point1 field"
            assert "point2" in action, f"action {action} should have point2 field"
            point1 = action['point1']
            point2 = action['point2']

            return_action.update({
                "point1": point1,
                "point2": point2
            })


        elif action_type == "LONGPRESS":
            assert "point" in action, f"action {action} should have point field"
            point = action['point']

            return_action.update({
                "point": point
            })

        else:
            raise ValueError(f"Unknown action type {action_type} in action {action}")

        return return_action

    def action2str(self, actions):
        assert (type(actions) == list and len(actions) == 0) or type(actions) == dict or type(actions) == OrderedDict, f"actions {actions} should be a list or a dict; only one action is supported"

        action_str = json.dumps(actions, ensure_ascii=False)

        return action_str


    def str2action(self, command_str):
        command_str = command_str.strip()

        # assert  "</think>" in command_str, f"command_str {command_str} should contain <think> and </think> tags"
        # assert "<THINK>" in command_str and "</THINK>" in command_str, f"command_str {command_str} should contain <THINK> and </THINK> tags"
        command_str = command_str.replace("<THINK>", "<think>").replace("</THINK>", "</think>")

        if "</think>" not in command_str:
            cot_small = ""
            # raise ValueError(f"command_str {command_str} should contain <think> and </think> tags")
        else:
            cot_small = command_str.split("<think>")[-1].split("</think>")[0].strip()

        # cot_big = command_str.split("<THINK>")[1].split("</THINK>")[0].strip()



        action = OrderedDict()
        # action['cot'] = cot_part

        action['cot'] = cot_small
        # action['cot'] = cot_big

        kv_part = command_str.split("</think>")[-1].strip()

        def process_kv_pairs(kv_part):
            lines = kv_part.split("\n")
            if len(lines) == 1:
                kvs = [kv.strip() for kv in kv_part.split("\t") if kv.strip()]
            else:
                if "\t" not in kv_part:
                    # 如果没有 \t 分隔符，说明可能是换行分隔的格式
                    kv_part = kv_part.replace("\n", "\t")
                    kvs = [kv.strip() for kv in lines if kv.strip()]
                else:
                    kvs = [kv.strip() for kv in kv_part.split("\t") if kv.strip()]

            return kvs

        # replace /n into space, because we use \t to split different fields, if there are \n in the value, it will cause parsing error.
        # kv_part = kv_part.replace("\n", "\t")

        # FIX:issue 13
        # Error split by \n, should split by tab separator
        # kvs = [kv.strip() for kv in kv_part.split("\t") if kv.strip()]

        kvs = process_kv_pairs(kv_part)

        # hot fix
        if "action: CLICK point:" in command_str:
            command_str = command_str.replace("CLICK point:", "CLICK\tpoint:")

        for kv in kvs:
            if ":" not in kv:
                continue


            key = kv.split(":", 1)[0].strip()
            value = kv.split(":", 1)[1].strip()

            if key == "action":
                action['action'] = value
            elif key == "summary":
                action['summary'] = value
            elif "point" in key:
                # Parse point format: "x,y" or "x y"
                try:
                    # Replace comma with space for unified processing
                    coords = value.replace(",", " ").split()
                    if len(coords) < 2:
                        raise ValueError(f"Expected 2 coordinates, got {len(coords)}")

                    x, y = int(coords[0]), int(coords[1])
                    action[key] = [x, y]

                except (ValueError, IndexError) as e:
                    raise ValueError(
                        f"[Parser Error] Failed to parse point '{value}' for key '{key}': {str(e)}. "
                        f"Expected format: 'x,y' or 'x y' with integer values"
                    ) from e
            else:
                action[key] = value
        # 观察到模型没吐note 字段会导致遗忘关键问题。
        assert "note" in action, f"action {action} should have note field"

        return action

    def env2messages4ask(
        self,
        task,
        environments,
        actions,
        skill=default_skill,
        keep_last_k_images=1,
        extra_skill="",
    ) -> list:

        assert len(environments) > 0, f"environments {environments} should not be empty"
        assert len(environments) - 1 == len(actions), f"environments {environments} should be one more than actions {actions}"
        system_skill = self._compose_system_skill(skill, extra_skill)

        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_skill
                    }
                ]
            },
        ]


        history_content = [
            {
                "type": "text",
                "text": task_define_prompt.format(task=task, current_time=datetime.now().strftime("%Y年%m月%d日")) + "\n\n" + "以下是你之前的操作历史回顾："
            }
        ]

        for idx, (env, act) in enumerate(zip(environments, actions + [None])):

            # environment_content = f"这是第{idx}步的环境信息："

            step_idx = idx + 1

            if act is not None:

                if"cot" in act:
                    del act['cot']

                if "point" in act:
                    del act['point']
                # if "point1" in act:
                    # del act['point1']
                # if "point2" in act:
                    # del act['point2']

                if "action_type" in act:
                    del act['action_type']

                # if slide 计算一下方向： 从上到下，从下到上，从左到右，从右到左
                def get_slide_direction(act):
                    if act['action'] != "SLIDE":
                        return None
                    point1 = act.get("point1", None)
                    point2 = act.get("point2", None)
                    if point1 is None or point2 is None:
                        return None
                    x1, y1 = point1
                    x2, y2 = point2
                    if abs(x2 - x1) > abs(y2 - y1):
                        if x2 > x1:
                            return "从左到右"
                        else:
                            return "从右到左"
                    else:
                        if y2 > y1:
                            return "从上到下"
                        else:
                            return "从下到上"
                if act['action'] == "SLIDE":
                    slide_direction = get_slide_direction(act)
                    if slide_direction is not None:
                        act['slide_direction'] = slide_direction



            user_comment = env.get('user_comment', '').strip()
            if len(user_comment) > 0:
                user_comment = f"用户回复说：\n---------\n{user_comment}\n---------\n用户回复结束\n\n"
            else:
                user_comment = ""
                # user_comment = "用户没有回复任何内容。"

            pic_comment = f"根据协议，第{step_idx}步有截图：\n" if idx >= len(environments) - keep_last_k_images else f"根据协议，第{step_idx}步截图不展示\n\n"

            history_content.append(
                {
                    "type": "text",
                    "text": f"这是第{step_idx}步的环境信息：\n" + user_comment + pic_comment
                }
            )

            if idx == len(environments) - keep_last_k_images:
                history_content.append(
                    {
                        "type": "text",
                        "text": f"<-------------------从这里开始是最近{step_idx}步的环境信息------------------->"  + "\n\n"
                    }
                )

            if idx >= len(environments) - keep_last_k_images:
                history_content.append(
                    {
                        "type": "text",
                        "text": f"<-----第{step_idx}步截图----->"
                    }
                )
                history_content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": env['image']}
                    }
                )
                history_content.append(
                    {
                        "type": "text",
                        "text": f"<-----第{step_idx}步截图重复一遍----->"
                    }
                )
                history_content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": env['image']}
                    }
                )
                history_content.append(
                    {
                        "type": "text",
                        "text": f"<-----第{step_idx}步截图结束----->"
                    }
                )

            if act is not None:
                action_comment = f"这一步的动作是：{json.dumps(act, ensure_ascii=False)}\n\n"
            else:
                action_comment = "\n\n"

            history_content.append(
                {
                    "type": "text",
                    "text": f"这是第{step_idx}步的环境信息结束。" + action_comment
                }
            )

        history_content.append(
            {
                "type": "text",
                "text": f"你需要根据第<-----{len(environments)}----->步的环境信息，预测第{len(environments)}步的动作。\n\n"
                f"一个潜伏在屏幕后的观察者指出：当前屏幕出现了新的变化。请在think 过程中详细的描述出来 ！\n\n"
            }
        )

        history_content.append(
            {
                "type": "text",
                "text": instruction_prompt
            }
        )
        messages.append(
            {
                "role": "user",
                "content": history_content
            }
        )

        return messages

def tkj_action_transformer(action, width: int, height: int):
    ret_dict = {}

    assert "action_type" in action or "action" in action, f"action {action} should have action_type or action field"

    if "action_type" in action:
        action_type = action['action_type']
    if "action" in action:
        action_type = action['action']

    action['action_type'] = action_type
    action['action'] = action_type

    # try:
    if True:
        ret_dict['explain'] = action['explain']
        ret_dict['cot'] = action.get('cot', '')

        # compatible with new and old field names
        ret_dict['action_type'] = action.get('action_type') or action.get('action')
        if "search_type" in action:
            ret_dict['search_type'] = action['search_type']

        # compatible with different field names of keyboard
        if "keyboard_exists" in action:
            ret_dict['keyboard_exists'] = action['keyboard_exists']
        elif "is_keyboard" in action:
            ret_dict['keyboard_exists'] = action['is_keyboard']

        if "is_auto_close" in action:
            ret_dict["is_auto_close"] = action["is_auto_close"]

        if "point" in action:
            ret_dict['coordinates'] = action['point']

        for key in ["point", "point1", "point2"]:
            if key in action:
                ret_dict[key] = action[key]

        if "value" in action:
            ret_dict['text'] = action['value']
        if action['action_type'] == "WAIT":
            ret_dict['duration'] = action['value']
            if "功能类" in action['explain']:
                ret_dict["is_auto_close"] = True

            if "close_reasons" in action:
                ret_dict["close_reasons"] = [{
                    "reason": reason["reason"],
                    "bbox": reason["bbox"],
                } for reason in action["close_reasons"]]
            else:
                ret_dict["close_reasons"] = []
        if action['action_type'] == "TYPE":
            if "point" in action:
                ret_dict['coordinates'] = action['point']
            else:
                ret_dict['coordinates'] = action['point']
        # if ['action_type'] == "SCROLL":
        #     ret_dict['point1'] = denormalize_point(action['point1'], width, height)
        #     ret_dict['point2'] = denormalize_point(action['point2'], width, height)
        # if action['action_type'] == "LONGPRESS":
        #     ret_dict['point'] = denormalize_point(action['point'], width, height)
    # except Exception as e:
        # ret_dict["action_type"] = "ABORT"
        # ret_dict["abort_reason"] = "operation parameter parsing exception"

    return ret_dict


if __name__ == "__main__":
    # test_case = [
    #     "<think>xxx</think>",
    #     "<think>xxx</think>\nexplain:xxx\taction:xx\tvalue:xxx\tsummary:xxx",
    #     "<think>xxx</think>\nexplain:xxx\taction:xx\tvalue:xxx\tsummary:xxx",
    #     "<think>xxx</think>\nexplain:xxx\taction:xx\tvalue:xxx\tsummary:xxx",
    #     "< think>xxx</think>\nexplain:xxx\taction:xx\tvalue:xxx\tsummary:xxx",
    #     "</THINK>xxx</THINK>\nexplain:xxx\taction:xx\tvalue:xxx\tsummary:xxx",
    #     "<THINK>xxx</THINK>\nexplain:xxx\taction:xx\tvalue:xxx\tsummary:xxx",
    # ]
    # for command_str in test_case:
    #     action = str2action(command_str)
    #     print(f"action: {action}")
    pass
