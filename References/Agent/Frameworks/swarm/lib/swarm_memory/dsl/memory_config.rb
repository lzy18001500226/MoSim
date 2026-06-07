# frozen_string_literal: true

module SwarmMemory
  module DSL
    # Memory configuration for agents
    #
    # This class is injected into SwarmSDK when swarm_memory is required,
    # allowing agents to configure memory via the DSL.
    #
    # Supports custom adapters through options hash that gets passed through
    # to the adapter constructor.
    #
    # @example Filesystem adapter
    #   memory do
    #     adapter :filesystem
    #     directory ".swarm/memory"
    #   end
    #
    # @example Custom adapter
    #   memory do
    #     adapter :activerecord
    #     option :namespace, "my_agent"
    #     option :table_name, "memory_entries"
    #   end
    class MemoryConfig
      attr_reader :adapter_type, :adapter_options

      def initialize
        @adapter_type = :filesystem # Default adapter
        @adapter_options = {} # Options passed to adapter constructor
        @mode = :read_write # Default mode
      end

      # DSL method to set/get adapter type
      #
      # @param value [Symbol, nil] Adapter type
      # @return [Symbol] Current adapter
      def adapter(value = nil)
        return @adapter_type if value.nil?

        @adapter_type = value.to_sym
      end

      # DSL method to set adapter option (generic)
      #
      # This allows passing any option to the adapter constructor.
      #
      # @param key [Symbol] Option key
      # @param value [Object] Option value
      #
      # @example
      #   option :namespace, "my_agent"
      #   option :connection_pool_size, 5
      def option(key, value)
        @adapter_options[key.to_sym] = value
      end

      # DSL method to set/get directory (convenience for filesystem adapter)
      #
      # Equivalent to: option :directory, value
      #
      # @param value [String, nil] Memory directory path
      # @return [String] Current directory
      def directory(value = nil)
        if value.nil?
          @adapter_options[:directory]
        else
          @adapter_options[:directory] = value
        end
      end

      # DSL method to set/get mode
      #
      # Modes:
      # - :read_write (default) - Read + Write + Edit, balanced for learning and retrieval
      # - :read_only - Read-only, optimized for Q&A
      # - :full_access - All tools including Delete and Defrag, optimized for knowledge management
      #
      # @param value [Symbol, nil] Memory mode
      # @return [Symbol] Current mode
      def mode(value = nil)
        return @mode if value.nil?

        @mode = value.to_sym
      end

      # DSL method to set/get semantic weight for hybrid search
      #
      # Controls how much semantic (embedding) similarity affects search results.
      # Default is 0.5 (50%). Set to 1.0 for pure semantic search.
      #
      # @param value [Float, nil] Weight between 0.0 and 1.0
      # @return [Float, nil] Current semantic weight
      #
      # @example Pure semantic search (no keyword penalty)
      #   semantic_weight 1.0
      #   keyword_weight 0.0
      def semantic_weight(value = nil)
        if value.nil?
          @adapter_options[:semantic_weight]
        else
          @adapter_options[:semantic_weight] = value.to_f
        end
      end

      # DSL method to set/get keyword weight for hybrid search
      #
      # Controls how much keyword (tag) matching affects search results.
      # Default is 0.5 (50%). Set to 0.0 to disable keyword matching.
      #
      # @param value [Float, nil] Weight between 0.0 and 1.0
      # @return [Float, nil] Current keyword weight
      #
      # @example Disable keyword matching
      #   keyword_weight 0.0
      def keyword_weight(value = nil)
        if value.nil?
          @adapter_options[:keyword_weight]
        else
          @adapter_options[:keyword_weight] = value.to_f
        end
      end

      # Check if memory is enabled
      #
      # @return [Boolean] True if adapter is configured with required options
      def enabled?
        case @adapter_type
        when :filesystem
          !@adapter_options[:directory].nil?
        else
          # For custom adapters, assume enabled if adapter is set
          # Custom adapter will validate its own requirements
          true
        end
      end

      # Convert config to hash (for SDK plugin)
      #
      # @return [Hash] Configuration as hash
      def to_h
        {
          adapter: @adapter_type,
          mode: @mode,
          loadskill_preserve_delegation: @loadskill_preserve_delegation,
          **@adapter_options,
        }
      end
    end
  end
end
