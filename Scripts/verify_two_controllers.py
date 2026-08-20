#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify awff_pid and pid_awff_linear_eso GraphicalRunners via CheckModel
Output MCP command requests for Claude to execute
"""

import sys
import json

def main():
    models_to_check = [
        "MoSimQuadrotorModel.Experiment.AwffControllers.AwffPidGraphicalRunner",
        "MoSimQuadrotorModel.Experiment.AwffControllers.PidAwffLinearEsoGraphicalRunner",
    ]

    print("=" * 80)
    print("验证 AWFF 控制器 GraphicalRunner")
    print("=" * 80)
    print("\nMCP_CHECK_MODEL_REQUEST")
    print(json.dumps({
        "models": models_to_check,
        "action": "check_model"
    }, indent=2))
    print("MCP_CHECK_MODEL_REQUEST_END")

    return 0

if __name__ == "__main__":
    sys.exit(main())
