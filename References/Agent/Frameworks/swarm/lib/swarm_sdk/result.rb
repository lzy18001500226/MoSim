# frozen_string_literal: true

module SwarmSDK
  class Result
    attr_reader :content, :agent, :duration, :logs, :error, :metadata

    def initialize(content: nil, agent:, cost: nil, tokens: nil, duration: 0.0, logs: [], error: nil, metadata: {})
      @content = content
      @agent = agent
      @duration = duration
      @logs = logs
      @error = error
      @metadata = metadata
      # Legacy parameters kept for backward compatibility but not stored
      # Use total_cost and tokens methods instead which calculate from logs
    end

    def success?
      @error.nil?
    end

    def failure?
      !success?
    end

    # Check if execution was interrupted via swarm.stop
    #
    # @return [Boolean] true if execution was interrupted
    #
    # @example
    #   result = swarm.execute("Build auth")
    #   result.interrupted?  # => false
    #
    #   # After calling swarm.stop during execution:
    #   result.interrupted?  # => true
    def interrupted?
      @metadata[:interrupted] == true
    end

    # Get the reason execution finished
    #
    # Possible values:
    # - "finished" - Normal completion
    # - "interrupted" - Stopped via swarm.stop
    # - "error" - Execution failed with an error
    #
    # @return [String] The finish reason
    #
    # @example
    #   result.finish_reason  # => "finished"
    def finish_reason
      @metadata[:finish_reason] || (success? ? "finished" : "error")
    end

    # Calculate total cost from logs
    #
    # Delegates to total_cost for consistency. This attribute is calculated
    # dynamically rather than stored.
    #
    # @return [Float] Total cost in dollars
    def cost
      total_cost
    end

    # Get token breakdown from logs
    #
    # Returns input and output tokens from the last log entry with usage data.
    # This attribute is calculated dynamically rather than stored.
    #
    # @return [Hash] Token breakdown with :input and :output keys, or empty hash if no usage data
    def tokens
      last_entry = @logs.reverse.find { |entry| entry.dig(:usage, :cumulative_input_tokens) }
      return {} unless last_entry

      {
        input: last_entry.dig(:usage, :cumulative_input_tokens) || 0,
        output: last_entry.dig(:usage, :cumulative_output_tokens) || 0,
      }
    end

    def to_h
      {
        content: @content,
        agent: @agent,
        cost: cost,
        tokens: tokens,
        duration: @duration,
        success: success?,
        error: @error&.message,
        metadata: @metadata,
      }.compact
    end

    def to_json(*args)
      to_h.to_json(*args)
    end

    # Calculate total cost across all LLM responses
    #
    # Cost accumulation works as follows:
    # - Input cost: The LAST response's input_cost already includes the cost for the
    #   full conversation history (all previous messages + current context)
    # - Output cost: Each response generates NEW tokens, so we SUM all output_costs
    # - Total = Last input_cost + Sum of all output_costs
    #
    # IMPORTANT: Do NOT sum total_cost across all entries - that would count
    # input costs multiple times since each call includes the full history!
    def total_cost
      entries_with_usage = @logs.select { |entry| entry.dig(:usage, :total_cost) }
      return 0.0 if entries_with_usage.empty?

      # Last entry's input cost (includes full conversation history)
      last_input_cost = entries_with_usage.last.dig(:usage, :input_cost) || 0.0

      # Sum all output costs (each response generates new tokens)
      total_output_cost = entries_with_usage.sum { |entry| entry.dig(:usage, :output_cost) || 0.0 }

      last_input_cost + total_output_cost
    end

    # Get total tokens from the last LLM response with cumulative tracking
    #
    # Token accumulation works as follows:
    # - Input tokens: Each API call sends the full conversation history, so the latest
    #   response's cumulative_input_tokens already represents the full context
    # - Output tokens: Each response generates new tokens, cumulative_output_tokens sums them
    # - The cumulative_total_tokens in the last response already does this correctly
    #
    # IMPORTANT: Do NOT sum total_tokens across all log entries - that would count
    # input tokens multiple times since each call includes the full history!
    def total_tokens
      last_entry = @logs.reverse.find { |entry| entry.dig(:usage, :cumulative_total_tokens) }
      last_entry&.dig(:usage, :cumulative_total_tokens) || 0
    end

    # Get list of all agents involved in execution
    def agents_involved
      @logs.map { |entry| entry[:agent] }.compact.uniq.map(&:to_sym)
    end

    # Generate an LLM-readable transcript of the conversation
    #
    # Converts the execution logs into a human/LLM-readable format suitable for
    # reflection, analysis, memory creation, or passing to another agent.
    #
    # @param agents [Array<Symbol>] Optional list of agents to filter by.
    #   If no agents specified, includes all agents.
    #   If one or more agents specified, only includes events from those agents.
    # @param include_tool_results [Boolean] Include tool execution results (default: true)
    # @param include_thinking [Boolean] Include agent_step content/thinking (default: false)
    # @return [String] Formatted transcript ready for LLM consumption
    #
    # @example Get full transcript
    #   result.transcript
    #   # => "USER: Help me with CORS\n\nAGENT [assistant]: ..."
    #
    # @example Filter to specific agents
    #   result.transcript(:backend, :database)
    #   # => Only events from backend and database agents
    #
    # @example Single agent transcript
    #   result.transcript(:backend)
    #   # => Only events from backend agent
    #
    # @example Include thinking steps
    #   result.transcript(include_thinking: true)
    #   # => Includes agent_step intermediate reasoning
    def transcript(*agents, include_tool_results: true, include_thinking: false)
      agent_filter = agents.empty? ? nil : agents
      TranscriptBuilder.build(
        @logs,
        agents: agent_filter,
        include_tool_results: include_tool_results,
        include_thinking: include_thinking,
      )
    end

    # Get per-agent usage breakdown from logs
    #
    # Aggregates context usage, tokens, and cost for each agent from their
    # final agent_stop or agent_step events. Each agent's entry includes:
    # - input_tokens, output_tokens, total_tokens
    # - context_limit, usage_percentage, tokens_remaining
    # - input_cost, output_cost, total_cost
    #
    # @return [Hash{Symbol => Hash}] Per-agent usage breakdown
    #
    # @example
    #   result.per_agent_usage[:backend]
    #   # => {
    #   #   input_tokens: 15000,
    #   #   output_tokens: 5000,
    #   #   total_tokens: 20000,
    #   #   context_limit: 200000,
    #   #   usage_percentage: "10.0%",
    #   #   tokens_remaining: 180000,
    #   #   input_cost: 0.045,
    #   #   output_cost: 0.075,
    #   #   total_cost: 0.12
    #   # }
    def per_agent_usage
      # Find the last usage entry for each agent
      agent_entries = {}

      @logs.each do |entry|
        next unless entry[:usage] && entry[:agent]
        next unless entry[:type] == "agent_step" || entry[:type] == "agent_stop"

        agent_name = entry[:agent].to_sym
        agent_entries[agent_name] = entry[:usage]
      end

      # Build breakdown from final usage entries
      agent_entries.transform_values do |usage|
        {
          input_tokens: usage[:cumulative_input_tokens] || 0,
          output_tokens: usage[:cumulative_output_tokens] || 0,
          total_tokens: usage[:cumulative_total_tokens] || 0,
          cached_tokens: usage[:cumulative_cached_tokens] || 0,
          context_limit: usage[:context_limit],
          usage_percentage: usage[:tokens_used_percentage],
          tokens_remaining: usage[:tokens_remaining],
          input_cost: usage[:input_cost] || 0.0,
          output_cost: usage[:output_cost] || 0.0,
          total_cost: usage[:total_cost] || 0.0,
        }
      end
    end

    # Count total LLM requests made
    # Each LLM API call produces either agent_step (tool calls) or agent_stop (final answer)
    def llm_requests
      @logs.count { |entry| entry[:type] == "agent_step" || entry[:type] == "agent_stop" }
    end

    # Count total tool calls made
    def tool_calls_count
      @logs.count { |entry| entry[:type] == "tool_call" }
    end
  end
end
