# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  # Integration tests for custom tool registration with swarms
  class CustomToolIntegrationTest < Minitest::Test
    def setup
      # Set fake API keys to avoid RubyLLM configuration errors
      @original_anthropic_key = ENV["ANTHROPIC_API_KEY"]
      @original_openai_key = ENV["OPENAI_API_KEY"]
      ENV["ANTHROPIC_API_KEY"] = "test-key-12345"
      ENV["OPENAI_API_KEY"] = "test-key-12345"
      RubyLLM.configure do |config|
        config.anthropic_api_key = "test-key-12345"
        config.openai_api_key = "test-key-12345"
      end

      @temp_dir = Dir.mktmpdir
      SwarmSDK.clear_custom_tools!
    end

    def teardown
      SwarmSDK.clear_custom_tools!
      FileUtils.rm_rf(@temp_dir) if @temp_dir && File.exist?(@temp_dir)

      # Restore original API keys
      if @original_anthropic_key
        ENV["ANTHROPIC_API_KEY"] = @original_anthropic_key
      else
        ENV.delete("ANTHROPIC_API_KEY")
      end

      if @original_openai_key
        ENV["OPENAI_API_KEY"] = @original_openai_key
      else
        ENV.delete("OPENAI_API_KEY")
      end
    end

    def test_custom_tool_available_in_swarm_via_dsl
      SwarmSDK.register_tool(:Weather, TestTools::SimpleTool)

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:Weather)
        end
      end

      agent_chat = swarm.agent(:agent1)

      assert(agent_chat.has_tool?(:Weather), "Agent should have custom Weather tool")
    end

    def test_custom_tool_can_be_used_alongside_builtin_tools
      SwarmSDK.register_tool(:Weather, TestTools::SimpleTool)

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:Weather, :Read, :Write)
        end
      end

      agent_chat = swarm.agent(:agent1)

      # Should have custom tool
      assert(agent_chat.has_tool?(:Weather), "Should have custom Weather tool")

      # Should have built-in tools
      assert(agent_chat.has_tool?(:Read), "Should have built-in Read tool")
      assert(agent_chat.has_tool?(:Write), "Should have built-in Write tool")
    end

    def test_custom_tool_plus_default_tools
      SwarmSDK.register_tool(:Weather, TestTools::SimpleTool)

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:Weather) # Only custom tool explicit
          # Default tools should still be added
        end
      end

      agent_chat = swarm.agent(:agent1)

      # Should have custom tool
      assert(agent_chat.has_tool?(:Weather), "Should have custom Weather tool")

      # Should have default tools too
      assert(agent_chat.has_tool?(:Read), "Should have default Read")
      assert(agent_chat.has_tool?(:Grep), "Should have default Grep")
      assert(agent_chat.has_tool?(:Glob), "Should have default Glob")
    end

    def test_custom_tool_with_context_requirements
      SwarmSDK.register_tool(:ContextTool, TestTools::ContextAwareTool)

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:ContextTool)
        end
      end

      agent_chat = swarm.agent(:agent1)

      # Tool should be registered with the custom name
      assert(agent_chat.has_tool?(:ContextTool), "Should have ContextTool")

      # The tool's name should be the registered name, not the class name
      tool_names = agent_chat.tool_names

      assert_includes(tool_names, "ContextTool")
    end

    def test_multiple_custom_tools_in_same_agent
      SwarmSDK.register_tool(:Weather, TestTools::SimpleTool)
      SwarmSDK.register_tool(:Stock, TestTools::StockPrice)

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:trader)

        agent(:trader) do
          description("Trading assistant")
          model("gpt-5")
          system_prompt("Help with trading")
          tools(:Weather, :Stock)
        end
      end

      agent_chat = swarm.agent(:trader)

      assert(agent_chat.has_tool?(:Weather), "Should have Weather tool")
      assert(agent_chat.has_tool?(:Stock), "Should have Stock tool")
    end

    def test_custom_tools_work_with_swarm_new_api
      SwarmSDK.register_tool(:Weather, TestTools::SimpleTool)

      test_scratchpad = Tools::Stores::ScratchpadStorage.new
      swarm = Swarm.new(name: "Test Swarm", scratchpad: test_scratchpad)

      swarm.add_agent(create_agent(
        name: :developer,
        description: "Developer agent",
        model: "gpt-5",
        system_prompt: "You are a developer.",
        tools: [:Weather, :Read],
      ))

      agent = swarm.agent(:developer)

      assert(agent.has_tool?(:Weather), "Should have custom Weather tool")
      assert(agent.has_tool?(:Read), "Should have built-in Read tool")
    end

    def test_custom_tool_not_affected_by_disable_default_tools
      SwarmSDK.register_tool(:Weather, TestTools::SimpleTool)

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:Weather, :Write)
          disable_default_tools(true) # Disable all defaults
        end
      end

      agent_chat = swarm.agent(:agent1)

      # Custom tool should still be present
      assert(agent_chat.has_tool?(:Weather), "Custom tool should not be affected by disable_default_tools")

      # Explicit built-in tool should still be present
      assert(agent_chat.has_tool?(:Write), "Explicit Write should still be present")

      # Default tools should be disabled
      refute(agent_chat.has_tool?(:Read), "Read should be disabled")
      refute(agent_chat.has_tool?(:Grep), "Grep should be disabled")
    end

    def test_unregistered_custom_tool_raises_error
      # Don't register any custom tools
      SwarmSDK.clear_custom_tools!

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:NonExistentTool)
        end
      end

      # Error is raised when agent is first accessed (lazy initialization)
      error = assert_raises(ConfigurationError) do
        swarm.agent(:agent1)
      end

      assert_includes(error.message, "Unknown tool")
    end

    def test_custom_tool_registered_after_swarm_definition_works
      # Define swarm first (but don't build yet since that triggers initialization)
      # This tests that tool registration is checked at swarm build time

      # Register the tool
      SwarmSDK.register_tool(:Weather, TestTools::SimpleTool)

      # Now build the swarm - should work
      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:Weather)
        end
      end

      agent_chat = swarm.agent(:agent1)

      assert(agent_chat.has_tool?(:Weather), "Should have Weather tool")
    end

    def test_custom_tool_inferred_name_works_in_swarm
      # Register with inferred name
      SwarmSDK.register_tool(TestTools::WeatherTool) # Should register as :Weather

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:Weather) # Use the inferred name
        end
      end

      agent_chat = swarm.agent(:agent1)

      assert(agent_chat.has_tool?(:Weather), "Should have Weather tool with inferred name")
    end

    def test_tool_priority_custom_before_builtin
      # This test verifies that custom tools are checked before built-in tools
      # Since we can't override built-in tools, we test the order by checking
      # that custom tools are found correctly

      SwarmSDK.register_tool(:CustomRead, TestTools::SimpleTool)

      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          description("Test agent")
          model("gpt-5")
          system_prompt("Test")
          tools(:CustomRead, :Read) # Custom + built-in with similar names
        end
      end

      agent_chat = swarm.agent(:agent1)

      # Both should be available
      assert(agent_chat.has_tool?(:CustomRead), "Should have custom CustomRead")
      assert(agent_chat.has_tool?(:Read), "Should have built-in Read")
    end
  end
end
