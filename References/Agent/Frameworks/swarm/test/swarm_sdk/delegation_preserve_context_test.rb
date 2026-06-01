# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  # Tests for preserve_context option in delegation
  class DelegationPreserveContextTest < Minitest::Test
    def setup
      @original_api_key = ENV["OPENAI_API_KEY"]
      ENV["OPENAI_API_KEY"] = "test-key-12345"
      RubyLLM.configure { |config| config.openai_api_key = "test-key-12345" }

      @test_scratchpad = Tools::Stores::ScratchpadStorage.new
    end

    def teardown
      ENV["OPENAI_API_KEY"] = @original_api_key
      RubyLLM.configure { |config| config.openai_api_key = @original_api_key }
    end

    # Test: Default preserve_context is true
    def test_default_preserve_context_is_true
      swarm = Swarm.new(name: "Test Swarm", scratchpad: @test_scratchpad)

      swarm.add_agent(create_agent(
        name: :backend,
        description: "Backend developer",
        model: "gpt-4o-mini",
        directory: ".",
      ))

      swarm.add_agent(create_agent(
        name: :frontend,
        description: "Frontend developer",
        model: "gpt-4o-mini",
        delegates_to: [:backend],
        directory: ".",
      ))

      swarm.lead = :frontend

      # Trigger initialization
      frontend_agent = swarm.agent(:frontend)

      # Get the delegation tool
      delegation_tool = frontend_agent.tools[:WorkWithBackend]

      assert(delegation_tool, "Should have WorkWithBackend delegation tool")

      # Verify preserve_context defaults to true
      assert(
        delegation_tool.preserve_context,
        "preserve_context should default to true",
      )
    end

    # Test: Can set preserve_context to false via delegation config hash
    def test_preserve_context_false_via_config_hash
      swarm = Swarm.new(name: "Test Swarm", scratchpad: @test_scratchpad)

      swarm.add_agent(create_agent(
        name: :backend,
        description: "Backend developer",
        model: "gpt-4o-mini",
        directory: ".",
      ))

      swarm.add_agent(create_agent(
        name: :frontend,
        description: "Frontend developer",
        model: "gpt-4o-mini",
        delegates_to: [{ agent: :backend, preserve_context: false }],
        directory: ".",
      ))

      swarm.lead = :frontend

      # Trigger initialization
      frontend_agent = swarm.agent(:frontend)

      # Get the delegation tool
      delegation_tool = frontend_agent.tools[:WorkWithBackend]

      assert(delegation_tool, "Should have WorkWithBackend delegation tool")

      # Verify preserve_context is false
      refute(
        delegation_tool.preserve_context,
        "preserve_context should be false when explicitly set",
      )
    end

    # Test: Can set custom tool_name and preserve_context together
    def test_custom_tool_name_with_preserve_context
      swarm = Swarm.new(name: "Test Swarm", scratchpad: @test_scratchpad)

      swarm.add_agent(create_agent(
        name: :backend,
        description: "Backend developer",
        model: "gpt-4o-mini",
        directory: ".",
      ))

      swarm.add_agent(create_agent(
        name: :frontend,
        description: "Frontend developer",
        model: "gpt-4o-mini",
        delegates_to: [{ agent: :backend, tool_name: "AskBackend", preserve_context: false }],
        directory: ".",
      ))

      swarm.lead = :frontend

      # Trigger initialization
      frontend_agent = swarm.agent(:frontend)

      # Get the delegation tool using custom name
      delegation_tool = frontend_agent.tools[:AskBackend]

      assert(delegation_tool, "Should have AskBackend delegation tool with custom name")

      # Verify both options are respected
      assert_equal("AskBackend", delegation_tool.tool_name)
      refute(
        delegation_tool.preserve_context,
        "preserve_context should be false",
      )
    end

    # Test: Mixed delegates_to with different preserve_context settings
    def test_mixed_preserve_context_settings
      swarm = Swarm.new(name: "Test Swarm", scratchpad: @test_scratchpad)

      swarm.add_agent(create_agent(
        name: :database,
        description: "Database agent",
        model: "gpt-4o-mini",
        directory: ".",
      ))

      swarm.add_agent(create_agent(
        name: :cache,
        description: "Cache agent",
        model: "gpt-4o-mini",
        directory: ".",
      ))

      swarm.add_agent(create_agent(
        name: :backend,
        description: "Backend developer",
        model: "gpt-4o-mini",
        delegates_to: [
          :database, # preserve_context: true (default)
          { agent: :cache, preserve_context: false },
        ],
        directory: ".",
      ))

      swarm.lead = :backend

      # Trigger initialization
      backend_agent = swarm.agent(:backend)

      # Get both delegation tools
      database_tool = backend_agent.tools[:WorkWithDatabase]
      cache_tool = backend_agent.tools[:WorkWithCache]

      assert(database_tool, "Should have WorkWithDatabase delegation tool")
      assert(cache_tool, "Should have WorkWithCache delegation tool")

      # Verify different preserve_context settings
      assert(
        database_tool.preserve_context,
        "database delegation should preserve context by default",
      )
      refute(
        cache_tool.preserve_context,
        "cache delegation should not preserve context when explicitly set",
      )
    end

    # Test: preserve_context is stored in tool registry metadata
    def test_preserve_context_in_tool_registry_metadata
      swarm = Swarm.new(name: "Test Swarm", scratchpad: @test_scratchpad)

      swarm.add_agent(create_agent(
        name: :backend,
        description: "Backend developer",
        model: "gpt-4o-mini",
        directory: ".",
      ))

      swarm.add_agent(create_agent(
        name: :frontend,
        description: "Frontend developer",
        model: "gpt-4o-mini",
        delegates_to: [{ agent: :backend, preserve_context: false }],
        directory: ".",
      ))

      swarm.lead = :frontend

      # Trigger initialization
      frontend_agent = swarm.agent(:frontend)

      # Get tool entry from registry using the correct API
      registry = frontend_agent.tool_registry
      tool_entry = registry.get("WorkWithBackend")

      assert(tool_entry, "Should find WorkWithBackend in registry")
      refute(
        tool_entry.metadata[:preserve_context],
        "preserve_context should be stored in metadata",
      )
    end

    # Test: DSL builder supports preserve_context
    def test_dsl_builder_preserve_context
      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:frontend)

        agent(:backend) do
          model("gpt-4o-mini")
          description("Backend developer")
        end

        agent(:frontend) do
          model("gpt-4o-mini")
          description("Frontend developer")
          delegates_to({ agent: :backend, preserve_context: false })
        end
      end

      frontend_agent = swarm.agent(:frontend)
      delegation_tool = frontend_agent.tools[:WorkWithBackend]

      assert(delegation_tool, "Should have WorkWithBackend delegation tool")
      refute(
        delegation_tool.preserve_context,
        "DSL should support preserve_context: false",
      )
    end

    # Test: Definition parse_delegation_config handles preserve_context
    def test_definition_parse_delegation_config_preserve_context
      definition = Agent::Definition.new(:test, {
        description: "Test agent",
        model: "gpt-4o-mini",
        delegates_to: [
          :agent_a,
          { agent: :agent_b, preserve_context: false },
          { agent: :agent_c, tool_name: "CustomTool", preserve_context: true },
        ],
        directory: ".",
      })

      configs = definition.delegation_configs

      assert_equal(3, configs.size)

      # First: simple symbol (defaults to preserve_context: true)
      assert_equal(:agent_a, configs[0][:agent])
      assert(configs[0][:preserve_context])

      # Second: explicit preserve_context: false
      assert_equal(:agent_b, configs[1][:agent])
      refute(configs[1][:preserve_context])

      # Third: with custom tool_name and explicit preserve_context: true
      assert_equal(:agent_c, configs[2][:agent])
      assert_equal("CustomTool", configs[2][:tool_name])
      assert(configs[2][:preserve_context])
    end

    # Test: Builder delegates_to handles full config hash
    # Tests Builder behavior through the Definition it produces (public API)
    def test_builder_delegates_to_full_config_hash
      builder = Agent::Builder.new(:test)
      builder.model("gpt-4o-mini")
      builder.description("Test agent")
      builder.delegates_to(
        :agent_a,
        { agent: :agent_b, tool_name: "CustomB", preserve_context: false },
      )

      # Convert to definition and verify through public API
      definition = builder.to_definition

      configs = definition.delegation_configs

      assert_equal(2, configs.size)

      # First: simple symbol
      assert_equal(:agent_a, configs[0][:agent])
      assert_nil(configs[0][:tool_name])
      assert(configs[0][:preserve_context])

      # Second: full config hash
      assert_equal(:agent_b, configs[1][:agent])
      assert_equal("CustomB", configs[1][:tool_name])
      refute(configs[1][:preserve_context])
    end

    private

    def create_agent(name:, **config)
      config[:description] ||= "Test agent #{name}"
      config[:model] ||= "gpt-5"
      config[:system_prompt] ||= "Test"
      config[:directory] ||= "."
      config[:streaming] = false unless config.key?(:streaming)

      Agent::Definition.new(name, config)
    end
  end
end
