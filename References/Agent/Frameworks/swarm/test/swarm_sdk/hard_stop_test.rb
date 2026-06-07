# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class HardStopTest < Minitest::Test
    def setup
      cleanup_logging_state

      @original_api_key = ENV["OPENAI_API_KEY"]
      ENV["OPENAI_API_KEY"] = "test-key-12345"
      SwarmSDK.reset_config!
      RubyLLM.configure do |config|
        config.openai_api_key = "test-key-12345"
      end

      @scratchpad = create_test_scratchpad
    end

    def teardown
      cleanup_logging_state
      WebMock.reset!
      ENV["OPENAI_API_KEY"] = @original_api_key
      SwarmSDK.reset_config!
    end

    # --- Swarm#stop / stop_requested? ---

    def test_stop_requested_false_initially
      swarm = build_test_swarm

      refute_predicate(swarm, :stop_requested?)
    end

    def test_stop_sets_flag
      swarm = build_test_swarm
      swarm.stop

      assert_predicate(swarm, :stop_requested?)
    end

    def test_stop_is_idempotent
      swarm = build_test_swarm
      swarm.stop
      swarm.stop # Second call is a no-op

      assert_predicate(swarm, :stop_requested?)
    end

    def test_stop_when_no_execution_running_is_noop
      swarm = build_test_swarm
      # No execution in progress, no pipe - should not raise
      swarm.stop

      assert_predicate(swarm, :stop_requested?)
    end

    # --- Result#interrupted? and Result#finish_reason ---

    def test_result_interrupted_false_on_normal_completion
      swarm = build_test_swarm
      stub_llm_request(mock_llm_response(content: "Done"))

      result = swarm.execute("Hello") { |_| }

      refute_predicate(result, :interrupted?)
      assert_equal("finished", result.finish_reason)
    end

    def test_result_interrupted_true_when_stopped
      result = Result.new(
        content: nil,
        agent: "test",
        error: InterruptedError.new("Swarm execution was interrupted"),
        metadata: { interrupted: true, finish_reason: "interrupted" },
      )

      assert_predicate(result, :interrupted?)
      assert_equal("interrupted", result.finish_reason)
    end

    def test_result_finish_reason_error_on_failure
      result = Result.new(
        content: nil,
        agent: "test",
        error: StandardError.new("boom"),
      )

      assert_equal("error", result.finish_reason)
      refute_predicate(result, :interrupted?)
    end

    def test_result_finish_reason_from_metadata_takes_precedence
      result = Result.new(
        content: "done",
        agent: "test",
        metadata: { finish_reason: "custom_reason" },
      )

      assert_equal("custom_reason", result.finish_reason)
    end

    # --- Stop from event callback ---

    def test_stop_from_event_callback
      swarm = build_test_swarm

      # First response triggers tool call, second responds after tool
      tool_calls = [{ name: "Read", arguments: { file_path: "/tmp/test.txt" } }]
      stub_llm_sequence(
        mock_llm_response(content: nil, tool_calls: tool_calls),
        mock_llm_response(content: "Final response"),
      )

      events = []
      result = swarm.execute("Read a file") do |event|
        events << event
        # Stop when we see the tool_call event
        swarm.stop if event[:type] == "tool_call"
      end

      # Result should be interrupted
      assert_predicate(result, :interrupted?)
      assert_equal("interrupted", result.finish_reason)
      assert_kind_of(InterruptedError, result.error)
    end

    # --- swarm_stop event includes finish_reason ---

    def test_swarm_stop_event_has_finish_reason_on_normal_completion
      swarm = build_test_swarm
      stub_llm_request(mock_llm_response(content: "Done"))

      events = []
      swarm.execute("Hello") { |event| events << event }

      swarm_stop_event = events.find { |e| e[:type] == "swarm_stop" }

      assert_equal("finished", swarm_stop_event[:finish_reason])
    end

    def test_swarm_stop_event_has_finish_reason_interrupted
      swarm = build_test_swarm

      # Use a tool call so stop happens mid-execution
      tool_calls = [{ name: "Read", arguments: { file_path: "/tmp/test.txt" } }]
      stub_llm_sequence(
        mock_llm_response(content: nil, tool_calls: tool_calls),
        mock_llm_response(content: "Done"),
      )

      events = []
      swarm.execute("Read a file") do |event|
        events << event
        swarm.stop if event[:type] == "tool_call"
      end

      swarm_stop_event = events.find { |e| e[:type] == "swarm_stop" }

      assert_equal("interrupted", swarm_stop_event[:finish_reason])
    end

    # --- agent_stop events for interrupted agents ---

    def test_interrupted_result_has_swarm_stop_event
      # When stop is called from event callback, the cooperative check
      # fires between loop iterations. The swarm_stop event should have
      # finish_reason: "interrupted" regardless of whether agents were active.
      swarm = build_test_swarm

      tool_calls = [{ name: "Read", arguments: { file_path: "/tmp/test.txt" } }]
      stub_llm_sequence(
        mock_llm_response(content: nil, tool_calls: tool_calls),
        mock_llm_response(content: "Done"),
      )

      events = []
      result = swarm.execute("Read a file") do |event|
        events << event
        swarm.stop if event[:type] == "tool_call"
      end

      # The result should be interrupted
      assert_predicate(result, :interrupted?)

      # The swarm_stop event should reflect interruption
      swarm_stop_event = events.find { |e| e[:type] == "swarm_stop" }

      assert_equal("interrupted", swarm_stop_event[:finish_reason])
    end

    # --- Re-execution after stop ---

    def test_re_execution_after_stop_works
      swarm = build_test_swarm

      # First execution - stop it
      tool_calls = [{ name: "Read", arguments: { file_path: "/tmp/test.txt" } }]
      stub_llm_sequence(
        mock_llm_response(content: nil, tool_calls: tool_calls),
        mock_llm_response(content: "Done"),
      )

      result1 = swarm.execute("Read a file") do |event|
        swarm.stop if event[:type] == "tool_call"
      end

      assert_predicate(result1, :interrupted?)

      # Second execution - should work normally
      stub_llm_request(mock_llm_response(content: "Second response"))

      result2 = swarm.execute("Hello again") { |_| }

      assert_predicate(result2, :success?)
      refute_predicate(result2, :interrupted?)
      assert_equal("finished", result2.finish_reason)
      assert_equal("Second response", result2.content)
    end

    # --- Observer stop on interruption ---

    def test_observer_manager_stop
      manager = Observer::Manager.new(build_test_swarm)
      # Should not raise even without setup
      manager.stop
    end

    # --- InterruptedError ---

    def test_interrupted_error_class_hierarchy
      error = InterruptedError.new("test")

      assert_kind_of(Error, error)
      assert_kind_of(StandardError, error)
    end

    # --- Swarm prepare/cleanup lifecycle ---

    def test_prepare_for_execution_resets_stop_flag
      swarm = build_test_swarm
      swarm.stop

      assert_predicate(swarm, :stop_requested?)

      swarm.prepare_for_execution

      refute_predicate(swarm, :stop_requested?)
    ensure
      swarm&.cleanup_stop_signal
    end

    def test_prepare_creates_and_cleanup_closes_pipe
      swarm = build_test_swarm

      swarm.prepare_for_execution

      refute_nil(swarm.stop_signal_read)
      refute_predicate(swarm.stop_signal_read, :closed?)

      swarm.cleanup_stop_signal

      assert_nil(swarm.stop_signal_read)
    end

    # --- Active agent tracking ---

    def test_mark_agent_active_and_inactive
      swarm = build_test_swarm
      chat = Object.new

      swarm.mark_agent_active(:test_agent, chat)

      assert_equal({ test_agent: chat }, swarm.active_agent_chats)

      swarm.mark_agent_inactive(:test_agent)

      assert_empty(swarm.active_agent_chats)
    end

    def test_active_agent_chats_returns_copy
      swarm = build_test_swarm
      chat = Object.new
      swarm.mark_agent_active(:test, chat)

      copy = swarm.active_agent_chats
      copy.delete(:test)

      # Original should still have the entry
      refute_empty(swarm.active_agent_chats)
    end

    # --- finish_reason in hook_triggers ---

    def test_swarm_stop_event_has_finish_reason_error_on_failure
      swarm = build_test_swarm

      # Simulate an error by stubbing with network error
      stub_llm_network_error

      events = []
      result = swarm.execute("Hello") { |event| events << event }

      assert_predicate(result, :failure?)
      swarm_stop_event = events.find { |e| e[:type] == "swarm_stop" }

      assert_equal("error", swarm_stop_event[:finish_reason])
    end

    # --- Non-blocking stop ---

    def test_stop_with_async_execution
      swarm = build_test_swarm

      # Mock a response that includes tool calls (so there's time to stop)
      tool_calls = [{ name: "Read", arguments: { file_path: "/tmp/test.txt" } }]
      stub_llm_sequence(
        mock_llm_response(content: nil, tool_calls: tool_calls),
        mock_llm_response(content: "Done"),
      )

      result = nil
      Sync do
        task = swarm.execute("Read a file", wait: false) do |event|
          swarm.stop if event[:type] == "tool_call"
        end
        result = task.wait
      end

      assert_predicate(result, :interrupted?)
      assert_equal("interrupted", result.finish_reason)
    end

    private

    def build_test_swarm
      swarm = Swarm.new(
        name: "Stop Test Swarm",
        scratchpad: @scratchpad,
        execution_timeout: nil,
      )

      swarm.add_agent(create_agent(
        name: :main,
        description: "Main test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
        tools: [:Read],
      ))

      swarm.lead = :main
      swarm
    end
  end
end
