# frozen_string_literal: true

module Fixtures
  module SwarmConfigsInvalid
    class << self
      def invalid_version
        <<~YAML
          version: 2
          swarm:
            name: "Invalid"
            main: lead
            instances:
              lead:
                description: "Lead instance"
        YAML
      end

      def missing_main
        <<~YAML
          version: 1
          swarm:
            name: "No Main"
            instances:
              lead:
                description: "Lead instance"
        YAML
      end

      def invalid_connection
        <<~YAML
          version: 1
          swarm:
            name: "Bad Connection"
            main: lead
            instances:
              lead:
                description: "Lead instance"
                connections: [nonexistent]
        YAML
      end

      def missing_description
        <<~YAML
          version: 1
          swarm:
            name: "Missing Description"
            main: lead
            instances:
              lead:
                directory: .
        YAML
      end

      def tools_not_array
        <<~YAML
          version: 1
          swarm:
            name: "Invalid Tools"
            main: lead
            instances:
              lead:
                description: "Lead instance"
                tools: "Read"
        YAML
      end

      def allowed_tools_not_array
        <<~YAML
          version: 1
          swarm:
            name: "Invalid Allowed Tools"
            main: lead
            instances:
              lead:
                description: "Lead instance"
                allowed_tools: Edit
        YAML
      end

      def disallowed_tools_not_array
        <<~YAML
          version: 1
          swarm:
            name: "Invalid Disallowed Tools"
            main: lead
            instances:
              lead:
                description: "Lead instance"
                disallowed_tools: 123
        YAML
      end
    end
  end
end
