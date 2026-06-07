# frozen_string_literal: true

module SwarmSDK
  # Transforms raw log events into LLM-readable conversation transcripts
  #
  # TranscriptBuilder converts the structured event log from swarm execution
  # into a human/LLM-readable format suitable for reflection, analysis, or
  # memory creation.
  #
  # @example Basic usage
  #   transcript = TranscriptBuilder.build(result.logs)
  #   # => "USER: Help me with CORS\n\nAGENT [assistant]: ..."
  #
  # @example Filter by agents
  #   transcript = TranscriptBuilder.build(result.logs, agents: [:backend, :database])
  #
  # @example Custom options
  #   transcript = TranscriptBuilder.build(
  #     result.logs,
  #     include_tool_results: true,
  #     max_result_length: 1000,
  #     include_thinking: false
  #   )
  class TranscriptBuilder
    # Default maximum length for tool result content
    DEFAULT_MAX_RESULT_LENGTH = 500

    # Default maximum length for tool arguments
    DEFAULT_MAX_ARGS_LENGTH = 200

    class << self
      # Build a transcript from log events
      #
      # @param logs [Array<Hash>] Array of log events from Result#logs
      # @param agents [Array<Symbol>, nil] Filter to specific agents (nil = all)
      # @param include_tool_results [Boolean] Include tool execution results (default: true)
      # @param include_thinking [Boolean] Include agent_step content/thinking (default: false)
      # @param max_result_length [Integer] Maximum characters for tool results
      # @param max_args_length [Integer] Maximum characters for tool arguments
      # @return [String] Formatted transcript
      def build(logs, agents: nil, include_tool_results: true, include_thinking: false,
        max_result_length: DEFAULT_MAX_RESULT_LENGTH, max_args_length: DEFAULT_MAX_ARGS_LENGTH)
        new(
          logs,
          agents: agents,
          include_tool_results: include_tool_results,
          include_thinking: include_thinking,
          max_result_length: max_result_length,
          max_args_length: max_args_length,
        ).build
      end
    end

    # Initialize a new TranscriptBuilder
    #
    # @param logs [Array<Hash>] Array of log events
    # @param agents [Array<Symbol>, nil] Filter to specific agents
    # @param include_tool_results [Boolean] Include tool execution results
    # @param include_thinking [Boolean] Include agent_step content
    # @param max_result_length [Integer] Maximum characters for tool results
    # @param max_args_length [Integer] Maximum characters for tool arguments
    def initialize(logs, agents: nil, include_tool_results: true, include_thinking: false,
      max_result_length: DEFAULT_MAX_RESULT_LENGTH, max_args_length: DEFAULT_MAX_ARGS_LENGTH)
      @logs = logs || []
      @agents = normalize_agents(agents)
      @include_tool_results = include_tool_results
      @include_thinking = include_thinking
      @max_result_length = max_result_length
      @max_args_length = max_args_length
    end

    # Build the transcript
    #
    # @return [String] Formatted transcript
    def build
      @logs
        .filter_map { |event| format_event(event) }
        .join("\n\n")
    end

    private

    # Normalize agent filter to array of symbols
    #
    # @param agents [Array, Symbol, String, nil] Agent filter input
    # @return [Array<Symbol>, nil] Normalized agent list or nil for all
    def normalize_agents(agents)
      return if agents.nil? || (agents.is_a?(Array) && agents.empty?)

      Array(agents).map(&:to_sym)
    end

    # Check if event passes agent filter
    #
    # @param event [Hash] Log event
    # @return [Boolean] True if event should be included
    def passes_agent_filter?(event)
      return true if @agents.nil?

      agent = event[:agent] || event["agent"]
      return true if agent.nil? # Include events without agent (like swarm_start)

      @agents.include?(agent.to_sym)
    end

    # Format a single event into transcript text
    #
    # @param event [Hash] Log event
    # @return [String, nil] Formatted text or nil to skip
    def format_event(event)
      return unless passes_agent_filter?(event)

      type = event[:type] || event["type"]

      case type
      when "user_prompt"
        format_user_prompt(event)
      when "agent_step"
        format_agent_step(event)
      when "agent_stop"
        format_agent_stop(event)
      when "tool_call"
        format_tool_call(event)
      when "tool_result"
        format_tool_result(event)
      when "pre_delegation", "delegation_start"
        format_delegation_start(event)
      when "post_delegation", "delegation_complete"
        format_delegation_complete(event)
      end
    end

    # Format user_prompt event
    #
    # @param event [Hash] Event data
    # @return [String, nil] Formatted text
    def format_user_prompt(event)
      prompt = event[:prompt] || event["prompt"]
      return if prompt.nil? || prompt.to_s.strip.empty?

      agent = event[:agent] || event["agent"]
      source = event[:source] || event["source"] || "user"

      # Show source if it's a delegation or system message
      prefix = case source.to_s
      when "delegation"
        "DELEGATION REQUEST"
      when "system"
        "SYSTEM"
      else
        "USER"
      end

      if agent && source.to_s != "user"
        "#{prefix} → [#{agent}]: #{prompt}"
      else
        "#{prefix}: #{prompt}"
      end
    end

    # Format agent_step event (intermediate response with tool calls)
    #
    # @param event [Hash] Event data
    # @return [String, nil] Formatted text
    def format_agent_step(event)
      return unless @include_thinking

      content = event[:content] || event["content"]
      return if content.nil? || content.to_s.strip.empty?

      agent = event[:agent] || event["agent"]
      "AGENT [#{agent}] (thinking): #{content}"
    end

    # Format agent_stop event (final response)
    #
    # @param event [Hash] Event data
    # @return [String, nil] Formatted text
    def format_agent_stop(event)
      content = event[:content] || event["content"]
      return if content.nil? || content.to_s.strip.empty?

      agent = event[:agent] || event["agent"]
      "AGENT [#{agent}]: #{content}"
    end

    # Format tool_call event
    #
    # @param event [Hash] Event data
    # @return [String] Formatted text
    def format_tool_call(event)
      tool = event[:tool] || event["tool"] || event[:tool_name] || event["tool_name"]
      agent = event[:agent] || event["agent"]
      arguments = event[:arguments] || event["arguments"]

      args_str = format_arguments(arguments)
      "TOOL [#{agent}] → #{tool}(#{args_str})"
    end

    # Format tool_result event
    #
    # @param event [Hash] Event data
    # @return [String, nil] Formatted text
    def format_tool_result(event)
      return unless @include_tool_results

      tool = event[:tool] || event["tool"] || event[:tool_name] || event["tool_name"]
      result = event[:result] || event["result"]
      # Use key existence check since false || nil would lose the false value
      success = event.key?(:success) ? event[:success] : event["success"]

      # Handle RubyLLM::ToolResult objects
      result_content = if result.respond_to?(:content)
        result.content
      else
        result.to_s
      end

      truncated = truncate(result_content, @max_result_length)

      status = success == false ? " [FAILED]" : ""
      "RESULT [#{tool}]#{status}: #{truncated}"
    end

    # Format delegation_start event
    #
    # @param event [Hash] Event data
    # @return [String, nil] Formatted text
    def format_delegation_start(event)
      from = event[:from_agent] || event["from_agent"] || event[:agent] || event["agent"]
      to = event[:to_agent] || event["to_agent"]
      task = event[:task] || event["task"] || event[:message] || event["message"]

      return unless to

      task_preview = truncate(task.to_s, 200)
      "DELEGATE: #{from} → #{to}: #{task_preview}"
    end

    # Format delegation_complete event
    #
    # @param event [Hash] Event data
    # @return [String, nil] Formatted text
    def format_delegation_complete(event)
      from = event[:from_agent] || event["from_agent"] || event[:agent] || event["agent"]
      to = event[:to_agent] || event["to_agent"]

      return unless to

      "DELEGATE COMPLETE: #{to} → #{from}"
    end

    # Format tool arguments for display
    #
    # @param arguments [Hash, String, nil] Tool arguments
    # @return [String] Formatted arguments
    def format_arguments(arguments)
      return "{}" if arguments.nil?

      str = arguments.is_a?(String) ? arguments : arguments.to_json
      truncate(str, @max_args_length)
    end

    # Truncate text to maximum length with ellipsis
    #
    # @param text [String, nil] Text to truncate
    # @param max [Integer] Maximum length
    # @return [String] Truncated text
    def truncate(text, max)
      return "" if text.nil?

      str = text.to_s
      return str if str.length <= max

      "#{str[0...max]}..."
    end
  end
end
