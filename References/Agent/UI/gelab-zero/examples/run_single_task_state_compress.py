import argparse
import sys
import time

if "." not in sys.path:
    sys.path.append(".")

from copilot_agent_client.pu_client import evaluate_task_on_device
from copilot_agent_server.local_state_compress_server import LocalStateCompressServer
from copilot_front_end.mobile_action_helper import get_device_wm_size, list_devices


tmp_server_config = {
    "log_dir": "running_log/server_log/os-copilot-local-eval-logs/traces",
    "image_dir": "running_log/server_log/os-copilot-local-eval-logs/images",
    "debug": False
}

DEFAULT_TASK = (
    "帮我看看微博文娱热搜上有哪些内容，总结一下给我",
)


local_model_config = {
    "task_type": "parser_0920_summary_adv_state_compress",
    "model_config": {
        "model_name": "step-3.6",
        "model_provider": "stepfun",
        "args": {
            "temperature": 1,
            "top_p": 0.95,
            "frequency_penalty": 0.05,
            "max_tokens": 32768,
        },
    },
    "config": {
        "enable_state_compression": True,
        "state_compression_interval": 10,
        "state_compression_recent_window": 10,
        "state_compression_max_field_items": 10,
    },
    "max_steps": 400,
    "delay_after_capture": 3,
    "debug": False,
}


_step_times = []


def wrap_automate_step_with_timing(server_instance):
    original_method = server_instance.automate_step

    def timed_automate_step(payload):
        step_start = time.time()
        try:
            result = original_method(payload)
        finally:
            duration = time.time() - step_start
            _step_times.append(duration)
            print(f"Step {len(_step_times)} took: {duration:.2f} seconds")
        return result

    server_instance.automate_step = timed_automate_step


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a single task with rolling state compression.")
    parser.add_argument("--task", type=str, default=DEFAULT_TASK, help="Task to execute on device")
    parser.add_argument("--device-id", type=str, default=None, help="Optional adb device id")
    args = parser.parse_args()

    available_devices = list_devices()
    assert len(available_devices) > 0, "No Android device found."

    device_id = args.device_id or available_devices[0]
    device_wm_size = get_device_wm_size(device_id)
    device_info = {
        "device_id": device_id,
        "device_wm_size": device_wm_size,
    }

    print(f"Using device {device_id} with wm size {device_wm_size} to execute task: {args.task}")

    local_server = LocalStateCompressServer(tmp_server_config)
    wrap_automate_step_with_timing(local_server)

    total_start = time.time()
    evaluate_task_on_device(
        local_server,
        device_info,
        args.task,
        local_model_config,
        extra_info={
            "source": "examples/run_single_task_state_compress.py",
            "agent_loop_impl": "local_state_compress",
            "server_type": "local_state_compress_server",
        },
        reflush_app=True,
    )
    total_time = time.time() - total_start
    print(f"Total execution time: {total_time:.2f} seconds")
