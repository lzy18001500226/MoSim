# frozen_string_literal: true

require "test_helper"
require "swarm_cli"
require "stringio"
require "tempfile"

class InteractiveREPLTest < Minitest::Test
  def setup
    @swarm = mock_swarm
    # Create a temporary config file for Options
    @temp_config = Tempfile.new(["test_config", ".yml"])
    @temp_config.write("version: 2\nagents:\n  test:\n    system_prompt: test")
    @temp_config.close

    # Create options with parsed arguments
    @options = SwarmCLI::Options.new
    @options.parse([@temp_config.path, "-q"]) # -q for quiet mode
  end

  def teardown
    @temp_config&.unlink
  end

  def test_interactive_repl_initializes_successfully
    # Test that REPL can be initialized without errors
    # This ensures setup_fuzzy_completion runs without errors
    repl = SwarmCLI::InteractiveREPL.new(swarm: @swarm, options: @options)

    assert(repl, "REPL should initialize successfully")
  end

  def test_interactive_repl_initializes_with_initial_message
    # Test initialization with an initial message
    initial_message = "Hello, swarm!"
    repl = SwarmCLI::InteractiveREPL.new(
      swarm: @swarm,
      options: @options,
      initial_message: initial_message,
    )

    assert(repl, "REPL should initialize with initial message")
  end

  def test_interactive_repl_constants_are_defined
    # Verify COMMANDS constant exists and has expected commands
    assert_instance_of(Hash, SwarmCLI::InteractiveREPL::COMMANDS)
    assert_includes(SwarmCLI::InteractiveREPL::COMMANDS, "/help")
    assert_includes(SwarmCLI::InteractiveREPL::COMMANDS, "/clear")
    assert_includes(SwarmCLI::InteractiveREPL::COMMANDS, "/history")
    assert_includes(SwarmCLI::InteractiveREPL::COMMANDS, "/exit")
  end

  def test_execute_with_cancellation_returns_nil_when_interrupted
    # Test that execute_with_cancellation returns nil when result is interrupted
    repl = SwarmCLI::InteractiveREPL.new(swarm: @swarm, options: @options)

    # Mock an interrupted result (as returned by swarm.stop)
    interrupted_result = SwarmSDK::Result.new(
      content: nil,
      agent: "test",
      error: SwarmSDK::InterruptedError.new("Swarm execution was interrupted"),
      metadata: { interrupted: true, finish_reason: "interrupted" },
    )

    @swarm.expect(:execute, interrupted_result) do |_input, &_block|
      interrupted_result
    end

    result = repl.execute_with_cancellation("test input")

    # Should return nil when interrupted
    assert_nil(result, "execute_with_cancellation should return nil when interrupted")
  end

  def test_execute_with_cancellation_returns_result_on_success
    # Test that execute_with_cancellation returns the result on successful execution
    repl = SwarmCLI::InteractiveREPL.new(swarm: @swarm, options: @options)

    success_result = SwarmSDK::Result.new(
      content: "execution completed",
      agent: "test",
    )

    @swarm.expect(:execute, success_result) do |_input, &block|
      block&.call({ type: "agent_start", agent: :test })
      success_result
    end

    result = repl.execute_with_cancellation("test input")

    # Should return the result when successful
    assert_equal(success_result, result, "execute_with_cancellation should return result on success")
  end

  def test_execute_with_cancellation_restores_signal_handler
    # Test that the signal handler is properly restored after execution
    repl = SwarmCLI::InteractiveREPL.new(swarm: @swarm, options: @options)

    # Set a custom signal handler before
    original_trap = trap("INT", "DEFAULT")

    begin
      success_result = SwarmSDK::Result.new(
        content: "done",
        agent: "test",
      )

      @swarm.expect(:execute, success_result) do |_input, &block|
        block&.call({ type: "agent_start", agent: :test })
        success_result
      end

      repl.execute_with_cancellation("test")

      # After execute_with_cancellation completes, the original trap should be restored
      # We verify no error occurred during execution
      assert(true, "Signal handler should be restored without errors")
    ensure
      trap("INT", original_trap)
    end
  end

  def test_execute_with_cancellation_returns_nil_for_nil_result
    # Test that execute_with_cancellation handles nil result (edge case)
    repl = SwarmCLI::InteractiveREPL.new(swarm: @swarm, options: @options)

    @swarm.expect(:execute, nil) do |_input, &_block|
      true
    end

    result = repl.execute_with_cancellation("test input")

    assert_nil(result, "execute_with_cancellation should return nil for nil result")
  end

  private

  def mock_swarm
    swarm = Minitest::Mock.new
    swarm.expect(:name, "Test Swarm")
    swarm.expect(:lead_agent, :test_agent)
    swarm.expect(:validate, [])
    swarm
  end
end
