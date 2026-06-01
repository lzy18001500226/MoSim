# frozen_string_literal: true

module Fixtures
  module SwarmConfigs
    class << self
      def minimal
        <<~YAML
          version: 1
          swarm:
            name: "Minimal Swarm"
            main: lead
            instances:
              lead:
                description: "Lead instance for minimal configuration"
        YAML
      end

      def with_connections
        <<~YAML
          version: 1
          swarm:
            name: "Connected Swarm"
            main: lead
            instances:
              lead:
                description: "Lead instance connecting to backend and frontend"
                connections: [backend, frontend]
              backend:
                description: "Backend service instance"
                directory: ./backend
              frontend:
                description: "Frontend service instance"
                directory: ./frontend
        YAML
      end

      def with_tools
        <<~YAML
          version: 1
          swarm:
            name: "Tooled Swarm"
            main: lead
            instances:
              lead:
                description: "Instance with various tool access"
                tools: [Read, Edit, Bash, Grep]
        YAML
      end

      def with_tool_patterns
        <<~YAML
          version: 1
          swarm:
            name: "Pattern Swarm"
            main: lead
            instances:
              lead:
                description: "Instance with pattern-based tool restrictions"
                tools:
                  - Read
                  - Edit
                  - Bash
                  - Grep
        YAML
      end

      def with_mcps
        <<~YAML
          version: 1
          swarm:
            name: "MCP Swarm"
            main: lead
            instances:
              lead:
                description: "Instance with multiple MCP server configurations"
                mcps:
                  - name: "stdio_server"
                    type: "stdio"
                    command: "test-server"
                    args: ["--port", "3000"]
                  - name: "sse_server"
                    type: "sse"
                    url: "http://localhost:8080/events"
        YAML
      end

      def full_featured
        <<~YAML
          version: 1
          swarm:
            name: "Full Featured Swarm"
            main: lead
            instances:
              lead:
                description: "Lead developer coordinating the entire team"
                directory: ./lead
                model: opus
                connections: [backend, frontend, tester]
                tools: [Read, Edit, Bash, Grep]
                prompt: "You are the lead developer coordinating the team"
                mcps:
                  - name: "monitor"
                    type: "stdio"
                    command: "monitor-server"
              backend:
                description: "Backend developer handling API and server logic"
                directory: ./backend
                model: sonnet
                connections: [database]
                tools: [Bash, Edit, Read]
                prompt: "You handle API and backend logic"
              frontend:
                description: "Frontend developer building user interfaces"
                directory: ./frontend
                model: claude-3-5-haiku-20241022
                tools: [Edit, Bash, Read]
                prompt: "You build user interfaces"
              database:
                description: "Database specialist managing data operations"
                directory: ./db
                tools: [Bash]
              tester:
                description: "Test engineer ensuring code quality"
                directory: ./tests
                model: sonnet
                tools: [Bash, Read, Edit]
                mcps:
                  - name: "test_reporter"
                    type: "sse"
                    url: "http://localhost:9000/test-results"
        YAML
      end

      def circular_connections
        <<~YAML
          version: 1
          swarm:
            name: "Circular"
            main: a
            instances:
              a:
                description: "Instance A in circular connection"
                connections: [b]
              b:
                description: "Instance B in circular connection"
                connections: [c]
              c:
                description: "Instance C in circular connection"
                connections: [a]
        YAML
      end
    end
  end
end
