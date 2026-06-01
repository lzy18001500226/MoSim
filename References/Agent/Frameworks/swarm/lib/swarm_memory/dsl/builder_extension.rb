# frozen_string_literal: true

module SwarmMemory
  module DSL
    # Extension module that injects memory DSL into SwarmSDK::Agent::Builder
    #
    # This module is included into Agent::Builder when swarm_memory is required,
    # adding the `memory` configuration method.
    module BuilderExtension
      # Configure persistent memory for this agent
      #
      # @example Read-write mode (default) - Learn and retrieve
      #   memory do
      #     directory ".swarm/agent-memory"
      #   end
      #
      # @example Read-only mode - Q&A without learning
      #   memory do
      #     directory "team-knowledge/"
      #     mode :read_only
      #   end
      #
      # @example Full access mode - Knowledge management with Delete and Defrag
      #   memory do
      #     directory "team-knowledge/"
      #     mode :full_access
      #   end
      def memory(&block)
        @memory_config = SwarmMemory::DSL::MemoryConfig.new
        @memory_config.instance_eval(&block) if block_given?
        @memory_config
      end
    end
  end
end

# Inject memory DSL into Agent::Builder when this file is loaded
if defined?(SwarmSDK::Agent::Builder)
  SwarmSDK::Agent::Builder.include(SwarmMemory::DSL::BuilderExtension)
end
