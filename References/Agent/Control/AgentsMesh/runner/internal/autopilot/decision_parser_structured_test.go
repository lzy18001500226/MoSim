package autopilot

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Tests for structured JSON decision parsing

func TestDecisionParser_ParseStructuredDecision_Continue(t *testing.T) {
	dp := NewDecisionParser()

	input := `{
		"decision": {
			"type": "continue",
			"confidence": 0.9,
			"reasoning": "任务正在进展中，Pod 已完成文件创建"
		},
		"progress": {
			"summary": "已完成 2/5 个子任务",
			"completed": ["创建项目结构", "编写主文件"],
			"remaining": ["添加测试", "更新文档"]
		},
		"action": {
			"type": "send_input",
			"content": "请继续完成测试文件",
			"reason": "引导 Pod 进入下一步"
		}
	}`

	decision := dp.ParseDecision(input)

	assert.Equal(t, DecisionContinue, decision.Type)
	assert.Equal(t, 0.9, decision.Confidence)
	assert.Contains(t, decision.Reasoning, "任务正在进展中")

	// Progress
	assert.NotNil(t, decision.Progress)
	assert.Equal(t, "已完成 2/5 个子任务", decision.Progress.Summary)
	assert.Len(t, decision.Progress.CompletedSteps, 2)
	assert.Len(t, decision.Progress.RemainingSteps, 2)

	// Action
	assert.NotNil(t, decision.Action)
	assert.Equal(t, "send_input", decision.Action.Type)
	assert.Equal(t, "请继续完成测试文件", decision.Action.Content)
}

func TestDecisionParser_ParseStructuredDecision_Completed(t *testing.T) {
	dp := NewDecisionParser()

	input := `{
		"decision": {
			"type": "completed",
			"confidence": 1.0,
			"reasoning": "所有子任务已完成，测试通过"
		},
		"progress": {
			"summary": "任务 100% 完成",
			"completed": ["步骤1", "步骤2", "步骤3"],
			"remaining": [],
			"percent": 100
		},
		"action": {
			"type": "none",
			"content": "",
			"reason": "任务已完成"
		}
	}`

	decision := dp.ParseDecision(input)

	assert.Equal(t, DecisionCompleted, decision.Type)
	assert.Equal(t, 1.0, decision.Confidence)
	assert.NotNil(t, decision.Progress)
	assert.Equal(t, 100, decision.Progress.Percent)
	assert.Empty(t, decision.Progress.RemainingSteps)
}

func TestDecisionParser_ParseStructuredDecision_NeedHelp(t *testing.T) {
	dp := NewDecisionParser()

	input := `{
		"decision": {
			"type": "need_help",
			"confidence": 0.8,
			"reasoning": "Pod 遇到权限错误"
		},
		"help_request": {
			"reason": "无法安装依赖包",
			"context": "正在执行任务 '添加数据处理功能'",
			"terminal_excerpt": "npm ERR! EACCES",
			"suggestions": [
				{"action": "approve", "label": "批准：以 sudo 权限重试"},
				{"action": "skip", "label": "跳过：不安装此依赖"}
			]
		}
	}`

	decision := dp.ParseDecision(input)

	assert.Equal(t, DecisionNeedHumanHelp, decision.Type)
	assert.NotNil(t, decision.HelpRequest)
	assert.Equal(t, "无法安装依赖包", decision.HelpRequest.Reason)
	assert.Contains(t, decision.HelpRequest.TerminalExcerpt, "npm ERR!")
	assert.Len(t, decision.HelpRequest.Suggestions, 2)
	assert.Equal(t, "approve", decision.HelpRequest.Suggestions[0].Action)
}

func TestDecisionParser_ParseStructuredDecision_GiveUp(t *testing.T) {
	dp := NewDecisionParser()

	input := `{
		"decision": {
			"type": "give_up",
			"confidence": 0.7,
			"reasoning": "无法完成任务，架构不兼容"
		}
	}`

	decision := dp.ParseDecision(input)

	assert.Equal(t, DecisionGiveUp, decision.Type)
	assert.Contains(t, decision.Reasoning, "架构不兼容")
}
