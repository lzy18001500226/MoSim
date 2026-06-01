# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class Configuration
    # Test Configuration parsing with custom delegation tool names
    #
    # These tests verify that YAML configurations with hash-format
    # delegates_to are parsed correctly and circular dependencies are detected.
    class ParserCustomDelegationTest < Minitest::Test
      def test_yaml_with_hash_format_delegates_to
        yaml = <<~YAML
          version: 2
          swarm:
            name: "Custom Delegation Test"
            lead: coordinator
            agents:
              coordinator:
                description: "Coordinator"
                model: gpt-5-mini
                system_prompt: "Coordinator"
                delegates_to:
                  frontend: "AskFrontend"
                  backend: "GetBackend"

              frontend:
                description: "Frontend"
                model: gpt-5-mini
                system_prompt: "Frontend"

              backend:
                description: "Backend"
                model: gpt-5-mini
                system_prompt: "Backend"
        YAML

        swarm = SwarmSDK.load(yaml)
        coordinator_def = swarm.agent_definition(:coordinator)

        # Verify hash format is parsed correctly
        assert_equal(2, coordinator_def.delegation_configs.length)

        frontend_config = coordinator_def.delegation_configs.find { |c| c[:agent] == :frontend }

        assert_equal("AskFrontend", frontend_config[:tool_name])

        backend_config = coordinator_def.delegation_configs.find { |c| c[:agent] == :backend }

        assert_equal("GetBackend", backend_config[:tool_name])
      end

      def test_yaml_with_array_format_backwards_compatible
        yaml = <<~YAML
          version: 2
          swarm:
            name: "Array Format Test"
            lead: coordinator
            agents:
              coordinator:
                description: "Coordinator"
                model: gpt-5-mini
                system_prompt: "Coordinator"
                delegates_to: [frontend, backend]

              frontend:
                description: "Frontend"
                model: gpt-5-mini
                system_prompt: "Frontend"

              backend:
                description: "Backend"
                model: gpt-5-mini
                system_prompt: "Backend"
        YAML

        swarm = SwarmSDK.load(yaml)
        coordinator_def = swarm.agent_definition(:coordinator)

        # Verify array format generates nil tool_names (auto-generate)
        assert_equal(2, coordinator_def.delegation_configs.length)

        frontend_config = coordinator_def.delegation_configs.find { |c| c[:agent] == :frontend }

        assert_nil(frontend_config[:tool_name])

        backend_config = coordinator_def.delegation_configs.find { |c| c[:agent] == :backend }

        assert_nil(backend_config[:tool_name])
      end

      def test_yaml_with_preserve_context_option
        yaml = <<~YAML
          version: 2
          swarm:
            name: "Preserve Context Test"
            lead: coordinator
            agents:
              coordinator:
                description: "Coordinator"
                model: gpt-5-mini
                system_prompt: "Coordinator"
                delegates_to:
                  - agent: backend
                    preserve_context: false
                  - agent: frontend
                    tool_name: AskFrontend
                  - frontend_readonly

              frontend:
                description: "Frontend"
                model: gpt-5-mini
                system_prompt: "Frontend"

              frontend_readonly:
                description: "Frontend readonly"
                model: gpt-5-mini
                system_prompt: "Frontend readonly"

              backend:
                description: "Backend"
                model: gpt-5-mini
                system_prompt: "Backend"
        YAML

        swarm = SwarmSDK.load(yaml)
        coordinator_def = swarm.agent_definition(:coordinator)

        # Verify preserve_context is parsed correctly
        assert_equal(3, coordinator_def.delegation_configs.length)

        backend_config = coordinator_def.delegation_configs.find { |c| c[:agent] == :backend }

        refute(backend_config[:preserve_context])
        assert_nil(backend_config[:tool_name])

        frontend_config = coordinator_def.delegation_configs.find { |c| c[:agent] == :frontend }

        assert(frontend_config[:preserve_context])
        assert_equal("AskFrontend", frontend_config[:tool_name])

        # Simple symbol format defaults to preserve_context: true
        readonly_config = coordinator_def.delegation_configs.find { |c| c[:agent] == :frontend_readonly }

        assert(readonly_config[:preserve_context])
        assert_nil(readonly_config[:tool_name])
      end

      def test_circular_dependency_detection_with_hash_format
        yaml = <<~YAML
          version: 2
          swarm:
            name: "Circular Test"
            lead: agent_a
            agents:
              agent_a:
                description: "Agent A"
                model: gpt-5-mini
                system_prompt: "A"
                delegates_to:
                  agent_b: "CustomB"

              agent_b:
                description: "Agent B"
                model: gpt-5-mini
                system_prompt: "B"
                delegates_to:
                  agent_a: "CustomA"
        YAML

        # CircularDependencyError is a subclass of ConfigurationError
        error = assert_raises(CircularDependencyError) do
          SwarmSDK.load(yaml)
        end

        assert_match(/circular dependency/i, error.message)
      end

      def test_circular_dependency_detection_with_mixed_formats
        yaml = <<~YAML
          version: 2
          swarm:
            name: "Mixed Circular Test"
            lead: agent_a
            agents:
              agent_a:
                description: "Agent A"
                model: gpt-5-mini
                system_prompt: "A"
                delegates_to: [agent_b, agent_c]

              agent_b:
                description: "Agent B"
                model: gpt-5-mini
                system_prompt: "B"
                delegates_to:
                  agent_c: "CustomC"

              agent_c:
                description: "Agent C"
                model: gpt-5-mini
                system_prompt: "C"
                delegates_to:
                  agent_a: "CustomA"
        YAML

        # CircularDependencyError is a subclass of ConfigurationError
        error = assert_raises(CircularDependencyError) do
          SwarmSDK.load(yaml)
        end

        assert_match(/circular dependency/i, error.message)
      end
    end
  end
end
