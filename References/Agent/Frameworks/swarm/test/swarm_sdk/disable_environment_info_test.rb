# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class DisableEnvironmentInfoTest < Minitest::Test
    def setup
      ENV["OPENAI_API_KEY"] = "test-key"
      RubyLLM.configure { |c| c.openai_api_key = "test-key" }
    end

    # ========== Agent::Definition Tests ==========

    def test_defaults_to_false
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: "Custom prompt",
      )

      refute(agent_def.disable_environment_info)
    end

    def test_default_includes_environment_info
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: "Custom prompt",
      )

      assert_includes(agent_def.system_prompt, "Today's date")
      assert_includes(agent_def.system_prompt, "Current Environment")
      assert_includes(agent_def.system_prompt, "Custom prompt")
    end

    def test_true_omits_environment_info_non_coding_agent
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: "Custom prompt",
        disable_environment_info: true,
      )

      assert(agent_def.disable_environment_info)
      refute_includes(agent_def.system_prompt, "Today's date")
      refute_includes(agent_def.system_prompt, "Current Environment")
      assert_equal("Custom prompt", agent_def.system_prompt)
    end

    def test_true_omits_environment_info_coding_agent
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: "Custom prompt",
        coding_agent: true,
        disable_environment_info: true,
      )

      assert(agent_def.disable_environment_info)
      refute_includes(agent_def.system_prompt, "Today's date")
      refute_includes(agent_def.system_prompt, "Environment information")
      refute_match(/Working directory:/, agent_def.system_prompt)
      assert_includes(agent_def.system_prompt, "Custom prompt")
    end

    def test_false_preserves_environment_info_coding_agent
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: "Custom prompt",
        coding_agent: true,
        disable_environment_info: false,
      )

      refute(agent_def.disable_environment_info)
      assert_match(/Working directory:/, agent_def.system_prompt)
      assert_includes(agent_def.system_prompt, "Custom prompt")
    end

    def test_true_with_nil_custom_prompt_non_coding
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: nil,
        disable_environment_info: true,
      )

      assert_equal("", agent_def.system_prompt)
    end

    def test_to_h_serializes_disable_environment_info_true
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: "Custom",
        disable_environment_info: true,
      )

      hash = agent_def.to_h

      assert(hash[:disable_environment_info])
    end

    def test_to_h_serializes_disable_environment_info_false
      agent_def = Agent::Definition.new(
        :test_agent,
        description: "Test agent",
        model: "gpt-4",
        system_prompt: "Custom",
        disable_environment_info: false,
      )

      hash = agent_def.to_h

      refute(hash[:disable_environment_info])
    end

    # ========== Agent::Builder Tests ==========

    def test_builder_dsl_method
      builder = Agent::Builder.new(:test)
      builder.model("gpt-4")
      builder.description("Test")
      builder.system_prompt("Custom")
      builder.disable_environment_info(true)

      definition = builder.to_definition

      assert(definition.disable_environment_info)
      refute_includes(definition.system_prompt, "Today's date")
    end

    def test_builder_set_predicate_false_by_default
      builder = Agent::Builder.new(:test)

      refute_predicate(builder, :disable_environment_info_set?)
    end

    def test_builder_set_predicate_true_when_set_to_true
      builder = Agent::Builder.new(:test)
      builder.disable_environment_info(true)

      assert_predicate(builder, :disable_environment_info_set?)
    end

    def test_builder_set_predicate_true_when_set_to_false
      builder = Agent::Builder.new(:test)
      builder.disable_environment_info(false)

      assert_predicate(builder, :disable_environment_info_set?)
    end

    def test_builder_to_definition_includes_when_set
      builder = Agent::Builder.new(:test)
      builder.model("gpt-4")
      builder.description("Test")
      builder.system_prompt("Custom")
      builder.disable_environment_info(true)

      definition = builder.to_definition

      assert(definition.disable_environment_info)
    end

    def test_builder_to_definition_defaults_when_not_set
      builder = Agent::Builder.new(:test)
      builder.model("gpt-4")
      builder.description("Test")
      builder.system_prompt("Custom")

      definition = builder.to_definition

      refute(definition.disable_environment_info)
    end

    # ========== Ruby DSL Integration Tests ==========

    def test_ruby_dsl_disable_environment_info_true
      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          model("gpt-4")
          description("Agent 1")
          system_prompt("My custom prompt")
          disable_environment_info(true)
        end
      end

      agent_def = swarm.agent_definition(:agent1)

      assert(agent_def.disable_environment_info)
      refute_includes(agent_def.system_prompt, "Today's date")
      assert_equal("My custom prompt", agent_def.system_prompt)
    end

    def test_ruby_dsl_disable_environment_info_false
      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        agent(:agent1) do
          model("gpt-4")
          description("Agent 1")
          system_prompt("My custom prompt")
          disable_environment_info(false)
        end
      end

      agent_def = swarm.agent_definition(:agent1)

      refute(agent_def.disable_environment_info)
      assert_includes(agent_def.system_prompt, "Today's date")
      assert_includes(agent_def.system_prompt, "My custom prompt")
    end

    # ========== YAML Configuration Tests ==========

    def test_yaml_config_with_disable_environment_info_true
      yaml_content = <<~YAML
        version: 2
        swarm:
          name: "Test Swarm"
          lead: agent1
          agents:
            agent1:
              description: "Agent 1"
              model: gpt-4
              disable_environment_info: true
              system_prompt: "Custom only"
      YAML

      with_temp_config(yaml_content) do |config_path|
        swarm = Configuration.load_file(config_path).to_swarm

        agent_def = swarm.agent_definitions[:agent1]

        assert(agent_def.disable_environment_info)
        refute_includes(agent_def.system_prompt, "Today's date")
      end
    end

    def test_yaml_config_with_disable_environment_info_false
      yaml_content = <<~YAML
        version: 2
        swarm:
          name: "Test Swarm"
          lead: agent1
          agents:
            agent1:
              description: "Agent 1"
              model: gpt-4
              disable_environment_info: false
              system_prompt: "Custom"
      YAML

      with_temp_config(yaml_content) do |config_path|
        swarm = Configuration.load_file(config_path).to_swarm

        agent_def = swarm.agent_definitions[:agent1]

        refute(agent_def.disable_environment_info)
        assert_includes(agent_def.system_prompt, "Today's date")
      end
    end

    # ========== all_agents Inheritance Tests ==========

    def test_all_agents_disable_environment_info_inheritance
      yaml_content = <<~YAML
        version: 2
        swarm:
          name: "Test Swarm"
          lead: agent1
          all_agents:
            disable_environment_info: true
          agents:
            agent1:
              description: "Agent 1 - inherits"
              model: gpt-4
              system_prompt: "Agent 1"
            agent2:
              description: "Agent 2 - overrides to false"
              model: gpt-4
              system_prompt: "Agent 2"
              disable_environment_info: false
      YAML

      with_temp_config(yaml_content) do |config_path|
        swarm = Configuration.load_file(config_path).to_swarm

        agent1_def = swarm.agent_definitions[:agent1]
        agent2_def = swarm.agent_definitions[:agent2]

        # Agent1 inherits disable_environment_info: true
        assert(agent1_def.disable_environment_info)
        refute_includes(agent1_def.system_prompt, "Today's date")

        # Agent2 overrides to false
        refute(agent2_def.disable_environment_info)
        assert_includes(agent2_def.system_prompt, "Today's date")
      end
    end

    def test_all_agents_disable_environment_info_dsl
      swarm = SwarmSDK.build do
        name("Test Swarm")
        lead(:agent1)

        all_agents do
          disable_environment_info(true)
        end

        agent(:agent1) do
          model("gpt-4")
          description("Agent 1")
          system_prompt("Prompt 1")
        end

        agent(:agent2) do
          model("gpt-4")
          description("Agent 2")
          system_prompt("Prompt 2")
          disable_environment_info(false) # Override
        end
      end

      agent1_def = swarm.agent_definition(:agent1)
      agent2_def = swarm.agent_definition(:agent2)

      # Agent1 inherits from all_agents
      assert(agent1_def.disable_environment_info)
      refute_includes(agent1_def.system_prompt, "Today's date")

      # Agent2 overrides
      refute(agent2_def.disable_environment_info)
      assert_includes(agent2_def.system_prompt, "Today's date")
    end

    # ========== AllAgentsBuilder Tests ==========

    def test_all_agents_builder_setter
      builder = Swarm::AllAgentsBuilder.new
      builder.disable_environment_info(true)
      config = builder.to_h

      assert(config[:disable_environment_info])
    end

    def test_all_agents_builder_to_h_omits_nil
      builder = Swarm::AllAgentsBuilder.new
      config = builder.to_h

      refute(config.key?(:disable_environment_info))
    end

    private

    def with_temp_config(content)
      Dir.mktmpdir("swarm_sdk_test") do |dir|
        config_path = File.join(dir, "swarm.yml")
        File.write(config_path, content)
        yield config_path, dir
      end
    end
  end
end
