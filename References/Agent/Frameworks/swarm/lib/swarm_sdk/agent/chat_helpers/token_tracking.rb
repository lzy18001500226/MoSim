# frozen_string_literal: true

module SwarmSDK
  module Agent
    module ChatHelpers
      # Token usage tracking and context limit management
      #
      # Extracted from Chat to reduce class size and centralize token metrics.
      module TokenTracking
        # Get context window limit for the current model
        #
        # @return [Integer, nil] Maximum context tokens
        def context_limit
          return @explicit_context_window if @explicit_context_window
          return @real_model_info.context_window if @real_model_info&.context_window

          model_context_window
        rescue StandardError
          nil
        end

        # Calculate cumulative input tokens for the conversation
        #
        # Gets input_tokens from the most recent assistant message, which represents
        # the total context size sent to the model (not sum of all messages).
        #
        # @return [Integer] Total input tokens used
        def cumulative_input_tokens
          find_last_message { |msg| msg.role == :assistant && msg.input_tokens }&.input_tokens || 0
        end

        # Calculate cumulative output tokens across all assistant messages
        #
        # @return [Integer] Total output tokens used
        def cumulative_output_tokens
          assistant_messages.sum { |msg| msg.output_tokens || 0 }
        end

        # Calculate cumulative cached tokens
        #
        # @return [Integer] Total cached tokens used
        def cumulative_cached_tokens
          assistant_messages.sum { |msg| msg.cached_tokens || 0 }
        end

        # Calculate cumulative cache creation tokens
        #
        # @return [Integer] Total tokens written to cache
        def cumulative_cache_creation_tokens
          assistant_messages.sum { |msg| msg.cache_creation_tokens || 0 }
        end

        # Calculate effective input tokens (excluding cache hits)
        #
        # @return [Integer] Actual input tokens charged
        def effective_input_tokens
          cumulative_input_tokens - cumulative_cached_tokens
        end

        # Calculate total tokens used (input + output)
        #
        # @return [Integer] Total tokens used
        def cumulative_total_tokens
          cumulative_input_tokens + cumulative_output_tokens
        end

        # Calculate percentage of context window used
        #
        # @return [Float] Percentage (0.0 to 100.0)
        def context_usage_percentage
          limit = context_limit
          return 0.0 if limit.nil? || limit.zero?

          (cumulative_total_tokens.to_f / limit * 100).round(2)
        end

        # Calculate remaining tokens in context window
        #
        # @return [Integer, nil] Tokens remaining
        def tokens_remaining
          limit = context_limit
          return if limit.nil?

          limit - cumulative_total_tokens
        end

        # Calculate cumulative input cost based on tokens and model pricing
        #
        # @return [Float] Total input cost in dollars
        def cumulative_input_cost
          pricing = model_pricing
          return 0.0 unless pricing

          input_price = pricing["input_per_million"] || pricing[:input_per_million] || 0.0
          (cumulative_input_tokens / 1_000_000.0) * input_price
        end

        # Calculate cumulative output cost based on tokens and model pricing
        #
        # @return [Float] Total output cost in dollars
        def cumulative_output_cost
          pricing = model_pricing
          return 0.0 unless pricing

          output_price = pricing["output_per_million"] || pricing[:output_per_million] || 0.0
          (cumulative_output_tokens / 1_000_000.0) * output_price
        end

        # Calculate cumulative total cost (input + output)
        #
        # @return [Float] Total cost in dollars
        def cumulative_total_cost
          cumulative_input_cost + cumulative_output_cost
        end

        # Compact the conversation history to reduce token usage
        #
        # @param options [Hash] Compression options
        # @return [ContextCompactor::Metrics] Compression statistics
        def compact_context(**options)
          compactor = ContextCompactor.new(self, options)
          compactor.compact
        end

        private

        # Get pricing info for the current model
        #
        # Extracts standard text token pricing from model info.
        #
        # @return [Hash, nil] Pricing hash with input_per_million and output_per_million
        def model_pricing
          return unless @real_model_info&.pricing

          pricing = @real_model_info.pricing
          text_pricing = pricing["text_tokens"] || pricing[:text_tokens]
          return unless text_pricing

          text_pricing["standard"] || text_pricing[:standard]
        rescue StandardError
          nil
        end
      end
    end
  end
end
