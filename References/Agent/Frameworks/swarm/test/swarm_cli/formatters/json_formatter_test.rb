# frozen_string_literal: true

require "test_helper"
require "swarm_cli"

class JsonFormatterTest < Minitest::Test
  def setup
    @output = StringIO.new
    @formatter = SwarmCLI::Formatters::JsonFormatter.new(output: @output)
  end

  def test_on_start_does_not_emit
    # on_start should not emit because SDK emits swarm_start automatically
    @formatter.on_start(
      config_path: "config.yml",
      swarm_name: "Test Swarm",
      lead_agent: :lead,
      prompt: "Test prompt",
    )

    assert_empty(@output.string)
  end

  def test_on_log_emits_json_line
    entry = {
      type: "user_prompt",
      agent: :lead,
      timestamp: Time.now.to_s,
      content: "test",
    }

    @formatter.on_log(entry)

    output = @output.string

    refute_empty(output)
    parsed = JSON.parse(output.strip)

    assert_equal("user_prompt", parsed["type"])
    assert_equal("lead", parsed["agent"])
  end

  def test_on_log_calls_flush
    entry = { type: "test", data: "value" }

    # Call on_log
    @formatter.on_log(entry)

    # Verify output was written (flush is called internally)
    refute_empty(@output.string)
  end

  def test_on_log_emits_multiple_entries
    entry1 = { type: "agent_step", agent: :agent1 }
    entry2 = { type: "tool_call", agent: :agent1, tool: "Read" }

    @formatter.on_log(entry1)
    @formatter.on_log(entry2)

    lines = @output.string.split("\n")

    assert_equal(2, lines.size)

    parsed1 = JSON.parse(lines[0])
    parsed2 = JSON.parse(lines[1])

    assert_equal("agent_step", parsed1["type"])
    assert_equal("tool_call", parsed2["type"])
  end

  def test_on_success_does_not_emit
    # on_success should not emit because SDK emits swarm_stop automatically
    result = Minitest::Mock.new
    result.expect(:content, "result content")
    result.expect(:agent, :lead)

    @formatter.on_success(result: result)

    assert_empty(@output.string)
  end

  def test_on_error_emits_structured_json
    # on_error emits error events in JSON format for automation
    # This handles errors that occur before or outside swarm execution
    error = StandardError.new("test error")

    @formatter.on_error(error: error)

    output = @output.string

    refute_empty(output)

    # Parse JSON to verify structure
    parsed = JSON.parse(output.strip)

    assert_equal("error", parsed["type"])
    assert_equal("StandardError", parsed["error_class"])
    assert_equal("test error", parsed["error_message"])
    assert(parsed.key?("timestamp"))
  end

  def test_on_error_with_duration_includes_duration
    error = StandardError.new("test error")

    @formatter.on_error(error: error, duration: 1.5)

    output = @output.string

    refute_empty(output)

    parsed = JSON.parse(output.strip)

    assert_equal("error", parsed["type"])
    assert_in_delta(1.5, parsed["duration"])
  end

  def test_emit_uses_to_json
    entry = {
      type: "custom",
      data: { nested: "value" },
      array: [1, 2, 3],
    }

    @formatter.on_log(entry)

    parsed = JSON.parse(@output.string.strip)

    assert_equal("custom", parsed["type"])
    assert_equal({ "nested" => "value" }, parsed["data"])
    assert_equal([1, 2, 3], parsed["array"])
  end
end
