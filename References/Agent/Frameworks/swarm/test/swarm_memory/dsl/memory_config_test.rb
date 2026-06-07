# frozen_string_literal: true

require "test_helper"

module SwarmMemory
  module DSL
    class MemoryConfigTest < Minitest::Test
      def setup
        @config = MemoryConfig.new
      end

      # semantic_weight DSL method tests

      def test_semantic_weight_sets_value
        @config.semantic_weight(0.8)

        assert_in_delta(0.8, @config.adapter_options[:semantic_weight])
      end

      def test_semantic_weight_returns_current_value
        @config.semantic_weight(0.7)

        assert_in_delta(0.7, @config.semantic_weight)
      end

      def test_semantic_weight_returns_nil_when_not_set
        assert_nil(@config.semantic_weight)
      end

      def test_semantic_weight_converts_to_float
        @config.semantic_weight("0.9")

        assert_in_delta(0.9, @config.adapter_options[:semantic_weight])
        assert_instance_of(Float, @config.adapter_options[:semantic_weight])
      end

      # keyword_weight DSL method tests

      def test_keyword_weight_sets_value
        @config.keyword_weight(0.2)

        assert_in_delta(0.2, @config.adapter_options[:keyword_weight])
      end

      def test_keyword_weight_returns_current_value
        @config.keyword_weight(0.3)

        assert_in_delta(0.3, @config.keyword_weight)
      end

      def test_keyword_weight_returns_nil_when_not_set
        assert_nil(@config.keyword_weight)
      end

      def test_keyword_weight_converts_to_float
        @config.keyword_weight("0.1")

        assert_in_delta(0.1, @config.adapter_options[:keyword_weight])
        assert_instance_of(Float, @config.adapter_options[:keyword_weight])
      end

      # Combined usage tests

      def test_weights_combined_for_pure_semantic_search
        @config.semantic_weight(1.0)
        @config.keyword_weight(0.0)

        assert_in_delta(1.0, @config.adapter_options[:semantic_weight])
        assert_in_delta(0.0, @config.adapter_options[:keyword_weight])
      end

      def test_weights_included_in_to_h
        @config.directory("/tmp/memory")
        @config.semantic_weight(0.8)
        @config.keyword_weight(0.2)

        result = @config.to_h

        assert_equal("/tmp/memory", result[:directory])
        assert_in_delta(0.8, result[:semantic_weight])
        assert_in_delta(0.2, result[:keyword_weight])
      end

      def test_instance_eval_block_syntax
        @config.instance_eval do
          directory("/tmp/test")
          semantic_weight(0.9)
          keyword_weight(0.1)
        end

        assert_equal("/tmp/test", @config.directory)
        assert_in_delta(0.9, @config.semantic_weight)
        assert_in_delta(0.1, @config.keyword_weight)
      end

      # Verify option method still works for weights (backwards compatibility)

      def test_option_method_still_works_for_semantic_weight
        @config.option(:semantic_weight, 0.75)

        assert_in_delta(0.75, @config.adapter_options[:semantic_weight])
      end

      def test_option_method_still_works_for_keyword_weight
        @config.option(:keyword_weight, 0.25)

        assert_in_delta(0.25, @config.adapter_options[:keyword_weight])
      end
    end
  end
end
