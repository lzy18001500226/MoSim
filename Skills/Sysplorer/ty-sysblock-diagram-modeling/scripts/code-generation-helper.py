#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sysblock 建模辅助脚本

提供常用的 Sysblock 模型创建、参数设置、仿真和分析功能
"""

import json
from typing import Dict, List, Optional, Tuple


class SysblockModelBuilder:
    """Sysblock 模型构建器"""
    
    # 组件路径映射
    COMPONENT_PATHS = {
        # 信号源
        "Step": "SysplorerEmbeddedCoder.Sources.Step",
        "SineWave": "SysplorerEmbeddedCoder.Sources.SineWave",
        "Ramp": "SysplorerEmbeddedCoder.Sources.Ramp",
        "Constant": "SysplorerEmbeddedCoder.Sources.Constant",
        "PulseGenerator": "SysplorerEmbeddedCoder.Sources.PulseGenerator",
        
        # 数学运算
        "Gain": "SysplorerEmbeddedCoder.MathOperation.Gain",
        "Sum": "SysplorerEmbeddedCoder.MathOperation.Sum",
        "Product": "SysplorerEmbeddedCoder.MathOperation.Product",
        "Abs": "SysplorerEmbeddedCoder.MathOperation.Abs",
        
        # 连续系统
        "Integrator": "SysplorerEmbeddedCoder.Continuous.Integrator",
        "Derivative": "SysplorerEmbeddedCoder.Continuous.Derivative",
        "TransferFcn": "SysplorerEmbeddedCoder.Continuous.TransferFcn",
        
        # 离散系统
        "UnitDelay": "SysplorerEmbeddedCoder.Discrete.UnitDelay",
        
        # 逻辑运算
        "RelationalOperator": "SysplorerEmbeddedCoder.LogicAndBitOperation.RelationalOperator",
        
        # 观测
        "Scope": "SysplorerEmbeddedCoder.Utilities.Scope",
        "Display": "SysplorerEmbeddedCoder.Utilities.Display",
    }
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.components = []
        self.connections = []
        self.params = {}
        
    def add_step(self, name: str, x: float, y: float, 
                 time: float = 0, before: float = 0, after: float = 1) -> 'SysblockModelBuilder':
        """添加阶跃信号"""
        self.components.append({
            "type": "Step",
            "name": name,
            "x": x,
            "y": y,
            "params": {"stepTime": time, "initialValue": before, "finalValue": after}
        })
        return self
    
    def add_gain(self, name: str, x: float, y: float, k: float = 1.0) -> 'SysblockModelBuilder':
        """添加增益"""
        self.components.append({
            "type": "Gain",
            "name": name,
            "x": x,
            "y": y,
            "params": {"Gain": k}
        })
        return self
    
    def add_sum(self, name: str, x: float, y: float, 
                inputs: str = "++") -> 'SysblockModelBuilder':
        """添加加法器"""
        self.components.append({
            "type": "Sum",
            "name": name,
            "x": x,
            "y": y,
            "params": {"inputs": inputs}
        })
        return self
    
    def add_integrator(self, name: str, x: float, y: float, 
                       init_cond: float = 0) -> 'SysblockModelBuilder':
        """添加积分器"""
        self.components.append({
            "type": "Integrator",
            "name": name,
            "x": x,
            "y": y,
            "params": {"initCond": init_cond}
        })
        return self
    
    def add_transfer_fcn(self, name: str, x: float, y: float,
                        numerator: List[float], denominator: List[float]) -> 'SysblockModelBuilder':
        """添加传递函数"""
        self.components.append({
            "type": "TransferFcn",
            "name": name,
            "x": x,
            "y": y,
            "params": {"numerator": numerator, "denominator": denominator}
        })
        return self
    
    def add_scope(self, name: str, x: float, y: float) -> 'SysblockModelBuilder':
        """添加示波器"""
        self.components.append({
            "type": "Scope",
            "name": name,
            "x": x,
            "y": y
        })
        return self
    
    def connect(self, src: str, dst: str) -> 'SysblockModelBuilder':
        """连接端口"""
        self.connections.append({"src": src, "dst": dst})
        return self
    
    def generate_python_script(self) -> str:
        """生成 Python 脚本"""
        lines = [
            "import mworks.sysplorer as mwsp",
            "",
            f"model_name = '{self.model_name}'",
            "",
            "# 创建模型",
            f"mwsp.NewModel(model_name, 'Sysblock')",
            f"mwsp.OpenModel(model_name)",
            "",
            "# 添加组件"
        ]
        
        for comp in self.components:
            type_path = self.COMPONENT_PATHS[comp["type"]]
            lines.append(f'mwsp.AddComponent("{type_path}", model_name, "{comp["name"]}", {comp["x"]}, {comp["y"]})')
            
            for param, value in comp.get("params", {}).items():
                lines.append(f'mwsp.SetModelParamValue(model_name, "{comp["name"]}", "{param}", "{value}")')
            
            lines.append("")
        
        lines.append("# 连接端口")
        for conn in self.connections:
            lines.append(f'mwsp.ConnectPort(model_name, "{conn["src"]}", "{conn["dst"]}")')
        
        lines.extend([
            "",
            "# 仿真",
            f'mwsp.SimulateModelEx(model_name, {{"stopTime": 5.0, "interval": 0.01}})',
            "",
            "# 绘图",
            'mwsp.CreatePlot(y=["your_output_var"])'
        ])
        
        return "\n".join(lines)


def calculate_performance(time: List[float], value: List[float], 
                         setpoint: float) -> Dict[str, float]:
    """计算控制系统性能指标"""
    import numpy as np
    
    time = np.array(time)
    value = np.array(value)
    
    # 稳态值（取最后10%的平均值）
    steady_state = np.mean(value[int(len(value)*0.9):])
    
    # 稳态误差
    steady_error = abs(setpoint - steady_state) / setpoint * 100
    
    # 峰值和超调量
    max_value = np.max(value)
    overshoot = (max_value - steady_state) / steady_state * 100
    
    # 上升时间 (10% -> 90%)
    idx_10 = np.where(value >= setpoint * 0.1)[0]
    idx_90 = np.where(value >= setpoint * 0.9)[0]
    
    if len(idx_10) > 0 and len(idx_90) > 0:
        rise_time = time[idx_90[0]] - time[idx_10[0]]
    else:
        rise_time = float('inf')
    
    # 调节时间 (±2% 误差带)
    lower = steady_state * 0.98
    upper = steady_state * 1.02
    
    # 找到首次进入误差带的位置
    in_band = (value >= lower) & (value <= upper)
    settling_indices = np.where(in_band)[0]
    
    if len(settling_indices) > 0:
        # 从后往前找，确保稳定
        for i in range(len(settling_indices) - 1, -1, -1):
            if not in_band[settling_indices[i]]:
                settling_time = time[settling_indices[i + 1]] if i + 1 < len(settling_indices) else time[-1]
                break
        else:
            settling_time = time[settling_indices[0]] if len(settling_indices) > 0 else time[-1]
    else:
        settling_time = float('inf')
    
    return {
        "steady_state": float(steady_state),
        "steady_error_percent": float(steady_error),
        "max_value": float(max_value),
        "overshoot_percent": float(overshoot),
        "rise_time": float(rise_time),
        "settling_time": float(settling_time)
    }


if __name__ == "__main__":
    # 示例：创建 PI 控制系统
    builder = SysblockModelBuilder("PI_Control")
    
    builder.add_step("Setpoint", -80, 0, time=0, before=0, after=100) \
            .add_sum("Error_Sum", -40, 0, inputs="+-") \
            .add_gain("Kp", 0, -30, k=1.0) \
            .add_gain("Ki", 0, 30, k=1.0) \
            .add_integrator("Integrator", 40, 30, init_cond=0) \
            .add_sum("PI_Sum", 80, 0, inputs="++") \
            .add_transfer_fcn("Plant", 120, 0, numerator=[1], denominator=[1, 1]) \
            .add_scope("Scope", 160, 0) \
            .connect("Setpoint.y", "Error_Sum.u1") \
            .connect("Error_Sum.y", "Kp.u") \
            .connect("Error_Sum.y", "Ki.u") \
            .connect("Ki.y", "Integrator.u1") \
            .connect("Kp.y", "PI_Sum.u1") \
            .connect("Integrator.y", "PI_Sum.u2") \
            .connect("PI_Sum.y", "Plant.u") \
            .connect("Plant.y", "Scope.u1") \
            .connect("Plant.y", "Error_Sum.u2")
    
    script = builder.generate_python_script()
    print(script)