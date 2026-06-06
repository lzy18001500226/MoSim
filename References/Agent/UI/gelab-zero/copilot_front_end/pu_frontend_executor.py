# to define a standard front-end action space;
# to define some different format of parsers;
# to define executors to execute the front-end actions;

import subprocess
import time
import subprocess
import os
import shlex
import sys

import uiautomator2 as u2
# add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copilot_front_end.package_map import find_package_name

VALID_FRONTEND_ACTIONS = [
    "CLICK",
    "LONGPRESS",
    "TYPE",
    "SCROLL",
    "AWAKE",
    "SLIDE",
    "BACK",
    "HOME",
    "COMPLETE",
    "ABORT",
    "INFO",
    "WAIT",
    "CALL_USER",
    "ZOOMINOUT",
    "HOT_KEY",
    "LONGPRESSANDDRAG",
    "ZOOM",
    "ENTER",
]

ACTION_TYPE_ALIASES = {
    "CALL_USER": "CALL_USER",
}


def parser0729_to_frontend_action(parser_action):
    pass


def uiTars_to_frontend_action(ui_action):
    action_type = None
    if "action" in ui_action:
        action_type = ui_action["action"]
    elif "action_type" in ui_action:
        action_type = ui_action["action_type"]
    else:
        raise ValueError(
            f"ui_action must contain 'action' or 'action_type'. Got keys: {list(ui_action.keys())}"
        )

    action_type = ACTION_TYPE_ALIASES.get(action_type, action_type)

    ui_action['action_type'] = action_type

    if action_type == "CLICK":
        assert "point" in ui_action, "Missing point in CLICK action"
    elif action_type == "TYPE":
        assert "value" in ui_action, "Missing value in TYPE action"

    if action_type == "WAIT":
        if "value" in ui_action:
            try:
                seconds = float(ui_action["value"])
                if seconds > 100:
                    seconds /= 1000
            except (TypeError, ValueError):
                seconds = 5
            ui_action["seconds"] = seconds
            # del ui_action["value"]
    elif action_type == "LONGPRESS":
        duration = ui_action.get("duration", ui_action.get("value", 1.5))
        ui_action["duration"] = float(duration)

    # if action_type == "TYPE":
    #     value = ui_action.get("value", "")
    #     value = value.replace(" ","_").replace("(", "\(").replace(")", "\)").replace("&", "\&").replace("|", "\|").replace(";", "\;").replace("$", "\$")
    #     ui_action["value"] = value

    assert ui_action["action_type"] in VALID_FRONTEND_ACTIONS, f"Invalid action type: {ui_action['action_type']}"

    return ui_action

def _convert_normalized_point_to_fixed_point(point):
    x, y = point
    assert type(x) == float and type(y) == float, f"Point coordinates must be float, got {type(x)} and {type(y)}"
    assert 0.0 <= float(x) <= 1.0, f"x {x} out of range [0.0, 1.0]"
    assert 0.0 <= float(y) <= 1.0, f"y {y} out of range [0.0, 1.0]"

    fixed_x = int(float(x) * 1000)
    fixed_y = int(float(y) * 1000)
    return (fixed_x, fixed_y)




def ZOOMPOINT(
    d: u2.Device,
    start1: tuple[int, int],
    start2: tuple[int, int],
    end1: tuple[int, int],
    end2: tuple[int, int],
    steps: int = 20,
) -> None:
    """
    Two-finger pinch zoom defined by two image boxes (e.g. on a moving/zooming image).

    Start box: image bounds at gesture start -> finger positions at start.
    End box: image bounds after zoom -> finger positions at end.

    - start1 = (x, y) top-left of start box = first finger start position.
    - start2 = (x, y) bottom-right of start box = second finger start position.
    - end1 = (x, y) top-left of end box = first finger end position.
    - end2 = (x, y) bottom-right of end box = second finger end position.

    :param d: uiautomator2 device
    :param start1: (x, y) top-left of start box
    :param start2: (x, y) bottom-right of start box
    :param end1: (x, y) top-left of zoomed box
    :param end2: (x, y) bottom-right of zoomed box
    :param steps: gesture interpolation steps (default 50)
    """
    start1 = (int(start1[0]), int(start1[1]))
    start2 = (int(start2[0]), int(start2[1]))
    end1 = (int(end1[0]), int(end1[1]))
    end2 = (int(end2[0]), int(end2[1]))
    steps = max(10, min(200, int(steps)))
    d().gesture(start1, start2, end1, end2, steps=steps)


def step_api_to_frontend_action(step_api_action, default_duration=1.5):
    """
    Convert step API actions to frontend actions.
    """

    if "action" in step_api_action:
        action_type = step_api_action["action"]
    elif "action_type" in step_api_action:
        action_type = step_api_action["action_type"]
    else:
        raise ValueError("No action or action_type in step_api_action")

    action_type_map = {
        # "CLICK": "Click",
        "Click": "CLICK",
        # "TYPE": "Type",
        "Type": "TYPE",
        # "COMPLETE": "Complete",
        "Complete": "COMPLETE",
        # "INFO": "Pop",
        "Pop": "INFO",
        # "WAIT": "Wait",
        "Wait": "WAIT",
        # "AWAKE": "Awake",
        "Awake": "AWAKE",
        # "ABORT": "Abort",
        "Abort": "ABORT",
        # "SWIPE": "Scroll",
        "Scroll": "SLIDE",
        # "LONGPRESS": "LongPress",
        "LongPress": "LONGPRESS",
        # "CALL_USER": "CALL_USER",
        "CALL_USER": "CALL_USER",
        # "ZOOMINOUT": "ZOOMINOUT",
        "ZOOMINOUT": "ZOOMINOUT",

    }

    if action_type not in action_type_map:
        raise ValueError(f"Unsupported action type: {action_type}")

    frontend_action_type = action_type_map[action_type]

    action_type = action_type_map[action_type]

    frontend_action = {"action_type": frontend_action_type}

    if action_type == "CLICK":
        assert "args" in step_api_action, "Missing args in CLICK action"
        assert "normalized_point" in step_api_action["args"], "Missing normalized_point in CLICK action args"

        point = _convert_normalized_point_to_fixed_point(step_api_action["args"]["normalized_point"])
        frontend_action["point"] = point
        return frontend_action

    elif action_type == "TYPE":
        assert "args" in step_api_action, "Missing args in TYPE action"
        assert "text" in step_api_action["args"], "Missing text in TYPE action args"
        text = step_api_action["args"]["text"]
        frontend_action["value"] = text

        # keyboard_exists
        # normlized_point
        if "keyboard_exists" in step_api_action["args"]:
            frontend_action["keyboard_exists"] = step_api_action["args"]["keyboard_exists"]
        else:
            frontend_action["keyboard_exists"] = True

        if "normalized_point" in step_api_action["args"]:
            point = _convert_normalized_point_to_fixed_point(step_api_action["args"]["normalized_point"])
            frontend_action["point"] = point

        return frontend_action

    elif action_type == "COMPLETE":
        return frontend_action

    elif action_type == "INFO":
        return frontend_action

    elif action_type == "CALL_USER":
        return frontend_action

    elif action_type == "WAIT":
        assert "args" in step_api_action, "Missing args in WAIT action"
        assert "duration" in step_api_action["args"], "Missing seconds in WAIT action args"
        seconds = step_api_action["args"]["duration"]
        frontend_action["seconds"] = float(seconds)

        return frontend_action

    elif action_type == "AWAKE":
        assert "args" in step_api_action, "Missing args in AWAKE action"
        assert "text" in step_api_action["args"], "Missing text in AWAKE action args"
        text = step_api_action["args"]["text"]
        frontend_action["value"] = text

        return frontend_action

    elif action_type == "ABORT":
        return frontend_action

    elif action_type == "SLIDE":
        assert "args" in step_api_action, "Missing args in SLIDE action"
        assert "normalized_path" in step_api_action["args"], "Missing normalized_path in SLIDE action args"

        path = step_api_action["args"]["normalized_path"]
        start_point = _convert_normalized_point_to_fixed_point(path[0])
        end_point = _convert_normalized_point_to_fixed_point(path[-1])

        frontend_action["point1"] = start_point
        frontend_action["point2"] = end_point

        frontend_action["duration"] = default_duration

        return frontend_action

    elif action_type == "LONGPRESS":
        assert "args" in step_api_action, "Missing args in LONGPRESS action"
        assert "normalized_point" in step_api_action["args"], "Missing normalized_point in LONGPRESS action args"

        point = _convert_normalized_point_to_fixed_point(step_api_action["args"]["normalized_point"])
        frontend_action["point"] = point

        frontend_action["duration"] = default_duration

        return frontend_action

    else:
        raise ValueError(f"Unsupported action type: {action_type}")


def _normalize_point(point):
    """Normalize point to (x, y) from list, tuple, or dict with 'x'/'y' keys."""
    if isinstance(point, (list, tuple)) and len(point) >= 2:
        return (point[0], point[1])
    if isinstance(point, dict) and "x" in point and "y" in point:
        return (point["x"], point["y"])
    raise TypeError(
        f"point must be (x, y), [x, y], or {{'x': x, 'y': y}}, got {type(point).__name__}: {point!r}"
    )


def _convert_point_to_realworld_point(point, wm_size):
    x, y = _normalize_point(point)
    real_x = (float(x) / 1000) * wm_size[0]
    real_y = (float(y) / 1000) * wm_size[1]
    return (real_x, real_y)


def _preprocess_text_for_adb(text):
    # Keep the fuller TYPE escaping from the sibling frontend while preserving newline support.
    text = str(text)
    text = text.replace("\n", "\\n").replace("\\n", "\\\\n").replace("\t", " ")
    text = text.replace("(", "\\(").replace(")", "\\)")
    text = text.replace(" ", "\\ ").replace("#", "\\#").replace("&", "\\&").replace("'", "\\'")
    return text





def convert_zoom(point1, point2, point3, point4):
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    x3, y3 = point3[0], point3[1]
    x4, y4 = point4[0], point4[1]
    center_x, center_y = (x3 + x1) / 2, (y3 + y1) / 2
    initDistance = abs(center_y - y3)
    FinalDistrance = abs(center_y - y4)
    point = [center_x, center_y]
    initDistance = initDistance
    FinalDistrance = FinalDistrance

    return point, initDistance, FinalDistrance

def act_on_device(frontend_action, device_id, wm_size, print_command = False, reflush_app = True):
    """
    Execute the frontend action on the device.
    1. # CLICK(point=(x,y))
    2. # LONGPRESS(point=(x,y), duration=sec)
    3. # TYPE(value="string", point=None, keyboard_exists=True)  # point is the text input box; if not given, use the current focus box
    4. # SCROLL(point=(x,y), direction="up|down|left|right")  //UI-Tars only
    5. # AWAKE(value=app_name)
    6. # SLIDE(point1=(x1,y1), point2=(x2,y2), duration=sec)
    7. # BACK()   //UI-Tars only
    8. # HOME()   //UI-Tars only
    9. # COMPLETE()
    10. # ABORT()
    11. # INFO()
    12. # WAIT(seconds=sec)

    13. # HOT_KEY(key="volume_up|volume_down|power|...")

    Standard frontend action space:
    {
        "action_type": "CLICK",
        "param_key": param_value,
        ...
    }

    """
    assert "action_type" in frontend_action, "Missing action_type in frontend_action"
    frontend_action["action_type"] = ACTION_TYPE_ALIASES.get(
        frontend_action["action_type"], frontend_action["action_type"]
    )
    assert frontend_action["action_type"] in VALID_FRONTEND_ACTIONS, f"Invalid action type: {frontend_action['action_type']}"

    action_type = frontend_action["action_type"]

    if action_type == "CLICK":
        assert "point" in frontend_action, "Missing point in CLICK action"
        x, y = _convert_point_to_realworld_point(frontend_action["point"], wm_size)

        cmd = f"adb -s {device_id} shell input tap {x} {y}"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    elif action_type == "LONGPRESS":
        assert "point" in frontend_action, "Missing point in LONGPRESS action"
        assert "duration" in frontend_action, "Missing duration in LONGPRESS action"
        x, y = _convert_point_to_realworld_point(frontend_action["point"], wm_size)
        duration = frontend_action["duration"]
        cmd = f"adb -s {device_id} shell app_process -Djava.class.path=/data/local/tmp/yadb /data/local/tmp com.ysbing.yadb.Main -touch {x} {y} {int(duration * 1000)}"

        if print_command:
            print(f"Executing command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    # adb shell app_process -Djava.class.path=/data/local/tmp/yadb /data/local/tmp com.ysbing.yadb.Main -keyboard "{text}"
    elif action_type == "TYPE":
        assert "value" in frontend_action, "Missing value in TYPE action"

        value = frontend_action["value"]
        keyboard_exists = frontend_action.get("keyboard_exists", True)
        if not keyboard_exists:
            if "point" in frontend_action:
                x, y = _convert_point_to_realworld_point(frontend_action["point"], wm_size)
                cmd = f"adb -s {device_id} shell input tap {x} {y}"
                if print_command:
                    print(f"Executing command: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                time.sleep(1)
            else:
                print("Warning: keyboard does not exist and point is not given. Using current focus box.")

        escaped_value = shlex.quote(_preprocess_text_for_adb(value))
        cmd = f"adb -s {device_id} shell app_process -Djava.class.path=/data/local/tmp/yadb /data/local/tmp com.ysbing.yadb.Main -keyboard {escaped_value}"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result

    elif action_type == "SCROLL":
        assert "point" in frontend_action, "Missing point in SCROLL action"
        assert "direction" in frontend_action, "Missing direction in SCROLL action"
        x, y = _convert_point_to_realworld_point(frontend_action["point"], wm_size)

        deltax = int(0.3 * wm_size[0])
        deltay = int(0.3 * wm_size[1])

        direction = frontend_action["direction"]
        print("direction", direction)
        if direction == "down":
            x1, y1 = x, y
            x2, y2 = x, y - deltay
        elif direction == "up":
            x1, y1 = x, y
            x2, y2 = x, y + deltay
        elif direction == "left":
            x1, y1 = x, y
            x2, y2 = x - deltax, y
        elif direction == "right":
            x1, y1 = x, y
            x2, y2 = x + deltax, y
        else:
            raise ValueError(f"Invalid direction: {direction}")


        # cmd = f"adb -s {device_id} shell input swipe {x1} {y1} {x2} {y2} 1200"

        # adb push yadb /data/local/tmp & adb shell app_process -Djava.class.path=/data/local/tmp/yadb /data/local/tmp com.ysbing.yadb.Main -swipe 100 1000 100 500 1000
        # use yadb for 无惯性 non-inertial scroll
        cmd = f"adb -s {device_id} shell app_process -Djava.class.path=/data/local/tmp/yadb /data/local/tmp com.ysbing.yadb.Main -swipe {x1} {y1} {x2} {y2} 1000"

        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    elif action_type == "AWAKE":
        assert "value" in frontend_action, "Missing value in AWAKE action"
        app_name = frontend_action["value"]
        package_name = find_package_name(app_name)
        if package_name is None:
            raise ValueError(f"App name {app_name} not found in package map.")

        if reflush_app:
            cmd = f"adb -s {device_id} shell am force-stop {package_name}"
            if print_command:
                print(f"Executing command: {cmd}")

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            time.sleep(1)

        cmd = f"adb -s {device_id} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    elif action_type == "SLIDE":
        assert "point1" in frontend_action, "Missing point1 in SLIDE action"
        assert "point2" in frontend_action, "Missing point2 in SLIDE action"
        x1, y1 = _convert_point_to_realworld_point(frontend_action["point1"], wm_size)
        x2, y2 = _convert_point_to_realworld_point(frontend_action["point2"], wm_size)

        duration = frontend_action.get("duration", 10)
        cmd = f"adb -s {device_id} shell input swipe {x1} {y1} {x2} {y2} 1200"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result
    elif action_type == "LONGPRESSANDDRAG":
        assert "point1" in frontend_action, "Missing point1 in LONGPRESSANDDRAG action"
        assert "point2" in frontend_action, "Missing point2 in LONGPRESSANDDRAG action"
        x1, y1 = _convert_point_to_realworld_point(frontend_action["point1"], wm_size)
        x2, y2 = _convert_point_to_realworld_point(frontend_action["point2"], wm_size)

        # cmd = f"adb -s {device_id} shell input swipe {x1} {y1} {x2} {y2} {int(duration * 1000)}"
        pressDuration = frontend_action.get("pressDuration", 1.5)
        dragDuration = frontend_action.get("dragDuration", 2)
        # cmd = f"adb -s {device_id} shell input swipe {x1} {y1} {x2} {y2} {int(duration * 1000)}"
        cmd = f"adb -s {device_id} shell app_process -Djava.class.path=/data/local/tmp/yadb /data/local/tmp com.ysbing.yadb.Main -longPressDrag {x1} {y1} {x2} {y2} {int(pressDuration * 1000)} {int(dragDuration * 1000)}"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    elif action_type == "ZOOM":
        assert "point1" in frontend_action, "Missing point1 in ZOOM action"
        assert "point2" in frontend_action, "Missing point2 in ZOOM action"
        assert "point3" in frontend_action, "Missing point3 in ZOOM action"
        assert "point4" in frontend_action, "Missing point4 in ZOOM action"
        x1, y1 = _convert_point_to_realworld_point(frontend_action["point1"], wm_size)
        x2, y2 = _convert_point_to_realworld_point(frontend_action["point2"], wm_size)
        x3, y3 = _convert_point_to_realworld_point(frontend_action["point3"], wm_size)
        x4, y4 = _convert_point_to_realworld_point(frontend_action["point4"], wm_size)

        duration = frontend_action.get("duration", 1)
        point, initDistance, FinalDistrance = convert_zoom([x1, y1], [x2, y2], [x3, y3], [x4, y4])
        cmd = f"adb -s {device_id} shell app_process -Djava.class.path=/data/local/tmp/yadb /data/local/tmp com.ysbing.yadb.Main -pinch {point[0]} {point[1]} {initDistance} {FinalDistrance} {int(duration * 1000)}"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result
    elif action_type == "BACK":
        cmd = f"adb -s {device_id} shell input keyevent 4"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    elif action_type == "HOME":
        cmd = f"adb -s {device_id} shell input keyevent 3"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result
    elif action_type == "ENTER":
        cmd = f"adb -s {device_id} shell input keyevent 66"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    elif action_type == "COMPLETE":
        if print_command:
            print("Task completed.")
        return None

    elif action_type == "ABORT":
        if print_command:
            print("Task aborted.")
        return None

    elif action_type == "INFO":
        if print_command:
            print("Info action executed.")
        return None

    elif action_type == "CALL_USER":
        if print_command:
            print("Info action executed.")
        return None

    elif action_type == "WAIT":
        # assert "seconds" in frontend_action, "Missing seconds in WAIT action"
        seconds = frontend_action.get("seconds", 3)
        if print_command:
            print(f"Waiting for {seconds} seconds.")
        time.sleep(seconds)
        return None

    elif action_type == "HOT_KEY":
        assert "key" in frontend_action, "Missing key in HOT_KEY action"
        key = frontend_action["key"]
        key_event_map = {
            "volume_up": 24,
            "volume_down": 25,
            "power": 26,
            "home": 3,
            "back": 4,
            "menu": 82,
        }
        if key.lower() not in key_event_map:
            raise ValueError(f"Unsupported hot key: {key}")

        key_event = key_event_map[key.lower()]
        cmd = f"adb -s {device_id} shell input keyevent {key_event}"
        if print_command:
            print(f"Executing command: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return result

    elif action_type == "CALL_USER":
        time.sleep(10)
        if print_command:
            print("Info action executed.")
        return None
    elif action_type == "ZOOMINOUT":
        def _get_point(action: dict, key: str) -> tuple:
            val = action.get(key)
            if val is not None and not isinstance(val, (int, float)):
                return _normalize_point(val)
            x_key, y_key = f"{key}_x", f"{key}_y"
            if x_key in action and y_key in action:
                return (action[x_key], action[y_key])
            raise ValueError(f"ZOOMINOUT: {key} must be (x,y)/[x,y]/dict or {x_key}&{y_key}, got {type(val).__name__}")

        start1_pt = _get_point(frontend_action, "start1")
        start2_pt = _get_point(frontend_action, "start2")
        end1_pt = _get_point(frontend_action, "end1")
        end2_pt = _get_point(frontend_action, "end2")
        start1 = _convert_point_to_realworld_point(start1_pt, wm_size)
        start2 = _convert_point_to_realworld_point(start2_pt, wm_size)
        end1 = _convert_point_to_realworld_point(end1_pt, wm_size)
        end2 = _convert_point_to_realworld_point(end2_pt, wm_size)
        start1 = (int(start1[0]), int(start1[1]))
        start2 = (int(start2[0]), int(start2[1]))
        end1 = (int(end1[0]), int(end1[1]))
        end2 = (int(end2[0]), int(end2[1]))
        steps = int(frontend_action.get("steps", 20))
        steps = max(10, min(200, steps))
        d = u2.connect(device_id)
        ZOOMPOINT(d, start1, start2, end1, end2, steps=steps)
        if print_command:
            print(f"ZOOMINOUT: ZOOMPOINT(start1={start1}, start2={start2}, end1={end1}, end2={end2}, steps={steps})")
        return None

    else:
        raise ValueError(f"Unsupported action type: {action_type}")
