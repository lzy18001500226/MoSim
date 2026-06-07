# frozen_string_literal: true

module SwarmSDK
  # Shared utility methods for SwarmSDK
  module Utils
    class << self
      # Recursively convert all hash keys to symbols
      #
      # Handles nested hashes and arrays containing hashes.
      #
      # @param obj [Object] Object to symbolize (Hash, Array, or other)
      # @return [Object] Object with symbolized keys (if applicable)
      #
      # @example
      #   Utils.symbolize_keys({ "name" => "test", "config" => { "key" => "value" } })
      #   # => { name: "test", config: { key: "value" } }
      def symbolize_keys(obj)
        case obj
        when Hash
          obj.transform_keys(&:to_sym).transform_values { |v| symbolize_keys(v) }
        when Array
          obj.map { |item| symbolize_keys(item) }
        else
          obj
        end
      end

      # Recursively convert all hash keys to strings
      #
      # Handles nested hashes and arrays containing hashes.
      #
      # @param obj [Object] Object to stringify (Hash, Array, or other)
      # @return [Object] Object with stringified keys (if applicable)
      #
      # @example
      #   Utils.stringify_keys({ name: "test", config: { key: "value" } })
      #   # => { "name" => "test", "config" => { "key" => "value" } }
      def stringify_keys(obj)
        case obj
        when Hash
          obj.transform_keys(&:to_s).transform_values { |v| stringify_keys(v) }
        when Array
          obj.map { |item| stringify_keys(item) }
        else
          obj
        end
      end

      # Convert hash to YAML string
      #
      # Converts a Ruby hash to a YAML string. Useful for creating inline
      # swarm definitions from hash configurations.
      #
      # @param hash [Hash] Hash to convert
      # @return [String] YAML string representation
      #
      # @example
      #   config = { version: 2, swarm: { name: "Test" } }
      #   Utils.hash_to_yaml(config)
      #   # => "---\nversion: 2\nswarm:\n  name: Test\n"
      def hash_to_yaml(hash)
        # Convert symbols to strings for valid YAML
        stringified = stringify_keys(hash)
        stringified.to_yaml
      end
    end
  end
end
