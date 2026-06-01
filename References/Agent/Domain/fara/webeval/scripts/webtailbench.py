"""Run WebTailBench scored by the Universal Verifier (MMRubricAgent).

Example:
    # Single split ("flights") with 1 process, using the Foundry endpoint
    # configs for both the solver model and the judge (gpt-5.2):
    python scripts/webtailbench.py \
        --model_endpoint ../endpoint_configs/fara_foundry \
        --eval_oai_config ../endpoint_configs/gpt5.2_prod \
        --judge_eval_model gpt-5 \
        --split flights \
        --processes 1 --subsample 0.05 --max_rounds 30
"""

from webeval.systems.websurfer import WebSurferSystem
from webeval.benchmarks import WebTailBenchBenchmark
from pathlib import Path
import numpy as np
import os
import logging
import mlflow
from eval_exp import EvalExp, ModelReference, get_foundry_endpoint_configs
from webeval.oai_clients.graceful_client import GracefulRetryClient
from webeval.eval_result import EvalResult, Stage
from arg_parsing import get_eval_args


class Callback:
    def __init__(self):
        self.scores = []

    def __call__(self, result: EvalResult, mlflow_facade, mlflow_run_id: str):
        if result.stage == Stage.EVALUATED:
            self.scores.append(result.score)
        mlflow_facade.log_metric(
            "score", np.mean(self.scores or [0]), run_id=mlflow_run_id
        )


def add_webtailbench_args(parser):
    parser.add_argument(
        "--split",
        type=str,
        default=None,
        help=(
            "WebTailBench category to filter on (e.g. flights, hotels, "
            "shopping, restaurants, activities, ticketing, real-estate, "
            "jobs, shopping_list, comparison_shopping, compositional_tasks). "
            "Omit to evaluate all categories."
        ),
    )
    parser.add_argument(
        "--include_refusals",
        action="store_true",
        help="Also load WebTailBench-Refusals.tsv (the 111 harmful-task split).",
    )
    parser.add_argument(
        "--judge_eval_model",
        type=str,
        default="gpt-5",
        help=(
            "Which judge LLM to pick from --eval_oai_config (default: gpt-5; "
            "pass '*' to use all available configs)."
        ),
    )
    parser.add_argument(
        "--judge_o4_eval_model",
        type=str,
        default=None,
        help=(
            "Optional separate o4-mini judge endpoint. Defaults to the "
            "gpt-5 judge if unset. Expects --eval_oai_config to include "
            "o4-mini configs."
        ),
    )
    parser.add_argument(
        "--rubric_score_threshold",
        type=float,
        default=0.8,
        help="Rubric pass threshold (default 0.8).",
    )
    parser.add_argument(
        "--majority_vote_instances",
        type=int,
        default=1,
        help="Odd number of MMRubric instances for majority voting (default 1).",
    )
    parser.add_argument(
        "--success",
        choices=("outcome", "process", "both"),
        default="outcome",
        help=(
            "Which Universal Verifier signal counts as 'success' for the "
            "top-line score. 'outcome' (default) reports the binary "
            "outcome_success field — this is the metric Fara-7B numbers "
            "in the README are reported against. 'process' reports "
            "rubric_is_success (rubric_score >= --rubric_score_threshold) "
            "— more lenient, expect slightly higher numbers. 'both' "
            "requires outcome_success AND process pass."
        ),
    )


def main():
    args = get_eval_args(add_webtailbench_args)

    if args.browserbase:
        assert os.environ.get("BROWSERBASE_API_KEY"), (
            "BROWSERBASE_API_KEY environment variable must be set to use browserbase"
        )
        assert os.environ.get("BROWSERBASE_PROJECT_ID"), (
            "BROWSERBASE_PROJECT_ID environment variable must be set to use browserbase"
        )

    experiment = EvalExp(ws=None, user=args.user, seed=args.seed)

    with experiment.start_run() as run:
        model_ref = ModelReference(
            args.model_url,
            args.model_port,
            args.device_id,
            args.web_surfer_kwargs.get("max_n_images", 3),
            args.gpt_solver_model_name,
            args.dtype,
            args.enforce_eager,
            use_external_endpoint=bool(args.model_endpoint),
        )

        logger = logging.getLogger("webtailbench-eval")
        logger.setLevel(logging.INFO)

        mlflow.log_param("max_rounds", args.max_rounds)
        if args.web_surfer_model_type == "gpt_solver":
            mlflow.log_param(
                "web_surfer_model_type",
                f"{args.web_surfer_model_type}/{args.gpt_solver_model_name}",
            )
        else:
            mlflow.log_param("web_surfer_model_type", args.web_surfer_model_type)
        mlflow.log_param("fn_call_template", args.fn_call_template)

        if args.model_endpoint:
            websurfer_client_cfg = get_foundry_endpoint_configs(args.model_endpoint)
            logger.info(
                f"Loaded {len(websurfer_client_cfg)} external endpoint config(s) "
                f"from {args.model_endpoint}"
            )
            model_ref.model_url_to_log = websurfer_client_cfg[0]["base_url"]
            model_ref.model_to_log = websurfer_client_cfg[0]["base_url"]
            mlflow.log_param("using_external_endpoint", True)
            mlflow.log_param(
                "endpoint_config_path",
                ",".join([x["base_url"] for x in websurfer_client_cfg]),
            )
        else:
            websurfer_client_cfg = {
                "api_key": "NONE",
                "model": "gpt-4o-mini-2024-07-18",
                "base_url": f"http://0.0.0.0:{args.model_port}/v1",
            }
            if args.web_surfer_client_cfg is not None:
                websurfer_client_cfg = args.web_surfer_client_cfg
        if args.web_surfer_kwargs:
            mlflow.log_params(
                {f"web_surfer_kwargs.{k}": v for k, v in args.web_surfer_kwargs.items()}
            )

        system = WebSurferSystem(
            system_name="WebSurfer",
            web_surfer_model_type=args.web_surfer_model_type,
            max_rounds=args.max_rounds,
            websurfer_client_cfg=websurfer_client_cfg,
            start_on_target_url=True,
            browserbase=args.browserbase,
            web_surfer_kwargs=args.web_surfer_kwargs,
            gpt_solver_model_name=args.gpt_solver_model_name,
            fn_call_template=args.fn_call_template,
            step_budgets=args.step_budgets,
        )

        mlflow.log_param("eval_oai_config", args.eval_oai_config)
        mlflow.log_param("judge_eval_model", args.judge_eval_model)

        data_dir = Path(__file__).resolve().parent.parent / "data" / "webtailbench"
        data_dir.mkdir(parents=True, exist_ok=True)

        # The MMRubricAgent uses two clients: a gpt-5 family one and an
        # o4-mini one. We load them from the same --eval_oai_config dir
        # using the GracefulRetryClient model-filter.
        gpt5_client = GracefulRetryClient.from_path(
            args.eval_oai_config, logger=logger, eval_model=args.judge_eval_model
        )
        o4_target = args.judge_o4_eval_model or args.judge_eval_model
        try:
            o4mini_client = GracefulRetryClient.from_path(
                args.eval_oai_config, logger=logger, eval_model=o4_target
            )
        except ValueError:
            # Fall back to gpt5_client when eval_oai_config has no o4 configs.
            logger.warning(
                f"No configs matched '{o4_target}' in {args.eval_oai_config}; "
                f"reusing the gpt-5 judge as the o4-mini judge."
            )
            o4mini_client = gpt5_client

        benchmark = WebTailBenchBenchmark(
            data_dir=data_dir,
            gpt5_client=gpt5_client,
            o4mini_client=o4mini_client,
            include_refusals=args.include_refusals,
            redo_eval=args.redo_eval,
            rubric_score_threshold=args.rubric_score_threshold,
            majority_vote_instances=args.majority_vote_instances,
            success_criterion=args.success,
        )
        mlflow.log_param("success_criterion", args.success)
        mlflow.log_param("rubric_score_threshold", args.rubric_score_threshold)

        mlflow.log_param("subsample", args.subsample)
        mlflow.log_param("processes", args.processes)
        mlflow.log_param("split", args.split)
        mlflow.log_param("max_error_task_retries", args.max_error_task_retries)
        experiment.run(
            model_ref=model_ref,
            system=system,
            benchmark=benchmark,
            out_url=args.out_url,
            subsample=args.subsample,
            redo_eval=args.redo_eval,
            run_id=args.run_id,
            split=args.split,
            processes=args.processes,
            callbacks=[Callback()],
            eval_only=args.eval_only,
            max_error_task_retries=args.max_error_task_retries,
        )


if __name__ == "__main__":
    main()
