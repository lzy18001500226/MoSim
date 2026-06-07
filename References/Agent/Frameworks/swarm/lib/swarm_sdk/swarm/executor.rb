# frozen_string_literal: true

module SwarmSDK
  class Swarm
    # Handles swarm execution orchestration
    #
    # Extracted from Swarm#execute to reduce complexity and eliminate code duplication.
    # The core execution loop, error handling, and cleanup logic are unified here.
    #
    # ## Stop Mechanism
    #
    # Supports hard-stop via `swarm.stop` using IO.pipe for thread-safe signaling:
    # 1. `swarm.stop` writes to pipe and sets `@stop_requested`
    # 2. A listener task reads from the pipe (async-aware I/O)
    # 3. Listener calls `barrier.stop` within the Async reactor
    # 4. All child tasks receive `Async::Stop` exception
    # 5. `execute_in_task` catches `Async::Stop`, sets interrupted flag, emits events
    class Executor
      def initialize(swarm)
        @swarm = swarm
        @interrupted_result = nil
      end

      # Execute the swarm with a prompt
      #
      # @param prompt [String] User prompt
      # @param wait [Boolean] Block until completion (true) or return task (false)
      # @param logs [Array] Log collection array
      # @param has_logging [Boolean] Whether logging is enabled
      # @param original_fiber_storage [Hash] Original Fiber storage values to restore
      # @return [Result, Async::Task] Result if wait: true, Async::Task if wait: false
      def run(prompt, wait:, logs:, has_logging:, original_fiber_storage:)
        @original_fiber_storage = original_fiber_storage
        if wait
          run_blocking(prompt, logs: logs, has_logging: has_logging)
        else
          run_async(prompt, logs: logs, has_logging: has_logging)
        end
      end

      private

      # Blocking execution using Sync
      #
      # Wraps execution in an Async::Barrier so `swarm.stop` can cancel all tasks.
      # A stop listener task watches the IO.pipe for stop signals.
      def run_blocking(prompt, logs:, has_logging:)
        result = nil
        start_time = Time.now
        @swarm.prepare_for_execution

        Sync do |task|
          barrier = Async::Barrier.new
          @swarm.register_execution_barrier(barrier)
          stop_listener = setup_stop_listener(task, barrier)

          begin
            result = barrier.async do
              if @swarm.execution_timeout
                execute_with_execution_timeout(task, prompt, logs, has_logging, start_time)
              else
                execute_in_task(prompt, logs: logs, has_logging: has_logging) do |lead, current_prompt|
                  lead.ask(current_prompt)
                end
              end
            end.wait

            # barrier child .wait returns nil when stopped
            result = @interrupted_result if result.nil? && @swarm.stop_requested?
          rescue Async::Stop
            # Non-blocking path (rare - user called task.stop on Sync root)
            result = @interrupted_result
          ensure
            barrier.stop unless barrier.empty?
            stop_listener&.stop
            @swarm.clear_execution_barrier
          end
        ensure
          # Always wait for observer tasks, even if main execution raises
          # This is INSIDE Sync block, so async tasks can still complete
          @swarm.wait_for_observers
        end

        result
      ensure
        @interrupted_result = nil
        @swarm.cleanup_stop_signal
        restore_fiber_storage
      end

      # Non-blocking execution using parent async task
      #
      # Same barrier + stop listener pattern as run_blocking.
      def run_async(prompt, logs:, has_logging:)
        parent = Async::Task.current
        raise ConfigurationError, "wait: false requires an async context. Use Sync { swarm.execute(..., wait: false) }" unless parent

        @swarm.prepare_for_execution

        # NOTE: The block receives |task| as the spawned Async::Task when arity > 0
        parent.async(finished: false) do |task|
          start_time = Time.now
          barrier = Async::Barrier.new
          @swarm.register_execution_barrier(barrier)
          stop_listener = setup_stop_listener(task, barrier)

          begin
            result = barrier.async do
              if @swarm.execution_timeout
                execute_with_execution_timeout(task, prompt, logs, has_logging, start_time)
              else
                execute_in_task(prompt, logs: logs, has_logging: has_logging) do |lead, current_prompt|
                  lead.ask(current_prompt)
                end
              end
            end.wait

            result = @interrupted_result if result.nil? && @swarm.stop_requested?
            result
          rescue Async::Stop
            @interrupted_result
          ensure
            barrier.stop unless barrier.empty?
            stop_listener&.stop
            @swarm.clear_execution_barrier
            @interrupted_result = nil
            @swarm.cleanup_stop_signal
            @swarm.wait_for_observers
          end
        end
      end

      # Setup a listener task that watches for stop signals via IO.pipe
      #
      # The listener reads from the pipe (async-aware I/O that yields to scheduler).
      # When data arrives (from `swarm.stop`), it stops the barrier to cancel all tasks.
      #
      # @param task [Async::Task] Parent task to spawn listener under
      # @param barrier [Async::Barrier] Execution barrier to stop
      # @return [Async::Task, nil] The listener task, or nil if no pipe
      def setup_stop_listener(task, barrier)
        return unless @swarm.stop_signal_read

        task.async do
          @swarm.stop_signal_read.read(1) # Async-aware I/O, yields to scheduler
          barrier.stop unless barrier.empty?
        rescue IOError, Async::Stop
          # Pipe closed or listener stopped - normal cleanup
        end
      end

      # Core execution logic (unified, no duplication)
      #
      # Handles InterruptedError and Async::Stop to properly track interruption state.
      # The interrupted flag drives cleanup behavior (event emission, result building).
      #
      # @param prompt [String] Initial prompt
      # @param logs [Array] Log collection
      # @param has_logging [Boolean] Whether logging is enabled
      # @yield [lead, current_prompt] Block to execute LLM call
      # @return [Result] Execution result
      def execute_in_task(prompt, logs:, has_logging:, &block)
        start_time = Time.now
        result = nil
        swarm_stop_triggered = false
        current_prompt = prompt
        interrupted = false

        begin
          # Notify plugins that swarm is starting
          PluginRegistry.emit_event(:on_swarm_started, swarm: @swarm)

          result = execution_loop(current_prompt, logs, start_time, &block)
          swarm_stop_triggered = true
        rescue ConfigurationError, AgentNotFoundError, ExecutionTimeoutError, TurnTimeoutError
          # Re-raise configuration errors and timeouts - these should not be caught here
          # Timeouts are handled by execute_with_execution_timeout wrapper
          raise
        rescue InterruptedError
          interrupted = true
          raise
        rescue Async::Stop
          interrupted = true
          raise # Must re-raise for Async task cleanup
        rescue TypeError => e
          result = handle_type_error(e, logs, start_time)
        rescue StandardError => e
          result = handle_standard_error(e, logs, start_time)
        ensure
          # Notify plugins that swarm is stopping (called even on error)
          PluginRegistry.emit_event(:on_swarm_stopped, swarm: @swarm)

          result = cleanup_after_execution(
            result,
            start_time,
            logs,
            swarm_stop_triggered,
            has_logging,
            interrupted: interrupted,
          )
          @interrupted_result = result if interrupted
        end

        result
      end

      # Main execution loop with reprompting support
      #
      # Checks for stop requests at the top of each iteration to prevent
      # unnecessary LLM calls after stop is requested.
      def execution_loop(initial_prompt, logs, start_time)
        current_prompt = initial_prompt

        loop do
          raise InterruptedError, "Swarm execution was interrupted" if @swarm.stop_requested?

          lead = @swarm.agents[@swarm.lead_agent]
          response = yield(lead, current_prompt)

          # Check if swarm was finished by a hook (finish_swarm)
          if response.is_a?(Hash) && response[:__finish_swarm__]
            result = build_result(response[:message], logs, start_time)
            @swarm.trigger_swarm_stop(result)
            return result
          end

          result = build_result(response.content, logs, start_time)

          # Trigger swarm_stop hooks (for reprompt check and event emission)
          hook_result = @swarm.trigger_swarm_stop(result)

          # Check if hook requests reprompting
          if hook_result&.reprompt?
            current_prompt = hook_result.value
            # Continue loop with new prompt
          else
            # Exit loop - execution complete
            return result
          end
        end
      end

      # Build a Result object
      def build_result(content, logs, start_time)
        Result.new(
          content: content,
          agent: @swarm.lead_agent.to_s,
          logs: logs,
          duration: Time.now - start_time,
        )
      end

      # Handle TypeError (e.g., "String does not have #dig method")
      def handle_type_error(error, logs, start_time)
        if error.message.include?("does not have #dig method")
          agent_definition = @swarm.agent_definitions[@swarm.lead_agent]
          error_msg = if agent_definition.base_url
            "LLM API request failed: The proxy/server at '#{agent_definition.base_url}' returned an invalid response. " \
              "This usually means the proxy is unreachable, requires authentication, or returned an error in non-JSON format. " \
              "Original error: #{error.message}"
          else
            "LLM API request failed with unexpected response format. Original error: #{error.message}"
          end

          Result.new(
            content: nil,
            agent: @swarm.lead_agent.to_s,
            error: LLMError.new(error_msg),
            logs: logs,
            duration: Time.now - start_time,
          )
        else
          Result.new(
            content: nil,
            agent: @swarm.lead_agent.to_s,
            error: error,
            logs: logs,
            duration: Time.now - start_time,
          )
        end
      end

      # Handle StandardError
      def handle_standard_error(error, logs, start_time)
        Result.new(
          content: nil,
          agent: @swarm.lead_agent&.to_s || "unknown",
          error: error,
          logs: logs,
          duration: Time.now - start_time,
        )
      end

      # Cleanup after execution (ensure block logic)
      #
      # When interrupted, emits agent_stop events for active agents, builds
      # an interrupted result, and triggers swarm_stop hook with interrupted context.
      #
      # @param result [Result, nil] Current execution result
      # @param start_time [Time] Execution start time
      # @param logs [Array] Collected logs
      # @param swarm_stop_triggered [Boolean] Whether swarm_stop hook already fired
      # @param has_logging [Boolean] Whether logging is enabled
      # @param interrupted [Boolean] Whether execution was interrupted
      # @return [Result] Final result (may be replaced with interrupted result)
      def cleanup_after_execution(result, start_time, logs, swarm_stop_triggered, has_logging, interrupted: false)
        if interrupted && !swarm_stop_triggered
          emit_interrupted_agent_events
          result = build_interrupted_result(logs, start_time)

          # Trigger swarm_stop hook with interrupted result (emits swarm_stop event)
          begin
            @swarm.trigger_swarm_stop(result)
          rescue StandardError => e
            LogStream.emit_error(e, source: "executor", context: "interrupted_swarm_stop")
          end
          swarm_stop_triggered = true
        end

        # Trigger swarm_stop if not already triggered (handles error cases)
        unless swarm_stop_triggered
          @swarm.trigger_swarm_stop_final(result, start_time, logs)
        end

        # Cleanup MCP clients after execution
        @swarm.cleanup

        # Cleanup observer subscriptions (matches MCP cleanup pattern)
        @swarm.cleanup_observers

        # Restore original Fiber storage (preserves parent context for nested swarms)
        restore_fiber_storage

        # Reset logging state for next execution if we set it up
        reset_logging if has_logging

        result
      end

      # Emit agent_stop events for all agents that were actively executing when interrupted
      #
      # @return [void]
      def emit_interrupted_agent_events
        @swarm.active_agent_chats.each do |name, _chat|
          LogStream.emit(
            type: "agent_stop",
            agent: name,
            swarm_id: @swarm.swarm_id,
            parent_swarm_id: @swarm.parent_swarm_id,
            finish_reason: "interrupted",
            content: nil,
            tool_calls: [],
            usage: {},
            metadata: { interrupted: true },
          )
        end
      end

      # Build an interrupted result
      #
      # @param logs [Array] Collected logs
      # @param start_time [Time] Execution start time
      # @return [Result] Result marked as interrupted
      def build_interrupted_result(logs, start_time)
        Result.new(
          content: nil,
          agent: @swarm.lead_agent&.to_s || "unknown",
          error: InterruptedError.new("Swarm execution was interrupted"),
          logs: logs,
          duration: Time.now - start_time,
          metadata: { interrupted: true, finish_reason: "interrupted" },
        )
      end

      # Restore Fiber-local storage to original values (preserves parent context)
      def restore_fiber_storage
        Fiber[:execution_id] = @original_fiber_storage[:execution_id]
        Fiber[:swarm_id] = @original_fiber_storage[:swarm_id]
        Fiber[:parent_swarm_id] = @original_fiber_storage[:parent_swarm_id]
      end

      # Reset logging state
      def reset_logging
        LogCollector.reset!
        LogStream.reset!
      end

      # Execute with execution timeout wrapper
      def execute_with_execution_timeout(task, prompt, logs, has_logging, start_time)
        # Use Async::Task.current to get the actual current task context
        current_task = Async::Task.current || task

        # Use barrier to track ALL child tasks spawned during execution
        # This includes RubyLLM's async tool execution (when max_concurrent_tools is set)
        barrier = Async::Barrier.new

        begin
          current_task.with_timeout(
            @swarm.execution_timeout,
            ExecutionTimeoutError,
            "Swarm execution timed out after #{@swarm.execution_timeout}s",
          ) do
            # Execute inside barrier to track child tasks (tool executions)
            barrier.async do
              execute_in_task(prompt, logs: logs, has_logging: has_logging) do |lead, current_prompt|
                lead.ask(current_prompt)
              end
            end.wait
          end
        rescue ExecutionTimeoutError => e
          # Stop ALL child tasks (interrupts ongoing tool executions and delegations)
          barrier.stop

          emit_execution_timeout_event(@swarm.execution_timeout)
          build_timeout_result(e, logs, Time.now - start_time)
        ensure
          # Cleanup barrier if not already stopped
          barrier.stop unless barrier.empty?
        end
      end

      # Emit execution timeout event
      def emit_execution_timeout_event(limit)
        LogStream.emit(
          type: "execution_timeout",
          swarm_id: @swarm.swarm_id,
          parent_swarm_id: @swarm.parent_swarm_id,
          limit: limit,
          message: "Swarm execution timed out after #{limit}s",
        )
      end

      # Build timeout result
      def build_timeout_result(error, logs, duration)
        Result.new(
          content: nil,
          agent: @swarm.lead_agent&.to_s || "unknown",
          error: error,
          logs: logs,
          duration: duration,
          metadata: { timeout: true },
        )
      end
    end
  end
end
