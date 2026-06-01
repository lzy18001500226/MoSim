# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class TranscriptBuilderTest < Minitest::Test
    def test_build_empty_logs
      transcript = TranscriptBuilder.build([])

      assert_equal("", transcript)
    end

    def test_build_user_prompt
      logs = [
        { type: "user_prompt", agent: :assistant, prompt: "Help me with CORS" },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_equal("USER: Help me with CORS", transcript)
    end

    def test_build_agent_stop
      logs = [
        { type: "agent_stop", agent: :assistant, content: "Here's how to fix CORS..." },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_equal("AGENT [assistant]: Here's how to fix CORS...", transcript)
    end

    def test_build_full_conversation
      logs = [
        { type: "user_prompt", agent: :assistant, prompt: "Help me debug this" },
        { type: "tool_call", agent: :assistant, tool: "Read", arguments: { path: "file.rb" } },
        { type: "tool_result", agent: :assistant, tool: "Read", result: "def hello\n  puts 'hi'\nend" },
        { type: "agent_stop", agent: :assistant, content: "The issue is in the hello method." },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_includes(transcript, "USER: Help me debug this")
      assert_includes(transcript, "TOOL [assistant] → Read(")
      assert_includes(transcript, "RESULT [Read]: def hello")
      assert_includes(transcript, "AGENT [assistant]: The issue is in the hello method.")
    end

    def test_build_excludes_thinking_by_default
      logs = [
        { type: "user_prompt", agent: :assistant, prompt: "Question" },
        { type: "agent_step", agent: :assistant, content: "Let me think about this..." },
        { type: "agent_stop", agent: :assistant, content: "Here's my answer." },
      ]

      transcript = TranscriptBuilder.build(logs)

      refute_includes(transcript, "thinking")
      refute_includes(transcript, "Let me think")
      assert_includes(transcript, "USER: Question")
      assert_includes(transcript, "AGENT [assistant]: Here's my answer.")
    end

    def test_build_includes_thinking_when_requested
      logs = [
        { type: "user_prompt", agent: :assistant, prompt: "Question" },
        { type: "agent_step", agent: :assistant, content: "Let me think about this..." },
        { type: "agent_stop", agent: :assistant, content: "Here's my answer." },
      ]

      transcript = TranscriptBuilder.build(logs, include_thinking: true)

      assert_includes(transcript, "AGENT [assistant] (thinking): Let me think about this...")
      assert_includes(transcript, "AGENT [assistant]: Here's my answer.")
    end

    def test_build_excludes_tool_results_when_requested
      logs = [
        { type: "tool_call", agent: :assistant, tool: "Read", arguments: { path: "file.rb" } },
        { type: "tool_result", agent: :assistant, tool: "Read", result: "file content here" },
      ]

      transcript = TranscriptBuilder.build(logs, include_tool_results: false)

      assert_includes(transcript, "TOOL [assistant] → Read(")
      refute_includes(transcript, "RESULT")
      refute_includes(transcript, "file content here")
    end

    def test_build_filters_by_single_agent
      logs = [
        { type: "user_prompt", agent: :assistant, prompt: "Question" },
        { type: "agent_stop", agent: :assistant, content: "Delegating to backend" },
        { type: "user_prompt", agent: :backend, prompt: "Task from assistant" },
        { type: "tool_call", agent: :backend, tool: "Bash", arguments: { command: "ls" } },
        { type: "agent_stop", agent: :backend, content: "Done" },
      ]

      transcript = TranscriptBuilder.build(logs, agents: [:backend])

      refute_includes(transcript, "Question")
      refute_includes(transcript, "Delegating")
      assert_includes(transcript, "Task from assistant")
      assert_includes(transcript, "TOOL [backend]")
      assert_includes(transcript, "AGENT [backend]: Done")
    end

    def test_build_filters_by_multiple_agents
      logs = [
        { type: "agent_stop", agent: :lead, content: "Lead response" },
        { type: "agent_stop", agent: :backend, content: "Backend response" },
        { type: "agent_stop", agent: :frontend, content: "Frontend response" },
        { type: "agent_stop", agent: :database, content: "Database response" },
      ]

      transcript = TranscriptBuilder.build(logs, agents: [:backend, :frontend])

      refute_includes(transcript, "Lead response")
      assert_includes(transcript, "Backend response")
      assert_includes(transcript, "Frontend response")
      refute_includes(transcript, "Database response")
    end

    def test_build_truncates_long_tool_results
      long_content = "x" * 1000
      logs = [
        { type: "tool_result", agent: :assistant, tool: "Read", result: long_content },
      ]

      transcript = TranscriptBuilder.build(logs, max_result_length: 100)

      assert_includes(transcript, "x" * 100)
      assert_includes(transcript, "...")
      refute_includes(transcript, "x" * 101)
    end

    def test_build_truncates_long_tool_arguments
      long_path = "/very/long/path/" + ("x" * 500)
      logs = [
        { type: "tool_call", agent: :assistant, tool: "Read", arguments: { path: long_path } },
      ]

      transcript = TranscriptBuilder.build(logs, max_args_length: 50)

      # Arguments should be truncated
      assert_operator(transcript.length, :<, 500)
      assert_includes(transcript, "...")
    end

    def test_build_handles_delegation_events
      logs = [
        { type: "pre_delegation", agent: :lead, to_agent: :backend, task: "Do something" },
        { type: "post_delegation", agent: :lead, to_agent: :backend },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_includes(transcript, "DELEGATE: lead → backend: Do something")
      assert_includes(transcript, "DELEGATE COMPLETE: backend → lead")
    end

    def test_build_handles_string_keys
      logs = [
        { "type" => "user_prompt", "agent" => "assistant", "prompt" => "Hello" },
        { "type" => "agent_stop", "agent" => "assistant", "content" => "Hi there!" },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_includes(transcript, "USER: Hello")
      assert_includes(transcript, "AGENT [assistant]: Hi there!")
    end

    def test_build_handles_nil_content
      logs = [
        { type: "agent_stop", agent: :assistant, content: nil },
        { type: "user_prompt", agent: :assistant, prompt: nil },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_equal("", transcript)
    end

    def test_build_handles_empty_content
      logs = [
        { type: "agent_stop", agent: :assistant, content: "" },
        { type: "agent_stop", agent: :assistant, content: "   " },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_equal("", transcript)
    end

    def test_build_shows_failed_tool_results
      logs = [
        { type: "tool_result", agent: :assistant, tool: "Bash", result: "command failed", success: false },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_includes(transcript, "[FAILED]")
      assert_includes(transcript, "command failed")
    end

    def test_build_delegation_source
      logs = [
        { type: "user_prompt", agent: :backend, prompt: "Task from lead", source: "delegation" },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_includes(transcript, "DELEGATION REQUEST → [backend]: Task from lead")
    end

    def test_result_transcript_method
      logs = [
        { type: "user_prompt", agent: :assistant, prompt: "Help me" },
        { type: "agent_stop", agent: :assistant, content: "Here's help" },
      ]
      result = Result.new(agent: "test", logs: logs)

      transcript = result.transcript

      assert_includes(transcript, "USER: Help me")
      assert_includes(transcript, "AGENT [assistant]: Here's help")
    end

    def test_result_transcript_with_agent_filter
      logs = [
        { type: "agent_stop", agent: :backend, content: "Backend" },
        { type: "agent_stop", agent: :frontend, content: "Frontend" },
      ]
      result = Result.new(agent: "test", logs: logs)

      transcript = result.transcript(:backend)

      assert_includes(transcript, "Backend")
      refute_includes(transcript, "Frontend")
    end

    def test_result_transcript_with_multiple_agent_filter
      logs = [
        { type: "agent_stop", agent: :backend, content: "Backend" },
        { type: "agent_stop", agent: :frontend, content: "Frontend" },
        { type: "agent_stop", agent: :database, content: "Database" },
      ]
      result = Result.new(agent: "test", logs: logs)

      transcript = result.transcript(:backend, :frontend)

      assert_includes(transcript, "Backend")
      assert_includes(transcript, "Frontend")
      refute_includes(transcript, "Database")
    end

    def test_result_transcript_with_options
      logs = [
        { type: "agent_step", agent: :assistant, content: "Thinking..." },
        { type: "agent_stop", agent: :assistant, content: "Done" },
      ]
      result = Result.new(agent: "test", logs: logs)

      transcript = result.transcript(include_thinking: true)

      assert_includes(transcript, "Thinking...")
    end

    def test_events_are_joined_with_double_newlines
      logs = [
        { type: "user_prompt", agent: :assistant, prompt: "First" },
        { type: "agent_stop", agent: :assistant, content: "Second" },
      ]

      transcript = TranscriptBuilder.build(logs)

      assert_includes(transcript, "USER: First\n\nAGENT [assistant]: Second")
    end
  end
end
