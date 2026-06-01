# frozen_string_literal: true

require "test_helper"

class FilesystemToolsTest < Minitest::Test
  def setup
    SwarmSDK.reset_config!
  end

  def teardown
    SwarmSDK.reset_config!
  end

  # Configuration resolution tests
  def test_default_allows_filesystem_tools
    # Reset to fresh config
    SwarmSDK.reset_config!

    assert(SwarmSDK.config.allow_filesystem_tools)
  end

  def test_global_configuration_block
    SwarmSDK.configure do |config|
      config.allow_filesystem_tools = false
    end

    refute(SwarmSDK.config.allow_filesystem_tools)
  end

  def test_direct_setter
    SwarmSDK.configure do |config|
      config.allow_filesystem_tools = false
    end

    refute(SwarmSDK.config.allow_filesystem_tools)

    SwarmSDK.configure do |config|
      config.allow_filesystem_tools = true
    end

    assert(SwarmSDK.config.allow_filesystem_tools)
  end

  # NOTE: ENV variable tests are in config_test.rb
  # test_env_boolean_parsing_for_filesystem_tools
  # test_env_boolean_parsing_various_true_values
  # test_env_boolean_parsing_various_false_values

  def test_parameter_overrides_global
    SwarmSDK.config.allow_filesystem_tools = true

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.build(allow_filesystem_tools: false) do
        name("Test")
        agent(:dev) do
          description("Developer")
          tools(:Write)
        end
        lead(:dev)
      end
    end

    assert_match(/Write/, error.message)
  end

  # Validation tests
  def test_blocks_explicit_filesystem_tools
    SwarmSDK.config.allow_filesystem_tools = false

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.build do
        name("Test")
        agent(:dev) do
          description("Developer")
          tools(:Read, :Write, :Edit)
        end
        lead(:dev)
      end
    end

    assert_match(/Read/, error.message)
    assert_match(/Write/, error.message)
    assert_match(/Edit/, error.message)
    assert_match(/globally disabled/, error.message)
  end

  def test_blocks_all_agents_filesystem_tools
    SwarmSDK.config.allow_filesystem_tools = false

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.build do
        name("Test")

        all_agents do
          tools(:Grep, :Glob)
        end

        agent(:dev) { description("Developer") }
        lead(:dev)
      end
    end

    assert_match(/Grep/, error.message)
    assert_match(/Glob/, error.message)
    assert_match(/all_agents/, error.message)
  end

  def test_blocks_bash
    SwarmSDK.config.allow_filesystem_tools = false

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.build do
        name("Test")
        agent(:dev) do
          description("Developer")
          tools(:Bash)
        end
        lead(:dev)
      end
    end

    assert_match(/Bash/, error.message)
  end

  def test_allows_non_filesystem_tools_when_restricted
    SwarmSDK.config.allow_filesystem_tools = false

    swarm = SwarmSDK.build do
      name("Test")
      agent(:analyst) do
        description("Analyst")
        tools(:Think, :WebFetch, :Clock)
      end
      lead(:analyst)
    end

    assert_equal("Test", swarm.name)
    refute(swarm.allow_filesystem_tools)
  end

  def test_yaml_loading_respects_global_setting
    SwarmSDK.config.allow_filesystem_tools = false

    yaml = <<~YAML
      version: 2
      swarm:
        name: "Test"
        lead: dev
        agents:
          dev:
            description: "Developer"
            tools: [Read, Write]
    YAML

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.load(yaml)
    end

    assert_match(/Read/, error.message)
    assert_match(/Write/, error.message)
  end

  def test_yaml_loading_with_parameter_override
    SwarmSDK.config.allow_filesystem_tools = true # Global allows

    yaml = <<~YAML
      version: 2
      swarm:
        name: "Test"
        lead: dev
        agents:
          dev:
            description: "Developer"
            tools: [Bash]
    YAML

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.load(yaml, allow_filesystem_tools: false) # Parameter disallows
    end

    assert_match(/Bash/, error.message)
  end

  def test_swarm_instance_has_immutable_setting
    swarm = SwarmSDK.build(allow_filesystem_tools: false) do
      name("Test")
      agent(:dev) { description("Developer") }
      lead(:dev)
    end

    refute(swarm.allow_filesystem_tools)

    # Should not have a setter
    refute_respond_to(swarm, :allow_filesystem_tools=)
  end

  def test_error_message_provides_solution
    SwarmSDK.config.allow_filesystem_tools = false

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.build do
        name("Test")
        agent(:dev) do
          description("Developer")
          tools(:Edit)
        end
        lead(:dev)
      end
    end

    assert_match(/system-wide security setting/, error.message)
    assert_match(/SwarmSDK.config.allow_filesystem_tools = true/, error.message)
  end

  def test_allows_all_filesystem_tools_when_enabled
    SwarmSDK.config.allow_filesystem_tools = true

    swarm = SwarmSDK.build do
      name("Test")
      agent(:dev) do
        description("Developer")
        tools(:Read, :Write, :Edit, :MultiEdit, :Grep, :Glob, :Bash)
      end
      lead(:dev)
    end

    assert_equal("Test", swarm.name)
    assert(swarm.allow_filesystem_tools)
  end

  def test_mixed_tools_allowed_and_forbidden
    SwarmSDK.config.allow_filesystem_tools = false

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.build do
        name("Test")
        agent(:dev) do
          description("Developer")
          tools(:Think, :Read, :WebFetch, :Write) # Mixed: Think and WebFetch allowed, Read and Write forbidden
        end
        lead(:dev)
      end
    end

    # Should only mention forbidden tools
    assert_match(/Read/, error.message)
    assert_match(/Write/, error.message)
    # Should not mention allowed tools
    refute_match(/Think/, error.message)
    refute_match(/WebFetch/, error.message)
  end

  def test_scratchpad_tools_work_when_filesystem_disabled
    SwarmSDK.config.allow_filesystem_tools = false

    swarm = SwarmSDK.build do
      name("Test")
      agent(:dev) do
        description("Developer")
        # Scratchpad tools should still work
        tools(:ScratchpadWrite, :ScratchpadRead, :ScratchpadList)
      end
      lead(:dev)
    end

    assert_equal("Test", swarm.name)
    refute(swarm.allow_filesystem_tools)
  end

  def test_workflow_respects_filesystem_tools_setting
    SwarmSDK.config.allow_filesystem_tools = false

    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.workflow do
        name("Test Workflow")

        agent(:dev) do
          description("Developer")
          tools(:Read) # Should be blocked
        end

        node(:planning) do
          agent(:dev)
          lead(:dev)
        end

        start_node(:planning)
      end
    end

    assert_match(/Read/, error.message)
  end

  def test_load_file_respects_parameter
    SwarmSDK.config.allow_filesystem_tools = true

    yaml = <<~YAML
      version: 2
      swarm:
        name: "Test"
        lead: dev
        agents:
          dev:
            description: "Developer"
            tools: [Edit]
    YAML

    # Write to temp file
    require "tempfile"
    Tempfile.create(["test", ".yml"]) do |f|
      f.write(yaml)
      f.flush

      error = assert_raises(SwarmSDK::ConfigurationError) do
        SwarmSDK.load_file(f.path, allow_filesystem_tools: false)
      end

      assert_match(/Edit/, error.message)
    end
  end

  def test_all_agents_and_explicit_tools_both_validated
    SwarmSDK.config.allow_filesystem_tools = false

    # Test that all_agents validation catches early
    error = assert_raises(SwarmSDK::ConfigurationError) do
      SwarmSDK.build do
        name("Test")

        all_agents do
          tools(:Bash) # Should be caught in build_swarm validation
        end

        agent(:dev) { description("Developer") }
        lead(:dev)
      end
    end

    assert_match(/Bash/, error.message)
    assert_match(/all_agents/, error.message)
  end
end
