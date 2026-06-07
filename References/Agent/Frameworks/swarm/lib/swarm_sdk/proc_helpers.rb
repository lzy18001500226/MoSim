# frozen_string_literal: true

module SwarmSDK
  # Helper methods for working with Procs and Lambdas
  #
  # Provides functionality to convert regular Proc objects into Lambdas to enable
  # safe use of return statements in DSL blocks (like input/output transformers).
  module ProcHelpers
    class << self
      # Convert a Proc to a Lambda
      #
      # The fundamental difference between a Proc and a Lambda is in how they handle
      # return statements. In a Proc, return exits the enclosing method (or program),
      # while in a Lambda, return only exits the lambda itself.
      #
      # This method converts a Proc to a Lambda by:
      # 1. Converting the proc to an unbound method via define_method
      # 2. Wrapping it in a lambda that binds and calls the method
      # 3. In the method, return exits the method (not the original scope)
      #
      # This allows users to write natural control flow with return statements:
      #
      # @example
      #   my_proc = proc { |x| return x * 2 if x > 0; 0 }
      #   my_lambda = ProcHelpers.to_lambda(my_proc)
      #   my_lambda.call(5)  # => 10 (return works safely!)
      #
      # @param proc [Proc] The proc to convert
      # @return [Proc] A lambda with the same behavior but safe return semantics
      def to_lambda(proc)
        return proc if proc.lambda?

        # Save local reference to proc so we can use it in module_exec/lambda scopes
        source_proc = proc

        # Convert proc to unbound method
        # define_method with a block converts the block to a method, where return
        # exits the method (not the original scope)
        unbound_method = Module.new.module_exec do
          instance_method(define_method(:_proc_call, &source_proc))
        end

        # Return lambda which binds our unbound method to correct receiver and calls it
        lambda do |*args, **kwargs, &block|
          # Bind method to the original proc's receiver (the context where it was defined)
          # This preserves access to instance variables, local variables via closure, etc.
          receiver = source_proc.binding.eval("self")
          unbound_method.bind(receiver).call(*args, **kwargs, &block)
        end
      end
    end
  end
end
