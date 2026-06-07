# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  # Tests to ensure events are not emitted multiple times
  #
  # This test suite guards against regression of the duplicate event bug where
  # agent_stop, agent_step, and other events were being emitted twice due to
  # setup_logging being called multiple times during agent initialization.
  class EventDeduplicationTest < Minitest::Test
    include LLMMockHelper

    def setup
      # Reset logging state before each test
      begin
        LogStream.reset!
      rescue StandardError
        nil
      end

      begin
        LogCollector.reset!
      rescue StandardError
        nil
      end

      # Set dummy API key for tests
      @original_api_key = ENV["OPENAI_API_KEY"]
      ENV["OPENAI_API_KEY"] = "test-key-12345"
      RubyLLM.configure do |config|
        config.openai_api_key = "test-key-12345"
      end
    end

    def teardown
      begin
        LogStream.reset!
      rescue StandardError
        nil
      end

      begin
        LogCollector.reset!
      rescue StandardError
        nil
      end

      WebMock.reset!
      ENV["OPENAI_API_KEY"] = @original_api_key
      RubyLLM.configure do |config|
        config.openai_api_key = @original_api_key
      end
    end

    # Test that agent_stop event is emitted exactly once per agent completion
    def test_agent_stop_event_not_duplicated
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
      ))

      swarm.lead = :test_agent

      # Mock LLM response (simple response, no tool calls)
      stub_llm_request(mock_llm_response(content: "Test response"))

      logs = []
      result = swarm.execute("test prompt") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Count agent_stop events
      agent_stop_events = logs.select { |log| log[:type] == "agent_stop" }

      assert_equal(
        1,
        agent_stop_events.size,
        "Expected exactly 1 agent_stop event, got #{agent_stop_events.size}. " \
          "This indicates the duplicate event bug has regressed.",
      )
    end

    # Test that agent_step event is emitted exactly once per LLM response with tool calls
    def test_agent_step_event_not_duplicated
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
        tools: [:Glob],
      ))

      swarm.lead = :test_agent

      # Mock LLM responses: first with tool call, then final response
      tool_call_response = mock_llm_response(
        content: nil,
        tool_calls: [{ name: "Glob", arguments: { pattern: "*.rb" } }],
      )
      final_response = mock_llm_response(content: "Found some files")

      stub_llm_sequence(tool_call_response, final_response)

      logs = []
      result = swarm.execute("find ruby files") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Count agent_step events
      agent_step_events = logs.select { |log| log[:type] == "agent_step" }

      assert_equal(
        1,
        agent_step_events.size,
        "Expected exactly 1 agent_step event, got #{agent_step_events.size}. " \
          "This indicates the duplicate event bug has regressed.",
      )
    end

    # Test that tool_call event is emitted exactly once per tool invocation
    def test_tool_call_event_not_duplicated
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
        tools: [:Glob],
      ))

      swarm.lead = :test_agent

      # Mock LLM responses: first with tool call, then final response
      tool_call_response = mock_llm_response(
        content: nil,
        tool_calls: [{ name: "Glob", arguments: { pattern: "*.rb" } }],
      )
      final_response = mock_llm_response(content: "Found some files")

      stub_llm_sequence(tool_call_response, final_response)

      logs = []
      result = swarm.execute("find ruby files") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Count tool_call events
      tool_call_events = logs.select { |log| log[:type] == "tool_call" }

      assert_equal(
        1,
        tool_call_events.size,
        "Expected exactly 1 tool_call event, got #{tool_call_events.size}. " \
          "This indicates duplicate tool_call events are being emitted.",
      )
    end

    # Test that tool_result event is emitted exactly once per tool completion
    def test_tool_result_event_not_duplicated
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
        tools: [:Glob],
      ))

      swarm.lead = :test_agent

      # Mock LLM responses: first with tool call, then final response
      tool_call_response = mock_llm_response(
        content: nil,
        tool_calls: [{ name: "Glob", arguments: { pattern: "*.rb" } }],
      )
      final_response = mock_llm_response(content: "Found some files")

      stub_llm_sequence(tool_call_response, final_response)

      logs = []
      result = swarm.execute("find ruby files") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Count tool_result events
      tool_result_events = logs.select { |log| log[:type] == "tool_result" }

      assert_equal(
        1,
        tool_result_events.size,
        "Expected exactly 1 tool_result event, got #{tool_result_events.size}. " \
          "This indicates duplicate tool_result events are being emitted.",
      )
    end

    # Test that user_prompt event is emitted exactly once per user message
    def test_user_prompt_event_not_duplicated
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
      ))

      swarm.lead = :test_agent

      stub_llm_request(mock_llm_response(content: "Test response"))

      logs = []
      result = swarm.execute("test prompt") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Count user_prompt events
      user_prompt_events = logs.select { |log| log[:type] == "user_prompt" }

      assert_equal(
        1,
        user_prompt_events.size,
        "Expected exactly 1 user_prompt event, got #{user_prompt_events.size}. " \
          "This indicates duplicate user_prompt events are being emitted.",
      )
    end

    # Test swarm_start and swarm_stop events are not duplicated
    def test_swarm_lifecycle_events_not_duplicated
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
      ))

      swarm.lead = :test_agent

      stub_llm_request(mock_llm_response(content: "Test response"))

      logs = []
      result = swarm.execute("test prompt") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Count swarm lifecycle events
      swarm_start_events = logs.select { |log| log[:type] == "swarm_start" }
      swarm_stop_events = logs.select { |log| log[:type] == "swarm_stop" }

      assert_equal(
        1,
        swarm_start_events.size,
        "Expected exactly 1 swarm_start event, got #{swarm_start_events.size}",
      )

      assert_equal(
        1,
        swarm_stop_events.size,
        "Expected exactly 1 swarm_stop event, got #{swarm_stop_events.size}",
      )
    end

    # Test that multiple tool calls in one response don't cause duplicate agent_step events
    def test_multiple_tool_calls_single_agent_step
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
        tools: [:Glob, :Grep],
      ))

      swarm.lead = :test_agent

      # Mock LLM response with multiple tool calls in one response
      tool_call_response = mock_llm_response(
        content: nil,
        tool_calls: [
          { name: "Glob", arguments: { pattern: "*.rb" } },
          { name: "Grep", arguments: { pattern: "def test" } },
        ],
      )
      final_response = mock_llm_response(content: "Found some files and matches")

      stub_llm_sequence(tool_call_response, final_response)

      logs = []
      result = swarm.execute("find ruby files with test methods") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Should have exactly 1 agent_step event even with multiple tool calls
      agent_step_events = logs.select { |log| log[:type] == "agent_step" }

      assert_equal(
        1,
        agent_step_events.size,
        "Expected exactly 1 agent_step event for multiple tool calls, got #{agent_step_events.size}",
      )

      # Should have 2 tool_call events (one per tool)
      tool_call_events = logs.select { |log| log[:type] == "tool_call" }

      assert_equal(
        2,
        tool_call_events.size,
        "Expected exactly 2 tool_call events, got #{tool_call_events.size}",
      )
    end

    # Test that setup_logging is idempotent (calling it multiple times doesn't register duplicate callbacks)
    def test_setup_logging_idempotency
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
      ))

      swarm.lead = :test_agent

      stub_llm_request(mock_llm_response(content: "Test response"))

      # Execute once to initialize agents
      logs1 = []
      swarm.execute("first prompt") do |log_entry|
        logs1 << log_entry
      end

      WebMock.reset!
      stub_llm_request(mock_llm_response(content: "Test response 2"))

      # Execute again - should not register duplicate callbacks
      logs2 = []
      swarm.execute("second prompt") do |log_entry|
        logs2 << log_entry
      end

      # Count agent_stop events in second execution
      agent_stop_events = logs2.select { |log| log[:type] == "agent_stop" }

      assert_equal(
        1,
        agent_stop_events.size,
        "Expected exactly 1 agent_stop event in second execution, got #{agent_stop_events.size}. " \
          "This indicates setup_logging is not idempotent.",
      )
    end

    # Test that all event types in a typical execution have correct counts
    def test_comprehensive_event_counts_simple_response
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
      ))

      swarm.lead = :test_agent

      stub_llm_request(mock_llm_response(content: "Test response"))

      logs = []
      result = swarm.execute("test prompt") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Build event count map
      event_counts = logs.group_by { |log| log[:type] }.transform_values(&:count)

      # Verify expected event counts for a simple (no tool calls) execution
      expected_counts = {
        "swarm_start" => 1,
        "agent_start" => 1,
        "user_prompt" => 1,
        "llm_api_request" => 1,
        "llm_api_response" => 1,
        "agent_stop" => 1,
        "swarm_stop" => 1,
      }

      expected_counts.each do |event_type, expected_count|
        actual_count = event_counts[event_type] || 0

        assert_equal(
          expected_count,
          actual_count,
          "Expected #{expected_count} '#{event_type}' events, got #{actual_count}",
        )
      end
    end

    # Test that all event types in a tool-calling execution have correct counts
    def test_comprehensive_event_counts_with_tool_call
      swarm = Swarm.new(name: "Test Swarm", scratchpad: Tools::Stores::ScratchpadStorage.new)

      swarm.add_agent(create_agent(
        name: :test_agent,
        description: "Test agent",
        model: "gpt-5",
        system_prompt: "You are a test agent",
        directory: ".",
        tools: [:Glob],
      ))

      swarm.lead = :test_agent

      # Mock LLM responses: first with tool call, then final response
      tool_call_response = mock_llm_response(
        content: nil,
        tool_calls: [{ name: "Glob", arguments: { pattern: "*.rb" } }],
      )
      final_response = mock_llm_response(content: "Found some files")

      stub_llm_sequence(tool_call_response, final_response)

      logs = []
      result = swarm.execute("find ruby files") do |log_entry|
        logs << log_entry
      end

      assert_predicate(result, :success?)

      # Build event count map
      event_counts = logs.group_by { |log| log[:type] }.transform_values(&:count)

      # Verify expected event counts for a tool-calling execution
      expected_counts = {
        "swarm_start" => 1,
        "agent_start" => 1,
        "user_prompt" => 1,
        "llm_api_request" => 2,  # One for tool call, one for final response
        "llm_api_response" => 2, # One for tool call, one for final response
        "agent_step" => 1,       # One for the tool call response
        "tool_call" => 1,        # One tool was called
        "tool_result" => 1,      # One tool result
        "agent_stop" => 1,       # Final response
        "swarm_stop" => 1,
      }

      expected_counts.each do |event_type, expected_count|
        actual_count = event_counts[event_type] || 0

        assert_equal(
          expected_count,
          actual_count,
          "Expected #{expected_count} '#{event_type}' events, got #{actual_count}",
        )
      end
    end

    private

    def create_agent(name:, **config)
      config[:description] ||= "Test agent #{name}"
      config[:model] ||= "gpt-5"
      config[:system_prompt] ||= "Test"
      config[:directory] ||= "."

      Agent::Definition.new(name, config)
    end
  end
end
