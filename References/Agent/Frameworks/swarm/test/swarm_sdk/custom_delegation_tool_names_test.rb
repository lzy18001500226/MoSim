# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  # Test custom delegation tool names feature
  #
  # This tests the ability to customize delegation tool names via:
  # - Ruby DSL: delegates_to frontend: "AskFrontend"
  # - YAML: delegates_to: { frontend: "AskFrontend" }
  class CustomDelegationToolNamesTest < Minitest::Test
    def test_definition_with_custom_tool_names_hash
      agent_def = Agent::Definition.new(
        :coordinator,
        {
          description: "Coordinator agent",
          system_prompt: "You coordinate tasks",
          directory: ".",
          delegates_to: {
            frontend: "AskFrontendTeam",
            backend: "GetBackendHelp",
          },
        },
      )

      # Verify delegation_configs stores full configuration
      assert_equal(2, agent_def.delegation_configs.length)

      frontend_config = agent_def.delegation_configs.find { |c| c[:agent] == :frontend }

      assert_equal(:frontend, frontend_config[:agent])
      assert_equal("AskFrontendTeam", frontend_config[:tool_name])

      backend_config = agent_def.delegation_configs.find { |c| c[:agent] == :backend }

      assert_equal(:backend, backend_config[:agent])
      assert_equal("GetBackendHelp", backend_config[:tool_name])
    end

    def test_definition_with_array_format_backwards_compatible
      agent_def = Agent::Definition.new(
        :coordinator,
        {
          description: "Coordinator agent",
          system_prompt: "You coordinate tasks",
          directory: ".",
          delegates_to: [:frontend, :backend],
        },
      )

      # Verify array format is parsed correctly
      assert_equal(2, agent_def.delegation_configs.length)

      frontend_config = agent_def.delegation_configs.find { |c| c[:agent] == :frontend }

      assert_equal(:frontend, frontend_config[:agent])
      assert_nil(frontend_config[:tool_name]) # Auto-generate

      backend_config = agent_def.delegation_configs.find { |c| c[:agent] == :backend }

      assert_equal(:backend, backend_config[:agent])
      assert_nil(backend_config[:tool_name]) # Auto-generate
    end

    def test_definition_with_mixed_custom_and_auto
      agent_def = Agent::Definition.new(
        :coordinator,
        {
          description: "Coordinator agent",
          system_prompt: "You coordinate tasks",
          directory: ".",
          delegates_to: {
            frontend: nil, # Auto-generate
            backend: "GetBackendHelp", # Custom
          },
        },
      )

      frontend_config = agent_def.delegation_configs.find { |c| c[:agent] == :frontend }

      assert_nil(frontend_config[:tool_name])

      backend_config = agent_def.delegation_configs.find { |c| c[:agent] == :backend }

      assert_equal("GetBackendHelp", backend_config[:tool_name])
    end

    def test_delegates_to_method_returns_agent_names_backwards_compatible
      agent_def = Agent::Definition.new(
        :coordinator,
        {
          description: "Coordinator agent",
          system_prompt: "You coordinate tasks",
          directory: ".",
          delegates_to: {
            frontend: "AskFrontendTeam",
            backend: "GetBackendHelp",
          },
        },
      )

      # delegates_to method should return array of symbols (backwards compatible)
      assert_equal([:frontend, :backend], agent_def.delegates_to)
      assert_kind_of(Array, agent_def.delegates_to)
      assert(agent_def.delegates_to.all? { |name| name.is_a?(Symbol) })
    end

    def test_serialization_preserves_custom_tool_names
      agent_def = Agent::Definition.new(
        :coordinator,
        {
          description: "Coordinator agent",
          system_prompt: "You coordinate tasks",
          directory: ".",
          delegates_to: {
            frontend: "AskFrontendTeam",
            backend: nil,
          },
        },
      )

      # Serialize to hash
      hash = agent_def.to_h

      # Verify full config is preserved
      assert_equal(
        [
          { agent: :frontend, tool_name: "AskFrontendTeam", preserve_context: true },
          { agent: :backend, tool_name: nil, preserve_context: true },
        ],
        hash[:delegates_to],
      )

      # Create new agent from serialized hash (simulating cloning)
      cloned_def = Agent::Definition.new(:coordinator_clone, hash)

      # Verify delegation configs are preserved
      assert_equal(2, cloned_def.delegation_configs.length)

      frontend_config = cloned_def.delegation_configs.find { |c| c[:agent] == :frontend }

      assert_equal("AskFrontendTeam", frontend_config[:tool_name])

      backend_config = cloned_def.delegation_configs.find { |c| c[:agent] == :backend }

      assert_nil(backend_config[:tool_name])
    end

    def test_dsl_with_hash_syntax
      builder = Agent::Builder.new(:coordinator)
      builder.description("Coordinator agent")
      builder.system_prompt("You coordinate tasks")
      builder.delegates_to(frontend: "AskFrontendTeam", backend: "GetBackendHelp")

      definition = builder.to_definition

      assert_equal(2, definition.delegation_configs.length)

      frontend_config = definition.delegation_configs.find { |c| c[:agent] == :frontend }

      assert_equal("AskFrontendTeam", frontend_config[:tool_name])

      backend_config = definition.delegation_configs.find { |c| c[:agent] == :backend }

      assert_equal("GetBackendHelp", backend_config[:tool_name])
    end

    def test_dsl_with_symbols_backwards_compatible
      builder = Agent::Builder.new(:coordinator)
      builder.description("Coordinator agent")
      builder.system_prompt("You coordinate tasks")
      builder.delegates_to(:frontend, :backend)

      definition = builder.to_definition

      assert_equal(2, definition.delegation_configs.length)

      frontend_config = definition.delegation_configs.find { |c| c[:agent] == :frontend }

      assert_nil(frontend_config[:tool_name])

      backend_config = definition.delegation_configs.find { |c| c[:agent] == :backend }

      assert_nil(backend_config[:tool_name])
    end

    def test_dsl_with_mixed_calls
      builder = Agent::Builder.new(:coordinator)
      builder.description("Coordinator agent")
      builder.system_prompt("You coordinate tasks")
      builder.delegates_to(:frontend, :qa)
      builder.delegates_to(backend: "GetBackendHelp")

      definition = builder.to_definition

      assert_equal(3, definition.delegation_configs.length)

      # Verify all three are present
      assert(definition.delegation_configs.any? { |c| c[:agent] == :frontend })
      assert(definition.delegation_configs.any? { |c| c[:agent] == :qa })
      assert(definition.delegation_configs.any? { |c| c[:agent] == :backend })

      # Verify custom tool name
      backend_config = definition.delegation_configs.find { |c| c[:agent] == :backend }

      assert_equal("GetBackendHelp", backend_config[:tool_name])
    end

    def test_error_on_invalid_format
      assert_raises(SwarmSDK::ConfigurationError) do
        Agent::Definition.new(
          :coordinator,
          {
            description: "Coordinator agent",
            system_prompt: "You coordinate tasks",
            directory: ".",
            delegates_to: 123, # Invalid: not an array or hash
          },
        )
      end
    end

    def test_string_keys_converted_to_symbols
      agent_def = Agent::Definition.new(
        :coordinator,
        {
          description: "Coordinator agent",
          system_prompt: "You coordinate tasks",
          directory: ".",
          delegates_to: {
            "frontend" => "AskFrontendTeam", # String key (from YAML)
            "backend" => nil,
          },
        },
      )

      # Should convert string keys to symbols
      assert_equal([:frontend, :backend], agent_def.delegates_to)

      frontend_config = agent_def.delegation_configs.find { |c| c[:agent] == :frontend }

      assert_equal(:frontend, frontend_config[:agent])
      assert_equal("AskFrontendTeam", frontend_config[:tool_name])
    end
  end
end
