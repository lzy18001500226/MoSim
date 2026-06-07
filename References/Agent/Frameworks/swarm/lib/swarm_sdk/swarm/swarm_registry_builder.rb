# frozen_string_literal: true

module SwarmSDK
  class Swarm
    # Builder for swarm registry in DSL
    #
    # Supports registering external swarms for composable swarms pattern.
    #
    # @example
    #   swarms do
    #     register "code_review", file: "./swarms/code_review.rb"
    #     register "testing", file: "./swarms/testing.yml", keep_context: false
    #   end
    #
    # @example Inline swarm definition
    #   swarms do
    #     register "tester" do
    #       lead :tester
    #       agent :tester do
    #         model "gpt-4o-mini"
    #         system "You test code"
    #       end
    #     end
    #   end
    #
    class SwarmRegistryBuilder
      attr_reader :registrations

      def initialize
        @registrations = []
      end

      # Register a swarm from file, YAML string, or inline block
      #
      # @param name [String, Symbol] Registration name
      # @param file [String, nil] Path to swarm file (.rb or .yml)
      # @param yaml [String, nil] YAML content string
      # @param keep_context [Boolean] Whether to preserve conversation state (default: true)
      # @yield Optional block for inline swarm definition
      # @raise [ArgumentError] If neither file, yaml, nor block provided
      def register(name, file: nil, yaml: nil, keep_context: true, &block)
        # Validate that exactly one source is provided
        sources = [file, yaml, block].compact
        if sources.empty?
          raise ArgumentError, "register '#{name}' requires either file:, yaml:, or a block"
        elsif sources.size > 1
          raise ArgumentError, "register '#{name}' accepts only one of: file:, yaml:, or block (got #{sources.size})"
        end

        # Determine source type and store
        source = if file
          { type: :file, value: file }
        elsif yaml
          { type: :yaml, value: yaml }
        else
          { type: :block, value: block }
        end

        @registrations << {
          name: name.to_s,
          source: source,
          keep_context: keep_context,
        }
      end
    end
  end
end
