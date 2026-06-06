"""Tests for pentestagent.agents.state."""

import time

import pytest

from pentestagent.agents.state import AgentState, AgentStateManager, StateTransition


class TestAgentStateEnum:
    def test_all_states_exist(self):
        expected = {"IDLE", "THINKING", "EXECUTING", "WAITING_INPUT", "COMPLETE", "ERROR"}
        actual = {s.name for s in AgentState}
        assert expected == actual

    def test_state_values_are_strings(self):
        for state in AgentState:
            assert isinstance(state.value, str)

    def test_state_values_are_unique(self):
        values = [s.value for s in AgentState]
        assert len(values) == len(set(values))


class TestAgentStateManagerInit:
    def test_initial_state_is_idle(self):
        mgr = AgentStateManager()
        assert mgr.current_state == AgentState.IDLE

    def test_initial_history_is_empty(self):
        mgr = AgentStateManager()
        assert mgr.history == []

    def test_initial_metadata_is_empty(self):
        mgr = AgentStateManager()
        assert mgr.metadata == {}


class TestValidTransitions:
    def test_idle_to_thinking(self):
        mgr = AgentStateManager()
        assert mgr.transition_to(AgentState.THINKING) is True
        assert mgr.current_state == AgentState.THINKING

    def test_idle_to_error(self):
        mgr = AgentStateManager()
        assert mgr.transition_to(AgentState.ERROR) is True

    def test_thinking_to_executing(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert mgr.transition_to(AgentState.EXECUTING) is True

    def test_thinking_to_waiting_input(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert mgr.transition_to(AgentState.WAITING_INPUT) is True

    def test_thinking_to_complete(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert mgr.transition_to(AgentState.COMPLETE) is True

    def test_thinking_to_error(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert mgr.transition_to(AgentState.ERROR) is True

    def test_executing_to_thinking(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.EXECUTING)
        assert mgr.transition_to(AgentState.THINKING) is True

    def test_executing_to_error(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.EXECUTING)
        assert mgr.transition_to(AgentState.ERROR) is True

    def test_executing_to_complete(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.EXECUTING)
        assert mgr.transition_to(AgentState.COMPLETE) is True

    def test_complete_to_idle(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.COMPLETE)
        assert mgr.transition_to(AgentState.IDLE) is True

    def test_error_to_idle(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.ERROR)
        assert mgr.transition_to(AgentState.IDLE) is True


class TestInvalidTransitions:
    def test_idle_cannot_go_to_executing(self):
        mgr = AgentStateManager()
        assert mgr.transition_to(AgentState.EXECUTING) is False
        assert mgr.current_state == AgentState.IDLE

    def test_idle_cannot_go_to_complete(self):
        mgr = AgentStateManager()
        assert mgr.transition_to(AgentState.COMPLETE) is False

    def test_idle_cannot_go_to_waiting_input(self):
        mgr = AgentStateManager()
        assert mgr.transition_to(AgentState.WAITING_INPUT) is False

    def test_complete_cannot_go_to_thinking(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.COMPLETE)
        assert mgr.transition_to(AgentState.THINKING) is False

    def test_error_cannot_go_to_thinking(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.ERROR)
        assert mgr.transition_to(AgentState.THINKING) is False

    def test_failed_transition_does_not_change_state(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.COMPLETE)
        mgr.transition_to(AgentState.THINKING)  # invalid
        assert mgr.current_state == AgentState.COMPLETE

    def test_failed_transition_not_added_to_history(self):
        mgr = AgentStateManager()
        count_before = len(mgr.history)
        mgr.transition_to(AgentState.EXECUTING)  # invalid from IDLE
        assert len(mgr.history) == count_before


class TestTransitionHistory:
    def test_successful_transition_recorded_in_history(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert len(mgr.history) == 1
        assert mgr.history[0].from_state == AgentState.IDLE
        assert mgr.history[0].to_state == AgentState.THINKING

    def test_reason_stored_in_history(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING, reason="starting task")
        assert mgr.history[0].reason == "starting task"

    def test_transition_without_reason(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert mgr.history[0].reason is None

    def test_multiple_transitions_recorded(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.EXECUTING)
        mgr.transition_to(AgentState.COMPLETE)
        assert len(mgr.history) == 3

    def test_history_timestamps_are_ordered(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        time.sleep(0.01)
        mgr.transition_to(AgentState.EXECUTING)
        assert mgr.history[0].timestamp <= mgr.history[1].timestamp


class TestForceTransition:
    def test_force_transition_skips_validation(self):
        mgr = AgentStateManager()
        # IDLE -> EXECUTING is normally invalid
        mgr.force_transition(AgentState.EXECUTING, reason="test")
        assert mgr.current_state == AgentState.EXECUTING

    def test_force_transition_recorded_as_forced(self):
        mgr = AgentStateManager()
        mgr.force_transition(AgentState.EXECUTING, reason="test")
        assert "FORCED" in mgr.history[-1].reason

    def test_force_transition_without_reason(self):
        mgr = AgentStateManager()
        mgr.force_transition(AgentState.COMPLETE)
        assert "FORCED" in mgr.history[-1].reason


class TestPredicates:
    def test_is_terminal_complete(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.COMPLETE)
        assert mgr.is_terminal() is True

    def test_is_terminal_error(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.ERROR)
        assert mgr.is_terminal() is True

    def test_is_not_terminal_idle(self):
        mgr = AgentStateManager()
        assert mgr.is_terminal() is False

    def test_is_not_terminal_thinking(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert mgr.is_terminal() is False

    def test_is_active_thinking(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        assert mgr.is_active() is True

    def test_is_active_executing(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.EXECUTING)
        assert mgr.is_active() is True

    def test_is_not_active_idle(self):
        mgr = AgentStateManager()
        assert mgr.is_active() is False

    def test_is_not_active_complete(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.COMPLETE)
        assert mgr.is_active() is False


class TestReset:
    def test_reset_returns_to_idle(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.transition_to(AgentState.COMPLETE)
        mgr.reset()
        assert mgr.current_state == AgentState.IDLE

    def test_reset_clears_history(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        mgr.reset()
        assert mgr.history == []

    def test_reset_clears_metadata(self):
        mgr = AgentStateManager()
        mgr.metadata["key"] = "value"
        mgr.reset()
        assert mgr.metadata == {}


class TestStateDuration:
    def test_duration_zero_with_no_history(self):
        mgr = AgentStateManager()
        assert mgr.get_state_duration() == 0.0

    def test_duration_increases_over_time(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        time.sleep(0.05)
        assert mgr.get_state_duration() >= 0.04

    def test_duration_resets_after_transition(self):
        mgr = AgentStateManager()
        mgr.transition_to(AgentState.THINKING)
        time.sleep(0.05)
        mgr.transition_to(AgentState.EXECUTING)
        assert mgr.get_state_duration() < 0.05
