"""Script to run end-to-end evaluation on the benchmark.
Utils and basic architecture credit to https://github.com/web-arena-x/webarena/blob/main/run.py.
"""

import argparse
import datetime
import json
import logging
import os
import sys

from tqdm import tqdm

import lib_run_single
from desktop_env.desktop_env import DesktopEnv
from mm_agents.agent import PromptAgent
from mm_agents.qwen3vl_agent import Qwen3VLAgent
from mm_agents.qwen3vl_skill_agent import Qwen3VLSkillAgent
from mm_agents.qwen3vl_skill_agent_v2 import Qwen3VLSkillAgentV2
from mm_agents.general_agent import GeneralAgent
from mm_agents.general_skill_agent import GeneralSkillAgent
from mm_agents.general_text_skill_agent import (
    GeneralTextSkillAgent,
    TEXT_SKILL_MODE_BRANCH_PLANNER,
    TEXT_SKILL_MODE_INLINE_CONTEXT,
)
from mm_agents.mm_skill_agent import MMSkillAgent

AGENT_TYPE_ALIASES = {
    "gemini": "general",
    "gemini_skill": "general_skill",
    "gemini_text_skill": "general_text_skill",
    "gemini3pro": "general",
    "gemini3pro_skill": "general_skill",
}
GENERAL_AGENT_TYPES = {"general", "general_skill", "general_text_skill", "mm_skill"}

# Almost deprecated since it's not multi-env, use run_multienv_*.py instead

#  Logger Configs {{{ #
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

datetime_str: str = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")

file_handler = logging.FileHandler(
    os.path.join("logs", "normal-{:}.log".format(datetime_str)), encoding="utf-8"
)
debug_handler = logging.FileHandler(
    os.path.join("logs", "debug-{:}.log".format(datetime_str)), encoding="utf-8"
)
stdout_handler = logging.StreamHandler(sys.stdout)
sdebug_handler = logging.FileHandler(
    os.path.join("logs", "sdebug-{:}.log".format(datetime_str)), encoding="utf-8"
)

file_handler.setLevel(logging.INFO)
debug_handler.setLevel(logging.DEBUG)
stdout_handler.setLevel(logging.INFO)
sdebug_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="\x1b[1;33m[%(asctime)s \x1b[31m%(levelname)s \x1b[32m%(module)s/%(lineno)d-%(processName)s\x1b[1;33m] \x1b[0m%(message)s"
)
file_handler.setFormatter(formatter)
debug_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)
sdebug_handler.setFormatter(formatter)

stdout_handler.addFilter(logging.Filter("desktopenv"))
sdebug_handler.addFilter(logging.Filter("desktopenv"))

logger.addHandler(file_handler)
logger.addHandler(debug_handler)
logger.addHandler(stdout_handler)
logger.addHandler(sdebug_handler)
#  }}} Logger Configs #

logger = logging.getLogger("desktopenv.experiment")


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run end-to-end evaluation on the benchmark"
    )

    # environment config
    parser.add_argument("--path_to_vm", type=str, default=None)
    parser.add_argument(
        "--provider_name", type=str, default="vmware",
        help="Virtualization provider (vmware, docker, aws, azure, gcp, virtualbox)"
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run in headless machine"
    )
    parser.add_argument(
        "--action_space", type=str, default="pyautogui", help="Action type"
    )
    parser.add_argument(
        "--observation_type",
        choices=["screenshot", "a11y_tree", "screenshot_a11y_tree", "som"],
        default="a11y_tree",
        help="Observation type",
    )
    parser.add_argument("--screen_width", type=int, default=1920)
    parser.add_argument("--screen_height", type=int, default=1080)
    parser.add_argument("--sleep_after_execution", type=float, default=0.0)
    parser.add_argument("--max_steps", type=int, default=20)

    # agent config
    parser.add_argument("--max_trajectory_length", type=int, default=3)
    parser.add_argument(
        "--test_config_base_dir", type=str, default="evaluation_examples"
    )

    # lm config
    parser.add_argument("--model", type=str, default="gpt-4o")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--max_tokens", type=int, default=None)
    parser.add_argument("--stop_token", type=str, default=None)

    # agent config
    parser.add_argument(
        "--agent_type",
        type=str,
        default="prompt",
        choices=[
            "prompt",
            "qwen3vl",
            "qwen3vl_skill",
            "qwen3vl_skill_v2",
            "general",
            "general_skill",
            "general_text_skill",
            "gemini",
            "gemini_skill",
            "gemini_text_skill",
            "mm_skill",
            "gemini3pro",
            "gemini3pro_skill",
        ],
        help="Agent type to use. `general` is the model-agnostic screenshot-to-pyautogui adapter; "
             "`general_text_skill` and `mm_skill` add text-only or multimodal skill consultation. "
             "Legacy `gemini*` names are accepted as aliases.",
    )
    # Backend config
    parser.add_argument(
        "--api_backend",
        type=str,
        default="openai",
        choices=["openai", "dashscope", "gemini"],
        help="API backend. `general*` and `mm_skill` support openai-compatible and native gemini endpoints.",
    )
    parser.add_argument(
        "--base_url",
        type=str,
        default=None,
        help="Custom base URL for an OpenAI-compatible API endpoint",
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="API key for OpenAI-compatible API",
    )
    parser.add_argument(
        "--api_model",
        type=str,
        default=None,
        help="Optional backend model name. If omitted, uses --model.",
    )
    parser.add_argument(
        "--coordinate_type",
        type=str,
        default="relative",
        choices=["absolute", "relative"],
        help="Coordinate system for Qwen3VL agent (absolute or relative)",
    )
    # Reasoning/thinking config for compatible backends
    parser.add_argument(
        "--thinking_level",
        type=str,
        default="HIGH",
        choices=["NONE", "LOW", "MEDIUM", "HIGH"],
        help="Thinking level for compatible native Gemini endpoints",
    )
    parser.add_argument(
        "--thinking_mode",
        type=str,
        default="auto",
        choices=["auto", "on", "off"],
        help="Thinking mode for compatible backends used by GeneralAgent.",
    )
    parser.add_argument(
        "--include_thoughts",
        action="store_true",
        default=True,
        help="Include thinking/reasoning in compatible backend responses",
    )
    parser.add_argument(
        "--client_password",
        type=str,
        default="password",
        help="Client password for VM access (used by some providers/agents)",
    )

    # example config
    parser.add_argument("--domain", type=str, default="all")
    parser.add_argument(
        "--test_all_meta_path", type=str, default="evaluation_examples/test_all.json"
    )
    parser.add_argument(
        "--example_id", type=str, default=None,
        help="Specific example ID to test (e.g., 7b6c7e24-c58a-49fc-a5bb-d57b80e5b4c3)"
    )

    # logging related
    parser.add_argument("--result_dir", type=str, default="./results")
    # Skills config
    parser.add_argument(
        "--enable_skills",
        action="store_true",
        default=False,
        help="Enable skill-augmented agent with procedural knowledge from skills_library",
    )
    parser.add_argument(
        "--skill_mode",
        type=str,
        default="text_only",
        choices=["text_only", "multimodal"],
        help="Skill loading mode: 'text_only' loads only SKILL.md text, "
             "'multimodal' also enables on-demand visual reference loading",
    )
    parser.add_argument(
        "--text_skill_mode",
        type=str,
        default=TEXT_SKILL_MODE_INLINE_CONTEXT,
        choices=[TEXT_SKILL_MODE_INLINE_CONTEXT, TEXT_SKILL_MODE_BRANCH_PLANNER],
        help="Mode for general_text_skill: 'inline_context' keeps loaded SKILL.md text in the main context, "
             "'branch_planner' uses a lightweight text-only planner branch that returns JSON guidance.",
    )
    parser.add_argument(
        "--skills_library_dir",
        type=str,
        default="skills_library",
        help="Path to the skills library directory",
    )
    parser.add_argument(
        "--task_skill_mapping_root",
        type=str,
        default=None,
        help="Root directory containing per-domain task_skill_mapping_generated.json files",
    )
    parser.add_argument(
        "--task_skill_top_k",
        type=int,
        default=6,
        help="Maximum number of external mapped skills exposed to the agent per task; <= 0 keeps all",
    )
    parser.add_argument(
        "--save_conversation_json",
        action="store_true",
        default=False,
        help="Save full conversation history (prompts + responses) to conversation.json "
             "alongside runtime.log for each task",
    )

    args = parser.parse_args()
    args.agent_type = AGENT_TYPE_ALIASES.get(args.agent_type, args.agent_type)

    if args.agent_type in GENERAL_AGENT_TYPES:
        if args.api_backend not in {"openai", "gemini"}:
            raise ValueError(
                "general*, mm_skill agents support --api_backend openai or gemini. "
                "Use an OpenAI-compatible endpoint for other model providers."
            )
        if args.api_backend == "gemini":
            if args.api_key is None:
                args.api_key = os.getenv("GEMINI_API_KEY")
            if args.base_url is None:
                args.base_url = os.getenv("GEMINI_BASE_URL")
            if not args.api_key:
                raise ValueError("Gemini API key is required. Pass --api_key or set GEMINI_API_KEY.")
            if not args.base_url:
                raise ValueError("Gemini base URL is required. Pass --base_url or set GEMINI_BASE_URL.")
        else:
            if args.api_key is None:
                args.api_key = os.getenv("OPENAI_API_KEY")
            if args.base_url is None:
                args.base_url = os.getenv("OPENAI_BASE_URL")
            if not args.api_key:
                raise ValueError("OpenAI-compatible API key is required. Pass --api_key or set OPENAI_API_KEY.")
            if not args.base_url:
                raise ValueError("OpenAI-compatible base URL is required. Pass --base_url or set OPENAI_BASE_URL.")
        if args.temperature is None:
            args.temperature = 0.0
        if args.max_tokens is None:
            args.max_tokens = 32768
    else:
        if args.temperature is None:
            args.temperature = 1.0
        if args.max_tokens is None:
            args.max_tokens = 1500

    return args


def test(args: argparse.Namespace, test_all_meta: dict) -> None:
    scores = []
    max_steps = args.max_steps

    # log args
    logger.info("Args: %s", args)
    # set wandb project
    cfg_args = {
        "path_to_vm": args.path_to_vm,
        "provider_name": args.provider_name,
        "headless": args.headless,
        "action_space": args.action_space,
        "observation_type": args.observation_type,
        "screen_width": args.screen_width,
        "screen_height": args.screen_height,
        "sleep_after_execution": args.sleep_after_execution,
        "max_steps": args.max_steps,
        "max_trajectory_length": args.max_trajectory_length,
        "model": args.model,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "stop_token": args.stop_token,
        "result_dir": args.result_dir,
    }

    # Initialize agent based on agent_type
    if args.agent_type == "qwen3vl":
        agent = Qwen3VLAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            coordinate_type=args.coordinate_type,
            api_backend=args.api_backend,
            base_url=args.base_url,
            api_key=args.api_key,
            client_password=getattr(args, "client_password", ""),
            enable_skills=args.enable_skills,
            skill_mode=args.skill_mode,
            skills_library_dir=args.skills_library_dir,
            save_conversation_json=args.save_conversation_json,
        )
    elif args.agent_type == "qwen3vl_skill":
        agent = Qwen3VLSkillAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            coordinate_type=args.coordinate_type,
            api_backend=args.api_backend,
            base_url=args.base_url,
            api_key=args.api_key,
            client_password=getattr(args, "client_password", ""),
            enable_skills=args.enable_skills,
            skill_mode=args.skill_mode,
            skills_library_dir=args.skills_library_dir,
            save_conversation_json=args.save_conversation_json,
        )
    elif args.agent_type == "qwen3vl_skill_v2":
        agent = Qwen3VLSkillAgentV2(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            coordinate_type=args.coordinate_type,
            api_backend=args.api_backend,
            api_model=args.api_model,
            enable_thinking=args.enable_thinking,
            base_url=args.base_url,
            api_key=args.api_key,
            client_password=getattr(args, "client_password", ""),
            enable_skills=args.enable_skills,
            skill_mode=args.skill_mode,
            skills_library_dir=args.skills_library_dir,
            save_conversation_json=args.save_conversation_json,
        )
    elif args.agent_type == "general":
        agent = GeneralAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            max_trajectory_length=args.max_trajectory_length,
            client_password=getattr(args, 'client_password', 'password'),
            api_key=args.api_key,
            base_url=args.base_url,
            api_backend=args.api_backend,
            api_model=getattr(args, "api_model", None),
            thinking_level=args.thinking_level,
            include_thoughts=args.include_thoughts,
            thinking_mode=getattr(args, "thinking_mode", "auto"),
            coordinate_type=args.coordinate_type,
            save_conversation_json=args.save_conversation_json,
        )
    elif args.agent_type == "general_skill":
        agent = GeneralSkillAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            max_trajectory_length=args.max_trajectory_length,
            client_password=getattr(args, 'client_password', 'password'),
            api_key=args.api_key,
            base_url=args.base_url,
            api_backend=args.api_backend,
            api_model=getattr(args, "api_model", None),
            thinking_level=args.thinking_level,
            include_thoughts=args.include_thoughts,
            thinking_mode=getattr(args, "thinking_mode", "auto"),
            coordinate_type=args.coordinate_type,
            skill_mode=args.skill_mode,
            skills_library_dir=args.skills_library_dir,
            save_conversation_json=args.save_conversation_json,
        )
    elif args.agent_type == "general_text_skill":
        agent = GeneralTextSkillAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            max_trajectory_length=args.max_trajectory_length,
            client_password=getattr(args, 'client_password', 'password'),
            api_key=args.api_key,
            base_url=args.base_url,
            api_backend=args.api_backend,
            api_model=getattr(args, "api_model", None),
            thinking_level=args.thinking_level,
            include_thoughts=args.include_thoughts,
            thinking_mode=getattr(args, "thinking_mode", "auto"),
            coordinate_type=args.coordinate_type,
            skills_library_dir=args.skills_library_dir,
            save_conversation_json=args.save_conversation_json,
            text_skill_mode=args.text_skill_mode,
        )
    elif args.agent_type == "mm_skill":
        agent = MMSkillAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            max_trajectory_length=args.max_trajectory_length,
            client_password=getattr(args, 'client_password', 'password'),
            api_key=args.api_key,
            base_url=args.base_url,
            api_backend=args.api_backend,
            api_model=getattr(args, "api_model", None),
            thinking_level=args.thinking_level,
            include_thoughts=args.include_thoughts,
            thinking_mode=getattr(args, "thinking_mode", "auto"),
            coordinate_type=args.coordinate_type,
            skill_mode=args.skill_mode,
            skills_library_dir=args.skills_library_dir,
            save_conversation_json=args.save_conversation_json,
        )
    else:
        agent = PromptAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            max_trajectory_length=args.max_trajectory_length,
        )

    env = DesktopEnv(
        provider_name=args.provider_name,
        path_to_vm=args.path_to_vm,
        action_space=agent.action_space,
        screen_size=(args.screen_width, args.screen_height),
        headless=args.headless,
        os_type="Ubuntu",
        require_a11y_tree=args.observation_type
        in ["a11y_tree", "screenshot_a11y_tree", "som"],
        enable_proxy=False,
    )

    for domain in tqdm(test_all_meta, desc="Domain"):
        for example_id in tqdm(test_all_meta[domain], desc="Example", leave=False):
            # 如果指定了 example_id，只运行匹配的任务
            if args.example_id and example_id != args.example_id:
                continue

            config_file = os.path.join(
                args.test_config_base_dir, f"examples/{domain}/{example_id}.json"
            )
            with open(config_file, "r", encoding="utf-8") as f:
                example = json.load(f)
            example["_osworld_domain"] = domain

            logger.info(f"[Domain]: {domain}")
            logger.info(f"[Example ID]: {example_id}")

            instruction = example["instruction"]

            logger.info(f"[Instruction]: {instruction}")
            # wandb each example config settings
            cfg_args["instruction"] = instruction
            cfg_args["start_time"] = datetime.datetime.now().strftime(
                "%Y:%m:%d-%H:%M:%S"
            )
            # run.config.update(cfg_args)

            example_result_dir = os.path.join(
                args.result_dir,
                args.action_space,
                args.observation_type,
                args.model,
                domain,
                example_id,
            )
            os.makedirs(example_result_dir, exist_ok=True)
            # example start running
            try:
                lib_run_single.run_single_example(
                    agent,
                    env,
                    example,
                    max_steps,
                    instruction,
                    args,
                    example_result_dir,
                    scores,
                )
            except Exception as e:
                logger.error(f"Exception in {domain}/{example_id}: {e}")
                # Only attempt to end recording if controller exists (not Docker provider)
                if hasattr(env, 'controller') and env.controller is not None:
                    env.controller.end_recording(
                        os.path.join(example_result_dir, "recording.mp4")
                    )
                with open(os.path.join(example_result_dir, "traj.jsonl"), "a") as f:
                    f.write(
                        json.dumps(
                            {"Error": f"Time limit exceeded in {domain}/{example_id}"}
                        )
                    )
                    f.write("\n")

    env.close()
    logger.info(f"Average score: {sum(scores) / len(scores) if scores else 0}")


def get_unfinished(
    action_space, use_model, observation_type, result_dir, total_file_json
):
    target_dir = os.path.join(result_dir, action_space, observation_type, use_model)

    if not os.path.exists(target_dir):
        return total_file_json

    finished = {}
    for domain in os.listdir(target_dir):
        finished[domain] = []
        domain_path = os.path.join(target_dir, domain)
        if os.path.isdir(domain_path):
            for example_id in os.listdir(domain_path):
                if example_id == "onboard":
                    continue
                example_path = os.path.join(domain_path, example_id)
                if os.path.isdir(example_path):
                    if "result.txt" not in os.listdir(example_path):
                        # empty all files under example_id
                        for file in os.listdir(example_path):
                            os.remove(os.path.join(example_path, file))
                    else:
                        finished[domain].append(example_id)

    if not finished:
        return total_file_json

    for domain, examples in finished.items():
        if domain in total_file_json:
            total_file_json[domain] = [
                x for x in total_file_json[domain] if x not in examples
            ]

    return total_file_json


def get_result(action_space, use_model, observation_type, result_dir, total_file_json):
    target_dir = os.path.join(result_dir, action_space, observation_type, use_model)
    if not os.path.exists(target_dir):
        print("New experiment, no result yet.")
        return None

    all_result = []

    for domain in os.listdir(target_dir):
        domain_path = os.path.join(target_dir, domain)
        if os.path.isdir(domain_path):
            for example_id in os.listdir(domain_path):
                example_path = os.path.join(domain_path, example_id)
                if os.path.isdir(example_path):
                    if "result.txt" in os.listdir(example_path):
                        # empty all files under example_id
                        try:
                            all_result.append(
                                float(
                                    open(
                                        os.path.join(example_path, "result.txt"), "r"
                                    ).read()
                                )
                            )
                        except:
                            all_result.append(0.0)

    if not all_result:
        print("New experiment, no result yet.")
        return None
    else:
        print("Current Success Rate:", sum(all_result) / len(all_result) * 100, "%")
        return all_result


if __name__ == "__main__":
    ####### The complete version of the list of examples #######
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    args = config()

    # save args to json in result_dir/action_space/observation_type/model/args.json
    path_to_args = os.path.join(
        args.result_dir,
        args.action_space,
        args.observation_type,
        args.model,
        "args.json",
    )
    os.makedirs(os.path.dirname(path_to_args), exist_ok=True)
    with open(path_to_args, "w", encoding="utf-8") as f:
        json.dump(vars(args), f, indent=4)

    with open(args.test_all_meta_path, "r", encoding="utf-8") as f:
        test_all_meta = json.load(f)

    if args.domain != "all":
        test_all_meta = {args.domain: test_all_meta[args.domain]}

    test_file_list = get_unfinished(
        args.action_space,
        args.model,
        args.observation_type,
        args.result_dir,
        test_all_meta,
    )
    left_info = ""
    for domain in test_file_list:
        left_info += f"{domain}: {len(test_file_list[domain])}\n"
    logger.info(f"Left tasks:\n{left_info}")

    get_result(
        args.action_space,
        args.model,
        args.observation_type,
        args.result_dir,
        test_all_meta,
    )
    test(args, test_file_list)
