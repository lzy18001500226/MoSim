# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class NodeContextExtraTest < Minitest::Test
    # Test all branches in content() method
    def test_content_returns_result_content_for_output_context
      result = Result.new(content: "output content", agent: :test_agent, duration: 1.0)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_equal("output content", ctx.content)
    end

    def test_content_returns_transformed_content_for_input_context
      ctx = NodeContext.for_input(
        previous_result: nil,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
        transformed_content: "transformed",
      )

      assert_equal("transformed", ctx.content)
    end

    def test_content_returns_previous_result_content_when_respond_to_content
      previous = Result.new(content: "previous content", agent: :prev, duration: 1.0)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal("previous content", ctx.content)
    end

    def test_content_returns_nil_for_hash_previous_result
      ctx = NodeContext.for_input(
        previous_result: { a: "one", b: "two" },
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [:a, :b],
      )

      assert_nil(ctx.content)
    end

    def test_content_returns_to_s_for_string_previous_result
      ctx = NodeContext.for_input(
        previous_result: "string content",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal("string content", ctx.content)
    end

    def test_content_returns_to_s_for_other_types
      ctx = NodeContext.for_input(
        previous_result: 12345,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal("12345", ctx.content)
    end

    # Test all branches in agent() method
    def test_agent_returns_result_agent_for_output_context
      result = Result.new(content: "test", agent: :output_agent, duration: 1.0)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_equal(:output_agent, ctx.agent)
    end

    def test_agent_returns_previous_agent_when_respond_to_agent
      previous = Result.new(content: "test", agent: :previous_agent, duration: 1.0)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal(:previous_agent, ctx.agent)
    end

    def test_agent_returns_nil_for_non_result_previous
      ctx = NodeContext.for_input(
        previous_result: "string",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_nil(ctx.agent)
    end

    # Test all branches in logs() method
    def test_logs_returns_result_logs_for_output_context
      logs = [{ type: "test", message: "log entry" }]
      result = Result.new(content: "test", agent: :agent, duration: 1.0, logs: logs)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_equal(logs, ctx.logs)
    end

    def test_logs_returns_previous_logs_when_respond_to_logs
      logs = [{ type: "prev", message: "previous log" }]
      previous = Result.new(content: "test", agent: :agent, duration: 1.0, logs: logs)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal(logs, ctx.logs)
    end

    def test_logs_returns_nil_for_non_result_previous
      ctx = NodeContext.for_input(
        previous_result: "string",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_nil(ctx.logs)
    end

    # Test all branches in duration() method
    def test_duration_returns_result_duration_for_output_context
      result = Result.new(content: "test", agent: :agent, duration: 5.5)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_in_delta(5.5, ctx.duration)
    end

    def test_duration_returns_previous_duration_when_respond_to_duration
      previous = Result.new(content: "test", agent: :agent, duration: 3.3)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_in_delta(3.3, ctx.duration)
    end

    def test_duration_returns_nil_for_non_result_previous
      ctx = NodeContext.for_input(
        previous_result: "string",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_nil(ctx.duration)
    end

    # Test all branches in error() method
    def test_error_returns_result_error_for_output_context
      err = StandardError.new("test error")
      result = Result.new(content: nil, agent: :agent, duration: 1.0, error: err)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_equal(err, ctx.error)
    end

    def test_error_returns_previous_error_when_respond_to_error
      err = RuntimeError.new("previous error")
      previous = Result.new(content: nil, agent: :agent, duration: 1.0, error: err)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal(err, ctx.error)
    end

    def test_error_returns_nil_for_non_result_previous
      ctx = NodeContext.for_input(
        previous_result: "string",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_nil(ctx.error)
    end

    # Test all branches in success?() method
    def test_success_returns_result_success_for_output_context
      result = Result.new(content: "test", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_predicate(ctx, :success?)
    end

    def test_success_returns_false_for_result_with_error
      err = StandardError.new("error")
      result = Result.new(content: nil, agent: :agent, duration: 1.0, error: err)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      refute_predicate(ctx, :success?)
    end

    def test_success_returns_previous_success_when_respond_to_success
      previous = Result.new(content: "test", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_predicate(ctx, :success?)
    end

    def test_success_returns_nil_for_non_result_previous
      ctx = NodeContext.for_input(
        previous_result: "string",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_nil(ctx.success?)
    end

    # Test skip_execution control flow
    def test_skip_execution_returns_control_hash_with_content
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      result = ctx.skip_execution(content: "cached content")

      assert_equal({ skip_execution: true, content: "cached content" }, result)
    end

    def test_skip_execution_raises_error_when_content_is_nil
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test_node,
        dependencies: [],
      )

      error = assert_raises(ArgumentError) do
        ctx.skip_execution(content: nil)
      end

      assert_match(/skip_execution requires content/, error.message)
      assert_match(/got nil/, error.message)
      assert_match(/test_node/, error.message)
    end

    # Test halt_workflow control flow
    def test_halt_workflow_returns_control_hash_with_content
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      result = ctx.halt_workflow(content: "final content")

      assert_equal({ halt_workflow: true, content: "final content" }, result)
    end

    def test_halt_workflow_raises_error_when_content_is_nil
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :halt_node,
        dependencies: [],
      )

      error = assert_raises(ArgumentError) do
        ctx.halt_workflow(content: nil)
      end

      assert_match(/halt_workflow requires content/, error.message)
      assert_match(/got nil/, error.message)
      assert_match(/halt_node/, error.message)
    end

    # Test goto_node control flow
    def test_goto_node_returns_control_hash_with_content_and_target
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :source,
        dependencies: [],
      )

      result = ctx.goto_node(:target, content: "jump content")

      assert_equal({ goto_node: :target, content: "jump content" }, result)
    end

    def test_goto_node_converts_string_to_symbol
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :source,
        dependencies: [],
      )

      result = ctx.goto_node("target_node", content: "jump content")

      assert_equal({ goto_node: :target_node, content: "jump content" }, result)
    end

    def test_goto_node_raises_error_when_content_is_nil
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :goto_source,
        dependencies: [],
      )

      error = assert_raises(ArgumentError) do
        ctx.goto_node(:target, content: nil)
      end

      assert_match(/goto_node requires content/, error.message)
      assert_match(/got nil/, error.message)
      assert_match(/goto_source/, error.message)
      assert_match(/Target: target/, error.message)
    end

    # Test attribute readers
    def test_original_prompt_reader
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "test prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal("test prompt", ctx.original_prompt)
    end

    def test_all_results_reader
      results = { node1: Result.new(content: "test", agent: :agent, duration: 1.0) }
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: results,
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal(results, ctx.all_results)
    end

    def test_node_name_reader
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :my_node,
        dependencies: [],
      )

      assert_equal(:my_node, ctx.node_name)
    end

    def test_dependencies_reader
      deps = [:dep1, :dep2]
      ctx = NodeContext.for_input(
        previous_result: "test",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: deps,
      )

      assert_equal(deps, ctx.dependencies)
    end

    def test_previous_result_reader
      previous = Result.new(content: "test", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
      )

      assert_equal(previous, ctx.previous_result)
    end

    def test_result_reader
      result = Result.new(content: "test", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_equal(result, ctx.result)
    end

    # Test factory methods create correct contexts
    def test_for_input_creates_input_context
      ctx = NodeContext.for_input(
        previous_result: "prev",
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [:dep],
      )

      assert_equal("prev", ctx.previous_result)
      assert_nil(ctx.result)
      assert_equal([:dep], ctx.dependencies)
    end

    def test_for_output_creates_output_context
      result = Result.new(content: "test", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_equal(result, ctx.result)
      assert_nil(ctx.previous_result)
      assert_empty(ctx.dependencies)
    end

    # Test control flow with output context
    def test_halt_workflow_works_from_output_context
      result = Result.new(content: "result", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      control = ctx.halt_workflow(content: "halt content")

      assert_equal({ halt_workflow: true, content: "halt content" }, control)
    end

    def test_goto_node_works_from_output_context
      result = Result.new(content: "result", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      control = ctx.goto_node(:target, content: "goto content")

      assert_equal({ goto_node: :target, content: "goto content" }, control)
    end

    # Test with empty logs and metadata
    def test_logs_returns_empty_array_for_result_with_no_logs
      result = Result.new(content: "test", agent: :agent, duration: 1.0, logs: [])
      ctx = NodeContext.for_output(
        result: result,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
      )

      assert_empty(ctx.logs)
    end

    # Test edge cases with transformed_content
    def test_content_prefers_transformed_content_over_previous_result_content
      previous = Result.new(content: "original", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
        transformed_content: "transformed",
      )

      # Should return transformed content, not original
      assert_equal("transformed", ctx.content)
    end

    def test_content_uses_previous_result_when_no_transformed_content
      previous = Result.new(content: "original", agent: :agent, duration: 1.0)
      ctx = NodeContext.for_input(
        previous_result: previous,
        all_results: {},
        original_prompt: "prompt",
        node_name: :test,
        dependencies: [],
        transformed_content: nil,
      )

      assert_equal("original", ctx.content)
    end
  end
end
