#!/usr/bin/env python3
"""Generate the reviewed, UI-only Model Studio APP Designer project."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "app.jl"
NATIVE_DIR = ROOT / "native_app"
NATIVE_SOURCE = NATIVE_DIR / "app.jl"
OUTPUT = NATIVE_DIR / "MoSimModelStudioApp.slapp"
FIGURE_ID = "mosim-model-studio-figure"

ACTIVE_COLOR = [0.08, 0.36, 0.43]
INACTIVE_COLOR = [0.88, 0.91, 0.92]
SECTION_COLOR = [0.12, 0.25, 0.32]
WAIT_COLOR = [0.98, 0.93, 0.80]


def callback_body(source: str) -> str:
    return textwrap.indent(textwrap.dedent(source).strip(), "            ")


def common(component_id: str, component_type: str, variable: str, position: list[int]) -> dict:
    return {
        "id": component_id,
        "pid": FIGURE_ID,
        "state": {"position": position},
        "callbackFcns": {},
        "type": component_type,
        "visible": True,
        "enable": True,
        "tooltip": "",
        "contextMenu": [],
        "position": position,
        "interruptible": False,
        "busyAction": "queue",
        "tag": "",
        "variableName": variable,
    }


def label(component_id: str, variable: str, text: str, position: list[int], **overrides) -> dict:
    component = common(component_id, "label", variable, position)
    component.update(
        {
            "text": text,
            "interpreter": "none",
            "horizontalAlignment": "left",
            "verticalAlignment": "center",
            "wordWrap": False,
            "fontName": "Helvetica",
            "fontSize": 12,
            "fontWeight": "normal",
            "fontAngle": "normal",
            "fontColor": [0, 0, 0],
            "backgroundColor": [],
        }
    )
    component.update(overrides)
    component["state"].update(
        {
            "text": text,
            **{
                key: value
                for key, value in overrides.items()
                if key in {"fontSize", "fontWeight", "wordWrap", "backgroundColor"}
            },
        }
    )
    return component


def section(component_id: str, variable: str, text: str, position: list[int]) -> dict:
    return label(
        component_id,
        variable,
        "  " + text,
        position,
        fontWeight="bold",
        fontColor=[1.0, 1.0, 1.0],
        backgroundColor=SECTION_COLOR,
    )


def button(
    component_id: str,
    variable: str,
    text: str,
    callback: str,
    position: list[int],
    *,
    enabled: bool = True,
    background: list[float] | None = None,
    font_color: list[float] | None = None,
) -> dict:
    component = common(component_id, "button", variable, position)
    component["enable"] = enabled
    component.update(
        {
            "text": text,
            "wordWrap": False,
            "horizontalAlignment": "center",
            "verticalAlignment": "center",
            "icon": "",
            "iconAlignment": "left",
            "fontName": "Helvetica",
            "fontSize": 12,
            "fontWeight": "bold",
            "fontAngle": "normal",
            "fontColor": font_color or [0.20, 0.25, 0.28],
            "backgroundColor": background or [0.94, 0.94, 0.94],
            "buttonPushedFcn": callback,
        }
    )
    component["callbackFcns"] = {"buttonPushedFcn": callback}
    component["state"].update(
        {"text": text, "buttonPushedFcn": callback, "enable": enabled}
    )
    return component


def dropdown(
    component_id: str,
    variable: str,
    display_label: str,
    items: list[str],
    value: str,
    position: list[int],
    *,
    enabled: bool = True,
) -> dict:
    component = common(component_id, "dropdown", variable, position)
    component["enable"] = enabled
    component.update(
        {
            "label": display_label,
            "value": value,
            "items": items,
            "itemsData": [],
            "placeholder": "",
            "fontName": "Helvetica",
            "fontSize": 12,
            "fontWeight": "normal",
            "fontAngle": "normal",
            "fontColor": [0, 0, 0],
            "backgroundColor": [1, 1, 1],
            "editable": False,
            "valueChangedFcn": "SelectionChanged",
        }
    )
    component["callbackFcns"] = {"valueChangedFcn": "SelectionChanged"}
    component["state"].update(
        {
            "label": display_label,
            "items": items,
            "value": value,
            "enable": enabled,
            "valueChangedFcn": "SelectionChanged",
        }
    )
    return component


def slider(
    component_id: str,
    variable: str,
    display_label: str,
    value: float,
    limits: list[float],
    ticks: list[float],
    tick_labels: list[str],
    position: list[int],
) -> dict:
    component = common(component_id, "slider", variable, position)
    component.update(
        {
            "label": display_label,
            "value": value,
            "limits": limits,
            "majorTicks": ticks,
            "majorTickLabels": tick_labels,
            "minorTicks": [],
            "majorTicksMode": "manual",
            "majorTickLabelsMode": "manual",
            "minorTicksMode": "auto",
            "fontName": "Helvetica",
            "fontSize": 11,
            "fontWeight": "normal",
            "fontAngle": "normal",
            "fontColor": [0, 0, 0],
            "valueChangedFcn": "InjectionChanged",
        }
    )
    component["callbackFcns"] = {"valueChangedFcn": "InjectionChanged"}
    component["state"].update(
        {
            "label": display_label,
            "value": value,
            "limits": limits,
            "majorTicks": ticks,
            "majorTickLabels": tick_labels,
            "valueChangedFcn": "InjectionChanged",
        }
    )
    return component


def build_children() -> list[dict]:
    return [
        label("title", "TitleLabel", "MoSim Studio", [24, 16, 520, 34], fontSize=24, fontWeight="bold", fontColor=[0.08, 0.16, 0.22], horizontalAlignment="left"),
        button("mode-offline", "OfflineModeButton", "离线建模验证", "OfflineModePressed", [24, 82, 190, 40], background=INACTIVE_COLOR),
        button("mode-live", "LiveModeButton", "实时联合仿真", "LiveModePressed", [218, 82, 190, 40], background=ACTIVE_COLOR, font_color=[1, 1, 1]),
        button("mode-deploy", "DeployModeButton", "生成代码部署", "DeployModePressed", [412, 82, 190, 40], background=INACTIVE_COLOR),
        button("mode-assistant", "AssistantModeButton", "MoSim 助手", "AssistantModePressed", [606, 82, 190, 40], background=INACTIVE_COLOR),
        label("mode-status", "ModeStatusLabel", "实时联合仿真  |  RT0 能力待验证，MWORKS Live 当前可见禁用", [814, 82, 602, 40], horizontalAlignment="right", wordWrap=True, fontColor=[0.25, 0.32, 0.36]),
        section("config-section", "ConfigSectionLabel", "控制链与实验 Profile", [24, 144, 420, 34]),
        section("chain-section", "ChainSectionLabel", "职责、接口与能力门禁", [468, 144, 470, 34]),
        section("injection-section", "InjectionSectionLabel", "故障注入与运行状态", [962, 144, 454, 34]),
        dropdown("profile", "ProfileDropDown", "实验 Profile", ["official_pid_attitude_thrust_v1 [候选]", "official_pid + awff_v1 [候选]"], "official_pid_attitude_thrust_v1 [候选]", [24, 192, 420, 32]),
        dropdown("mission", "MissionDropDown", "任务轨迹", ["起飞-悬停-降落"], "起飞-悬停-降落", [24, 240, 420, 32]),
        dropdown("position", "PositionDropDown", "位置 / 平动外环", ["PX4CTRL 官方位置外环 PID"], "PX4CTRL 官方位置外环 PID", [24, 288, 420, 32]),
        dropdown("attitude", "AttitudeDropDown", "姿态 / 角速度内环", ["PX4 内置姿态/角速度环 [锁定]", "INDI [当前模式不可用]", "SMC [当前模式不可用]", "Backstepping [当前模式不可用]"], "PX4 内置姿态/角速度环 [锁定]", [24, 336, 420, 32], enabled=False),
        dropdown("augmentation", "AugmentationDropDown", "增强与扰动补偿", ["无", "AWFF", "L1 [门禁待通过]", "DOB/ESO [门禁待通过]", "模糊补偿 [门禁待通过]", "神经网络补偿 [门禁待通过]"], "无", [24, 384, 420, 32]),
        dropdown("safety", "SafetyDropDown", "安全层", ["基础限幅", "QP Safety Filter [门禁待通过]", "Return-and-Land [门禁待通过]", "CBF [门禁待通过]"], "基础限幅", [24, 432, 420, 32]),
        dropdown("output", "OutputDropDown", "输出边界", ["ATTITUDE_THRUST [锁定]"], "ATTITUDE_THRUST [锁定]", [24, 480, 420, 32], enabled=False),
        label("profile-summary", "ProfileSummaryLabel", "实验 Profile\nofficial_pid_attitude_thrust_v1 [候选]\n\n任务：起飞-悬停-降落\n外环：PX4CTRL 官方位置外环 PID\n增强：无", [24, 528, 420, 118], verticalAlignment="top", wordWrap=True, backgroundColor=[0.91, 0.94, 0.95]),
        label("capability", "CapabilityLabel", "实时能力门禁\n候选 100 Hz / 10 ms；RT0 前不可准备飞行，不得把候选参数写成已验证能力。", [24, 654, 420, 76], verticalAlignment="top", wordWrap=True, backgroundColor=WAIT_COLOR),
        label("chain", "ChainLabel", "控制链\n\n任务 / 参考 -> 位置外环 -> 期望姿态与总推力\n-> PX4 内置姿态 / 角速度环 -> 控制分配 -> 四电机\n\nATTITUDE_THRUST v1 中，自研姿态内环不可在线选择。", [468, 192, 470, 190], verticalAlignment="top", wordWrap=True, backgroundColor=[0.89, 0.94, 0.96]),
        label("contract", "ContractLabel", "三方职责\n\nModel Studio：配置、校验、发布、MIL / codegen、prepare\nQGC：连接、解锁、起飞、任务、降落、安全停止\nOrchestrator：唯一状态机、命令裁决和 RunManifest", [468, 394, 470, 144], verticalAlignment="top", wordWrap=True, backgroundColor=[0.94, 0.95, 0.95]),
        label("timing", "TimingLabel", "候选实时合同（未验证）\n\nframe: mosim_enu_flu_quaternion_xyzw_v1\nrate: 100 Hz  |  deadline: 10 ms\ncommand age: 50 ms  |  failsafe escalation: 100 ms\n\nRT0 未通过，MWORKS Live 保持禁用。", [468, 550, 470, 180], verticalAlignment="top", wordWrap=True, backgroundColor=WAIT_COLOR),
        slider("wind", "WindSlider", "风速待应用值（m/s，方向固定）", 0.0, [0.0, 20.0], [0.0, 5.0, 10.0, 15.0, 20.0], ["0", "5", "10", "15", "20"], [962, 194, 454, 52]),
        slider("motor1", "Motor1Slider", "电机 1 效率", 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"], [962, 254, 454, 52]),
        slider("motor2", "Motor2Slider", "电机 2 效率", 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"], [962, 314, 454, 52]),
        slider("motor3", "Motor3Slider", "电机 3 效率", 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"], [962, 374, 454, 52]),
        slider("motor4", "Motor4Slider", "电机 4 效率", 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"], [962, 434, 454, 52]),
        label("injection-values", "InjectionValuesLabel", "待应用值\n风速 0.0 m/s  |  电机效率 1.00 / 1.00 / 1.00 / 1.00\n\n实际值\n风速 0.0 m/s  |  电机效率 1.00 / 1.00 / 1.00 / 1.00", [962, 498, 454, 94], verticalAlignment="top", wordWrap=True, backgroundColor=[0.94, 0.95, 0.95]),
        button("apply-injection", "ApplyInjectionButton", "应用", "ApplyInjectionPressed", [962, 604, 216, 36]),
        button("restore-injection", "RestoreInjectionButton", "恢复正常", "RestoreInjectionPressed", [1200, 604, 216, 36]),
        label("manifest", "ManifestLabel", "运行状态\nRunManifest：尚未生成\nProfile：未冻结  |  QGC：未交接  |  实际故障：正常", [962, 652, 454, 78], verticalAlignment="top", wordWrap=True, backgroundColor=[0.93, 0.94, 0.94]),
        button("validate", "ValidateButton", "校验配置", "ValidatePressed", [24, 754, 140, 38]),
        button("publish", "PublishButton", "发布 Profile", "PublishPressed", [176, 754, 140, 38]),
        button("prepare", "PrepareButton", "准备运行", "PreparePressed", [328, 754, 140, 38], enabled=False),
        button("qgc", "QgcButton", "进入 QGC", "QgcPressed", [480, 754, 140, 38], enabled=False),
        button("safe-stop", "SafeStopButton", "请求安全停止", "SafeStopPressed", [632, 754, 140, 38], enabled=False),
        button("open-model", "OpenModelButton", "打开模型", "OpenModelPressed", [784, 754, 140, 38]),
        button("mil", "MilButton", "运行 MWORKS MIL", "MilPressed", [936, 754, 150, 38], enabled=False),
        button("codegen", "CodegenButton", "生成 C 代码", "CodegenPressed", [1098, 754, 140, 38], enabled=False),
        button("result", "ResultButton", "打开结果", "ResultPressed", [1250, 754, 166, 38]),
        label("status", "StatusLabel", "界面审核版已就绪。所有按钮仅演示状态，不连接 MWORKS、Gazebo、QGC 或 Orchestrator。", [24, 810, 1392, 62], verticalAlignment="top", wordWrap=True, backgroundColor=[0.90, 0.93, 0.94]),
    ]


def action_callback(action: str) -> str:
    return callback_body(
        f'app.StatusLabel.Text = "界面审核模式：已触发“{action}”界面状态，未连接 MWORKS、QGC 或 Orchestrator。"'
    )


def build_callbacks() -> list[dict]:
    callbacks = [
        {"name": "OfflineModePressed", "code": callback_body('app.set_mode("offline")')},
        {"name": "LiveModePressed", "code": callback_body('app.set_mode("live")')},
        {"name": "DeployModePressed", "code": callback_body('app.set_mode("deploy")')},
        {"name": "AssistantModePressed", "code": callback_body('app.set_mode("assistant")')},
        {"name": "SelectionChanged", "code": callback_body("app.refresh_summary()\napp.StatusLabel.Text = \"配置已修改，尚未校验或发布。\"")},
        {"name": "InjectionChanged", "code": callback_body("app.InjectionChanged(nothing)")},
        {"name": "ApplyInjectionPressed", "code": action_callback("应用故障")},
        {"name": "RestoreInjectionPressed", "code": callback_body("app.RestoreInjectionPressed(nothing)")},
    ]
    for name, action in [
        ("ValidatePressed", "校验配置"),
        ("PublishPressed", "发布 Profile"),
        ("PreparePressed", "准备运行"),
        ("QgcPressed", "进入 QGC"),
        ("SafeStopPressed", "请求安全停止"),
        ("OpenModelPressed", "打开模型"),
        ("MilPressed", "运行 MWORKS MIL"),
        ("CodegenPressed", "生成 C 代码"),
        ("ResultPressed", "打开结果"),
    ]:
        callbacks.append({"name": name, "code": action_callback(action)})
    return callbacks


def build_project() -> dict:
    return {
        "name": "MoSimModelStudioReviewApp",
        "callbackFunctions": build_callbacks(),
        "customPrivateFunctions": [],
        "customPublicFunctions": [],
        "customPrivateProperties": [],
        "customPublicProperties": [],
        "userLoadedModule": "",
        "figure": {
            "id": FIGURE_ID,
            "state": {},
            "callbackFcns": {},
            "type": "figure",
            "position": [30, 30, 1440, 900],
            "name": "MoSim Studio",
            "color": [0.96, 0.97, 0.97],
            "tag": "",
            "children": build_children(),
            "visible": True,
            "variableName": "UIFigure",
        },
        "info": {
            "type": "app",
            "name": "MoSim Studio",
            "version": "0.6.0",
            "author": "MoSim",
            "description": "四工作台控制器配置、模型验证、QGC 交接与本地操作指引界面审核版。",
            "icon": "",
            "startupFcn": "",
        },
        "code": SOURCE.read_text(encoding="utf-8"),
    }


def main() -> None:
    NATIVE_DIR.mkdir(parents=True, exist_ok=True)
    NATIVE_SOURCE.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    OUTPUT.write_text(
        json.dumps(build_project(), ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
