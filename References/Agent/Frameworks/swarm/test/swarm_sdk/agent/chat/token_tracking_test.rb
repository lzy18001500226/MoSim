# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Agent
    class TokenTrackingTest < Minitest::Test
      # Create a test class that includes the module
      class TestChat
        include ChatHelpers::TokenTracking

        attr_accessor :explicit_context_window, :real_model_info, :messages

        def initialize
          @messages = []
          @explicit_context_window = nil
          @real_model_info = nil
        end

        # Mock method required by TokenTracking
        def find_last_message(&block)
          @messages.reverse.find(&block)
        end

        # Mock method required by TokenTracking
        def assistant_messages
          @messages.select { |m| m.role == :assistant }
        end

        # Mock method required by TokenTracking
        def model_context_window
          200_000
        end
      end

      def setup
        @chat = TestChat.new
      end

      # ========================================
      # context_limit tests
      # ========================================

      def test_context_limit_returns_explicit_context_window_when_set
        @chat.explicit_context_window = 100_000

        assert_equal(100_000, @chat.context_limit)
      end

      def test_context_limit_returns_real_model_info_context_window
        model_info = SwarmSDK::Models::ModelInfo.new({ "context_window" => 150_000 })
        @chat.real_model_info = model_info

        assert_equal(150_000, @chat.context_limit)
      end

      def test_context_limit_falls_back_to_model_context_window
        # Neither explicit nor real_model_info set
        assert_equal(200_000, @chat.context_limit)
      end

      # ========================================
      # cumulative_input_tokens tests
      # ========================================

      def test_cumulative_input_tokens_returns_last_assistant_input_tokens
        msg1 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1000, 200, 0, 0)
        msg2 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:user, nil, nil, nil, nil)
        msg3 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 2500, 300, 0, 0)

        @chat.messages = [msg1, msg2, msg3]

        assert_equal(2500, @chat.cumulative_input_tokens)
      end

      def test_cumulative_input_tokens_returns_zero_when_no_assistant_messages
        @chat.messages = []

        assert_equal(0, @chat.cumulative_input_tokens)
      end

      # ========================================
      # cumulative_output_tokens tests
      # ========================================

      def test_cumulative_output_tokens_sums_all_assistant_output_tokens
        msg1 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1000, 200, 0, 0)
        msg2 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 2000, 300, 0, 0)

        @chat.messages = [msg1, msg2]

        assert_equal(500, @chat.cumulative_output_tokens)
      end

      # ========================================
      # context_usage_percentage tests
      # ========================================

      def test_context_usage_percentage_calculates_correctly
        @chat.explicit_context_window = 100_000

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 20_000, 5_000, 0, 0)
        @chat.messages = [msg]

        # (20000 + 5000) / 100000 * 100 = 25%
        assert_in_delta(25.0, @chat.context_usage_percentage)
      end

      def test_context_usage_percentage_returns_zero_when_no_limit
        @chat.explicit_context_window = nil
        @chat.real_model_info = nil

        # Override model_context_window to return nil
        @chat.define_singleton_method(:model_context_window) { nil }

        assert_in_delta(0.0, @chat.context_usage_percentage)
      end

      # ========================================
      # cumulative_input_cost tests
      # ========================================

      def test_cumulative_input_cost_with_valid_pricing
        model_info = SwarmSDK::Models::ModelInfo.new({
          "pricing" => {
            "text_tokens" => {
              "standard" => {
                "input_per_million" => 3.0,
                "output_per_million" => 15.0,
              },
            },
          },
        })
        @chat.real_model_info = model_info

        # Add assistant message with 1 million input tokens
        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 100_000, 0, 0)
        @chat.messages = [msg]

        # 1_000_000 / 1_000_000 * 3.0 = $3.00
        assert_in_delta(3.0, @chat.cumulative_input_cost, 0.001)
      end

      def test_cumulative_input_cost_with_symbol_keys
        model_info = SwarmSDK::Models::ModelInfo.new({
          pricing: {
            text_tokens: {
              standard: {
                input_per_million: 5.0,
                output_per_million: 20.0,
              },
            },
          },
        })
        @chat.real_model_info = model_info

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 500_000, 50_000, 0, 0)
        @chat.messages = [msg]

        # 500_000 / 1_000_000 * 5.0 = $2.50
        assert_in_delta(2.5, @chat.cumulative_input_cost, 0.001)
      end

      def test_cumulative_input_cost_returns_zero_without_pricing
        @chat.real_model_info = nil

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 100_000, 0, 0)
        @chat.messages = [msg]

        assert_in_delta(0.0, @chat.cumulative_input_cost)
      end

      def test_cumulative_input_cost_returns_zero_with_empty_pricing
        model_info = SwarmSDK::Models::ModelInfo.new({ "pricing" => {} })
        @chat.real_model_info = model_info

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 100_000, 0, 0)
        @chat.messages = [msg]

        assert_in_delta(0.0, @chat.cumulative_input_cost)
      end

      def test_cumulative_input_cost_returns_zero_with_missing_text_tokens
        model_info = SwarmSDK::Models::ModelInfo.new({
          "pricing" => {
            "image_tokens" => {},
          },
        })
        @chat.real_model_info = model_info

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 100_000, 0, 0)
        @chat.messages = [msg]

        assert_in_delta(0.0, @chat.cumulative_input_cost)
      end

      def test_cumulative_input_cost_returns_zero_with_missing_standard
        model_info = SwarmSDK::Models::ModelInfo.new({
          "pricing" => {
            "text_tokens" => {
              "batch" => {},
            },
          },
        })
        @chat.real_model_info = model_info

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 100_000, 0, 0)
        @chat.messages = [msg]

        assert_in_delta(0.0, @chat.cumulative_input_cost)
      end

      # ========================================
      # cumulative_output_cost tests
      # ========================================

      def test_cumulative_output_cost_with_valid_pricing
        model_info = SwarmSDK::Models::ModelInfo.new({
          "pricing" => {
            "text_tokens" => {
              "standard" => {
                "input_per_million" => 3.0,
                "output_per_million" => 15.0,
              },
            },
          },
        })
        @chat.real_model_info = model_info

        # Add multiple assistant messages
        msg1 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 500_000, 250_000, 0, 0)
        msg2 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 250_000, 0, 0)
        @chat.messages = [msg1, msg2]

        # (250_000 + 250_000) / 1_000_000 * 15.0 = $7.50
        assert_in_delta(7.5, @chat.cumulative_output_cost, 0.001)
      end

      def test_cumulative_output_cost_returns_zero_without_pricing
        @chat.real_model_info = nil

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 500_000, 250_000, 0, 0)
        @chat.messages = [msg]

        assert_in_delta(0.0, @chat.cumulative_output_cost)
      end

      # ========================================
      # cumulative_total_cost tests
      # ========================================

      def test_cumulative_total_cost_sums_input_and_output
        model_info = SwarmSDK::Models::ModelInfo.new({
          "pricing" => {
            "text_tokens" => {
              "standard" => {
                "input_per_million" => 3.0,
                "output_per_million" => 15.0,
              },
            },
          },
        })
        @chat.real_model_info = model_info

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 500_000, 0, 0)
        @chat.messages = [msg]

        # Input: 1_000_000 / 1_000_000 * 3.0 = $3.00
        # Output: 500_000 / 1_000_000 * 15.0 = $7.50
        # Total: $10.50
        assert_in_delta(10.5, @chat.cumulative_total_cost, 0.001)
      end

      def test_cumulative_total_cost_returns_zero_without_pricing
        @chat.real_model_info = nil

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1_000_000, 500_000, 0, 0)
        @chat.messages = [msg]

        assert_in_delta(0.0, @chat.cumulative_total_cost)
      end

      def test_cumulative_total_cost_with_multiple_messages
        model_info = SwarmSDK::Models::ModelInfo.new({
          "pricing" => {
            "text_tokens" => {
              "standard" => {
                "input_per_million" => 3.0,
                "output_per_million" => 15.0,
              },
            },
          },
        })
        @chat.real_model_info = model_info

        # Multiple messages - cumulative_input_tokens uses last assistant's input
        msg1 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 500_000, 100_000, 0, 0)
        msg2 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 800_000, 200_000, 0, 0)
        @chat.messages = [msg1, msg2]

        # Input: 800_000 (last assistant's input_tokens) / 1_000_000 * 3.0 = $2.40
        # Output: (100_000 + 200_000) / 1_000_000 * 15.0 = $4.50
        # Total: $6.90
        assert_in_delta(6.9, @chat.cumulative_total_cost, 0.001)
      end

      # ========================================
      # tokens_remaining tests
      # ========================================

      def test_tokens_remaining_calculates_correctly
        @chat.explicit_context_window = 200_000

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 50_000, 10_000, 0, 0)
        @chat.messages = [msg]

        # 200_000 - (50_000 + 10_000) = 140_000
        assert_equal(140_000, @chat.tokens_remaining)
      end

      def test_tokens_remaining_returns_nil_without_limit
        @chat.explicit_context_window = nil
        @chat.real_model_info = nil
        @chat.define_singleton_method(:model_context_window) { nil }

        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 50_000, 10_000, 0, 0)
        @chat.messages = [msg]

        assert_nil(@chat.tokens_remaining)
      end

      # ========================================
      # cumulative_cached_tokens tests
      # ========================================

      def test_cumulative_cached_tokens_sums_all_assistant_cached_tokens
        msg1 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 1000, 200, 500, 0)
        msg2 = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 2000, 300, 300, 0)

        @chat.messages = [msg1, msg2]

        assert_equal(800, @chat.cumulative_cached_tokens)
      end

      # ========================================
      # effective_input_tokens tests
      # ========================================

      def test_effective_input_tokens_subtracts_cached
        msg = Struct.new(:role, :input_tokens, :output_tokens, :cached_tokens, :cache_creation_tokens)
          .new(:assistant, 10_000, 2_000, 3_000, 0)
        @chat.messages = [msg]

        # 10_000 - 3_000 = 7_000
        assert_equal(7_000, @chat.effective_input_tokens)
      end
    end
  end
end
