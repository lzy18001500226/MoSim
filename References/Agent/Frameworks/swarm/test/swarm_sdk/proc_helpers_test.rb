# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class ProcHelpersTest < Minitest::Test
    def test_to_lambda_converts_proc_to_lambda
      my_proc = proc { |x| x * 2 }

      refute_predicate(my_proc, :lambda?)

      my_lambda = ProcHelpers.to_lambda(my_proc)

      assert_predicate(my_lambda, :lambda?)
    end

    def test_to_lambda_preserves_already_lambda
      my_lambda = lambda { |x| x * 2 }
      result = ProcHelpers.to_lambda(my_lambda)

      assert_same(my_lambda, result)
      assert_predicate(result, :lambda?)
    end

    def test_to_lambda_enables_safe_return
      # This proc would exit the enclosing method if called directly
      my_proc = proc { |x|
        return x * 2 if x > 0

        0
      }

      # Convert to lambda
      my_lambda = ProcHelpers.to_lambda(my_proc)

      # Now return only exits the lambda, not the test method
      result = my_lambda.call(5)

      assert_equal(10, result)

      result = my_lambda.call(-1)

      assert_equal(0, result)
    end

    def test_to_lambda_preserves_closures
      captured_value = "hello"
      my_proc = proc { |x| "#{captured_value} #{x}" }

      my_lambda = ProcHelpers.to_lambda(my_proc)
      result = my_lambda.call("world")

      assert_equal("hello world", result)
    end

    def test_to_lambda_works_with_keyword_arguments
      my_proc = proc { |x:, y:| x + y }
      my_lambda = ProcHelpers.to_lambda(my_proc)

      result = my_lambda.call(x: 5, y: 3)

      assert_equal(8, result)
    end

    def test_to_lambda_works_with_block_arguments
      my_proc = proc { |x, &block| block ? block.call(x) : x }
      my_lambda = ProcHelpers.to_lambda(my_proc)

      result = my_lambda.call(5) { |n| n * 2 }

      assert_equal(10, result)

      result = my_lambda.call(5)

      assert_equal(5, result)
    end

    def test_to_lambda_in_node_input_transformer
      # Simulate node input transformer usage
      transformer = proc do |ctx|
        return { skip_execution: true, content: "skipped" } if ctx == :skip

        "normal: #{ctx}"
      end

      lambda_transformer = ProcHelpers.to_lambda(transformer)

      # Early return works
      result = lambda_transformer.call(:skip)

      assert_equal({ skip_execution: true, content: "skipped" }, result)

      # Normal flow works
      result = lambda_transformer.call("input")

      assert_equal("normal: input", result)
    end

    def test_to_lambda_multiple_returns
      # Proc with multiple return paths
      my_proc = proc do |x|
        return "negative" if x < 0
        return "zero" if x == 0
        return "positive" if x > 0

        "unreachable"
      end

      my_lambda = ProcHelpers.to_lambda(my_proc)

      assert_equal("negative", my_lambda.call(-1))
      assert_equal("zero", my_lambda.call(0))
      assert_equal("positive", my_lambda.call(1))
    end
  end
end
