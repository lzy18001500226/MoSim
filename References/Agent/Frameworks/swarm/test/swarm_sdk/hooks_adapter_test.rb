# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class HooksAdapterTest < Minitest::Test
    def setup
      @original_api_key = ENV["OPENAI_API_KEY"]
      ENV["OPENAI_API_KEY"] = "test-key-12345"
      RubyLLM.configure { |config| config.openai_api_key = "test-key-12345" }
    end

    def teardown
      ENV["OPENAI_API_KEY"] = @original_api_key
      RubyLLM.configure { |config| config.openai_api_key = @original_api_key }
    end

    def test_apply_agent_hooks_adds_hooks_to_agent
      swarm = Swarm.new(name: "Test")
      swarm.add_agent(create_agent(
        name: :test,
        description: "Test",
        model: "gpt-5",
        system_prompt: "Test",
      ))

      # Access agent to trigger lazy initialization
      agent = swarm.agent(:test)

      hooks_config = {
        pre_tool_use: [
          {
            "matcher" => "Write",
            "type" => "command",
            "command" => "echo test",
            "timeout" => 5,
          },
        ],
      }

      # Apply hooks using public API
      SwarmSDK::Hooks::Adapter.apply_agent_hooks(agent, :test, hooks_config, "Test Swarm")

      # Verify hooks were registered (they exist in the agent's hook system)
      # We can't easily inspect the hooks directly, but we can verify no errors were raised
      assert_instance_of(Agent::Chat, agent)
    end

    def test_swarm_level_events_constant
      assert_equal([:swarm_start, :swarm_stop], SwarmSDK::Hooks::Adapter::SWARM_LEVEL_EVENTS)
    end

    def test_agent_level_events_constant
      expected = [
        :pre_tool_use,
        :post_tool_use,
        :user_prompt,
        :agent_step,
        :agent_stop,
        :first_message,
        :pre_delegation,
        :post_delegation,
        :context_warning,
      ]

      assert_equal(expected, SwarmSDK::Hooks::Adapter::AGENT_LEVEL_EVENTS)
    end

    def test_apply_hooks_with_swarm_hooks
      config = create_mock_config(swarm_hooks: {
        swarm_start: [{
          "command" => "echo 'swarm starting'",
          "timeout" => 10,
        }],
      })

      swarm = Swarm.new(name: "Test")

      # Should not raise error
      SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
    end

    def test_apply_hooks_with_all_agents_hooks
      config = create_mock_config(all_agents_hooks: {
        pre_tool_use: [{
          "matcher" => "Write",
          "command" => "echo 'validating'",
          "timeout" => 5,
        }],
      })

      swarm = Swarm.new(name: "Test")

      # Should not raise error
      SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
    end

    def test_apply_hooks_with_no_hooks
      config = create_mock_config(swarm_hooks: nil, all_agents_hooks: nil)
      swarm = Swarm.new(name: "Test")

      # Should not raise error with nil hooks
      SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
    end

    def test_apply_hooks_with_empty_hooks
      config = create_mock_config(swarm_hooks: {}, all_agents_hooks: {})
      swarm = Swarm.new(name: "Test")

      # Should not raise error with empty hooks
      SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
    end

    def test_apply_hooks_with_invalid_swarm_event
      # Test that invalid swarm-level events raise error through public API
      config = create_mock_config(swarm_hooks: {
        pre_tool_use: [{
          "command" => "echo 'invalid'",
        }],
      })

      swarm = Swarm.new(name: "Test")

      error = assert_raises(SwarmSDK::ConfigurationError) do
        SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
      end

      assert_match(/Invalid swarm-level hook event/, error.message)
    end

    def test_apply_hooks_with_invalid_agent_event
      # Test that invalid agent-level events raise error through public API
      config = create_mock_config(all_agents_hooks: {
        swarm_start: [{
          "command" => "echo 'invalid'",
        }],
      })

      swarm = Swarm.new(name: "Test")

      error = assert_raises(SwarmSDK::ConfigurationError) do
        SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
      end

      assert_match(/Invalid agent-level hook event/, error.message)
    end

    def test_apply_agent_hooks_with_invalid_event
      swarm = Swarm.new(name: "Test")
      swarm.add_agent(create_agent(
        name: :test,
        description: "Test",
        model: "gpt-4o",
        system_prompt: "Test",
      ))

      agent = swarm.agent(:test)

      # Invalid event at agent level
      hooks_config = {
        swarm_start: [{
          "command" => "echo 'invalid'",
        }],
      }

      error = assert_raises(SwarmSDK::ConfigurationError) do
        SwarmSDK::Hooks::Adapter.apply_agent_hooks(agent, :test, hooks_config, "Test")
      end

      assert_match(/Invalid agent-level hook event/, error.message)
    end

    def test_apply_agent_hooks_with_symbol_keys
      swarm = Swarm.new(name: "Test")
      swarm.add_agent(create_agent(
        name: :test,
        description: "Test",
        model: "gpt-4o",
        system_prompt: "Test",
      ))

      agent = swarm.agent(:test)

      # Symbol keys (from symbolized YAML)
      hooks_config = {
        pre_tool_use: [{
          command: "echo 'test'",
          timeout: 10,
        }],
      }

      # Should not raise error
      SwarmSDK::Hooks::Adapter.apply_agent_hooks(agent, :test, hooks_config, "Test")
    end

    def test_apply_agent_hooks_with_string_keys
      swarm = Swarm.new(name: "Test")
      swarm.add_agent(create_agent(
        name: :test,
        description: "Test",
        model: "gpt-4o",
        system_prompt: "Test",
      ))

      agent = swarm.agent(:test)

      # String keys (from raw YAML)
      hooks_config = {
        pre_tool_use: [{
          "command" => "echo 'test'",
          "timeout" => 10,
        }],
      }

      # Should not raise error
      SwarmSDK::Hooks::Adapter.apply_agent_hooks(agent, :test, hooks_config, "Test")
    end

    def test_apply_agent_hooks_with_matcher
      swarm = Swarm.new(name: "Test")
      swarm.add_agent(create_agent(
        name: :test,
        description: "Test",
        model: "gpt-4o",
        system_prompt: "Test",
      ))

      agent = swarm.agent(:test)

      hooks_config = {
        pre_tool_use: [{
          "matcher" => "Write|Edit",
          "command" => "echo 'validating'",
          "timeout" => 5,
        }],
      }

      # Should not raise error
      SwarmSDK::Hooks::Adapter.apply_agent_hooks(agent, :test, hooks_config, "Test")
    end

    def test_apply_swarm_hooks_with_valid_events
      # Test all valid swarm events through public API
      config = create_mock_config(swarm_hooks: {
        swarm_start: [{
          "command" => "echo 'start'",
        }],
        swarm_stop: [{
          "command" => "echo 'stop'",
        }],
      })

      swarm = Swarm.new(name: "Test")

      # Should not raise error
      SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
    end

    def test_apply_all_agents_hooks_with_valid_events
      # Test various valid agent events through public API
      config = create_mock_config(all_agents_hooks: {
        pre_tool_use: [{ "command" => "echo 'pre'" }],
        post_tool_use: [{ "command" => "echo 'post'" }],
        user_prompt: [{ "command" => "echo 'prompt'" }],
        agent_step: [{ "command" => "echo 'step'" }],
        agent_stop: [{ "command" => "echo 'stop'" }],
        first_message: [{ "command" => "echo 'first'" }],
        pre_delegation: [{ "command" => "echo 'pre_deleg'" }],
        post_delegation: [{ "command" => "echo 'post_deleg'" }],
        context_warning: [{ "command" => "echo 'warning'" }],
      })

      swarm = Swarm.new(name: "Test")

      # Should not raise error
      SwarmSDK::Hooks::Adapter.apply_hooks(swarm, config)
    end

    private

    def create_mock_config(swarm_hooks: nil, all_agents_hooks: nil)
      config = Minitest::Mock.new
      # May be called multiple times: for nil check and iteration
      config.expect(:swarm_hooks, swarm_hooks)
      config.expect(:swarm_hooks, swarm_hooks) if swarm_hooks
      config.expect(:all_agents_hooks, all_agents_hooks)
      config.expect(:all_agents_hooks, all_agents_hooks) if all_agents_hooks
      config
    end
  end
end
