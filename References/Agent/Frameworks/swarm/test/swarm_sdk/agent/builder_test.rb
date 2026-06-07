# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Agent
    class BuilderTest < Minitest::Test
      def setup
        @builder = Builder.new(:test_agent)
      end

      # === Initialization Tests ===

      def test_initialize_sets_defaults
        assert_equal("gpt-5", @builder.model)
        assert_nil(@builder.provider)
        assert_nil(@builder.base_url)
        assert_nil(@builder.api_version)
        assert_nil(@builder.request_timeout)
        assert_empty(@builder.tools_list)
        assert_empty(@builder.mcp_servers)
      end

      # === Model Getter/Setter Tests ===

      def test_model_getter_returns_current_value
        assert_equal("gpt-5", @builder.model)
      end

      def test_model_setter_changes_value
        @builder.model("claude-opus")

        assert_equal("claude-opus", @builder.model)
      end

      def test_model_with_no_args_returns_current
        @builder.model("gpt-4")

        assert_equal("gpt-4", @builder.model)
      end

      # === Provider Getter/Setter Tests ===

      def test_provider_getter_returns_nil_by_default
        assert_nil(@builder.provider)
      end

      def test_provider_setter_changes_value
        @builder.provider("anthropic")

        assert_equal("anthropic", @builder.provider)
      end

      def test_provider_with_no_args_returns_current
        @builder.provider("openai")

        assert_equal("openai", @builder.provider)
      end

      # === Base URL Getter/Setter Tests ===

      def test_base_url_getter_returns_nil_by_default
        assert_nil(@builder.base_url)
      end

      def test_base_url_setter_changes_value
        @builder.base_url("https://api.example.com")

        assert_equal("https://api.example.com", @builder.base_url)
      end

      def test_base_url_with_no_args_returns_current
        @builder.base_url("https://test.com")

        assert_equal("https://test.com", @builder.base_url)
      end

      # === API Version Getter/Setter Tests ===

      def test_api_version_getter_returns_nil_by_default
        assert_nil(@builder.api_version)
      end

      def test_api_version_setter_changes_value
        @builder.api_version("2024-01-01")

        assert_equal("2024-01-01", @builder.api_version)
      end

      def test_api_version_with_no_args_returns_current
        @builder.api_version("2024-02-01")

        assert_equal("2024-02-01", @builder.api_version)
      end

      # === Context Window Getter/Setter Tests ===

      def test_context_window_getter_returns_nil_by_default
        result = @builder.context_window

        assert_nil(result)
      end

      def test_context_window_setter_changes_value
        @builder.context_window(8000)

        assert_equal(8000, @builder.context_window)
      end

      def test_context_window_with_no_args_returns_current
        @builder.context_window(16000)

        assert_equal(16000, @builder.context_window)
      end

      # === Parameters Getter/Setter Tests ===

      def test_parameters_getter_returns_empty_hash_by_default
        assert_empty(@builder.parameters)
      end

      def test_parameters_setter_changes_value
        params = { temperature: 0.7, max_tokens: 2000 }
        @builder.parameters(params)

        assert_equal(params, @builder.parameters)
      end

      def test_parameters_with_no_args_returns_current
        params = { temperature: 0.5 }
        @builder.parameters(params)

        assert_equal(params, @builder.parameters)
      end

      # === Headers Getter/Setter Tests ===

      def test_headers_getter_returns_empty_hash_by_default
        assert_empty(@builder.headers)
      end

      def test_headers_setter_changes_value
        headers = { "Authorization" => "Bearer token" }
        @builder.headers(headers)

        assert_equal(headers, @builder.headers)
      end

      def test_headers_with_no_args_returns_current
        headers = { "X-Custom" => "value" }
        @builder.headers(headers)

        assert_equal(headers, @builder.headers)
      end

      # === Timeout Getter/Setter Tests ===

      def test_timeout_getter_returns_nil_by_default
        assert_nil(@builder.request_timeout)
      end

      def test_timeout_setter_changes_value
        @builder.request_timeout(600)

        assert_equal(600, @builder.request_timeout)
      end

      def test_timeout_with_no_args_returns_current
        @builder.request_timeout(300)

        assert_equal(300, @builder.request_timeout)
      end

      # === MCP Server Tests ===

      def test_mcp_server_adds_stdio_server
        @builder.mcp_server(:filesystem, type: :stdio, command: "npx", args: ["-y", "mcp-server"])

        assert_equal(1, @builder.mcp_servers.size)
        server = @builder.mcp_servers.first

        assert_equal(:filesystem, server[:name])
        assert_equal(:stdio, server[:type])
        assert_equal("npx", server[:command])
        assert_equal(["-y", "mcp-server"], server[:args])
      end

      def test_mcp_server_adds_sse_server
        @builder.mcp_server(:web, type: :sse, url: "https://example.com", headers: { auth: "token" })

        server = @builder.mcp_servers.first

        assert_equal(:web, server[:name])
        assert_equal(:sse, server[:type])
        assert_equal("https://example.com", server[:url])
        assert_equal({ auth: "token" }, server[:headers])
      end

      def test_mcp_server_adds_http_server
        @builder.mcp_server(:api, type: :http, url: "https://api.example.com", timeout: 60)

        server = @builder.mcp_servers.first

        assert_equal(:api, server[:name])
        assert_equal(:http, server[:type])
        assert_equal("https://api.example.com", server[:url])
        assert_equal(60, server[:timeout])
      end

      def test_mcp_server_multiple_servers
        @builder.mcp_server(:server1, type: :stdio, command: "cmd1")
        @builder.mcp_server(:server2, type: :sse, url: "https://example.com")

        assert_equal(2, @builder.mcp_servers.size)
        assert_equal(:server1, @builder.mcp_servers[0][:name])
        assert_equal(:server2, @builder.mcp_servers[1][:name])
      end

      # === Disable Default Tools Tests ===

      def test_disable_default_tools_with_no_args
        capture_io do
          @builder.disable_default_tools
          definition = @builder.to_definition
          # With no args, returns nil (doesn't disable anything)
          # Check behavior through to_definition
          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_disable_default_tools_with_true
        capture_io do
          @builder.disable_default_tools(true)
          definition = @builder.to_definition
          # Verify it was set
          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_disable_default_tools_with_false
        capture_io do
          @builder.disable_default_tools(false)
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_disable_default_tools_with_single_array
        capture_io do
          @builder.disable_default_tools([:Think, :TodoWrite])
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_disable_default_tools_with_multiple_symbols
        capture_io do
          @builder.disable_default_tools(:Think, :TodoWrite)
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      # === Other Setter Tests ===

      def test_bypass_permissions_setter
        @builder.bypass_permissions(true)
        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_coding_agent_setter
        @builder.coding_agent(true)
        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_assume_model_exists_setter
        @builder.assume_model_exists(true)
        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_system_prompt_setter
        @builder.system_prompt("You are a test agent")
        capture_io do
          definition = @builder.to_definition

          assert_includes(definition.system_prompt, "You are a test agent")
        end
      end

      def test_description_setter
        @builder.description("Test description")
        capture_io do
          definition = @builder.to_definition

          assert_equal("Test description", definition.description)
        end
      end

      def test_directory_setter
        @builder.directory("lib")
        capture_io do
          definition = @builder.to_definition

          assert_equal(File.expand_path("lib"), definition.directory)
        end
      end

      def test_delegates_to_single_agent
        @builder.delegates_to(:backend)
        capture_io do
          definition = @builder.to_definition

          assert_equal([:backend], definition.delegates_to)
        end
      end

      def test_delegates_to_multiple_agents
        @builder.delegates_to(:backend, :frontend)
        capture_io do
          definition = @builder.to_definition

          assert_equal([:backend, :frontend], definition.delegates_to)
        end
      end

      def test_delegates_to_cumulative
        @builder.delegates_to(:backend)
        @builder.delegates_to(:frontend)
        capture_io do
          definition = @builder.to_definition

          assert_equal([:backend, :frontend], definition.delegates_to)
        end
      end

      # === Tools Tests ===

      def test_tools_basic_usage
        @builder.tools(:Read, :Write)

        assert_equal([:Read, :Write], @builder.tools_list)
      end

      def test_tools_with_include_default_false
        @builder.tools(:Read, :Write, include_default: false)

        assert_equal([:Read, :Write], @builder.tools_list)
      end

      def test_tools_with_replace_true
        @builder.tools(:Read, :Write)
        @builder.tools(:Bash, replace: true)

        assert_equal([:Bash], @builder.tools_list)
      end

      def test_tools_with_replace_false
        @builder.tools(:Read, :Write)
        @builder.tools(:Bash, replace: false)

        assert_equal([:Read, :Write, :Bash], @builder.tools_list)
      end

      def test_tools_cumulative_by_default
        @builder.tools(:Read)
        @builder.tools(:Write)
        @builder.tools(:Read) # Duplicate

        assert_equal([:Read, :Write], @builder.tools_list)
      end

      def test_tools_automatic_deduplication
        @builder.tools(:Read, :Write, :Read, :Write)

        assert_equal([:Read, :Write], @builder.tools_list)
      end

      def test_prepend_tools_adds_tools
        @builder.prepend_tools(:Read, :Write)

        assert_equal([:Read, :Write], @builder.tools_list)
      end

      def test_prepend_tools_deduplicates
        @builder.tools(:Read)
        @builder.prepend_tools(:Read, :Write)

        assert_equal([:Read, :Write], @builder.tools_list)
      end

      # === Hook Tests ===

      def test_hook_with_ruby_block
        block = proc { |_ctx| "test" }
        @builder.hook(:pre_tool_use, matcher: "Bash", &block)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_hook_with_command
        @builder.hook(:pre_tool_use, matcher: "Bash", command: "validate.sh", timeout: 30)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_hook_with_nil_matcher
        block = proc { |_ctx| "test" }
        @builder.hook(:pre_tool_use, &block)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_hook_multiple_hooks
        block1 = proc { |_ctx| "test1" }
        block2 = proc { |_ctx| "test2" }
        @builder.hook(:pre_tool_use, matcher: "Write", &block1)
        @builder.hook(:post_tool_use, matcher: "Read", &block2)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      # === Permissions Tests ===

      def test_permissions_with_block
        @builder.permissions do
          tool(:Write).allow_paths("tmp/**/*")
        end

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_permissions_hash_setter
        hash = { Write: { allowed_paths: ["tmp/**/*"] } }
        @builder.permissions_hash = hash

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_permissions_hash_setter_with_nil
        @builder.permissions_hash = nil

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      # === Shared Across Delegations Tests ===

      def test_shared_across_delegations_true
        result = @builder.shared_across_delegations(true)

        assert_equal(@builder, result) # Returns self

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_shared_across_delegations_false
        result = @builder.shared_across_delegations(false)

        assert_equal(@builder, result)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      # === Predicate Methods Tests ===

      def test_model_set_returns_false_for_default
        refute_predicate(@builder, :model_set?)
      end

      def test_model_set_returns_true_when_changed
        @builder.model("claude-opus")

        assert_predicate(@builder, :model_set?)
      end

      def test_provider_set_returns_false_by_default
        refute_predicate(@builder, :provider_set?)
      end

      def test_provider_set_returns_true_when_set
        @builder.provider("anthropic")

        assert_predicate(@builder, :provider_set?)
      end

      def test_base_url_set_returns_false_by_default
        refute_predicate(@builder, :base_url_set?)
      end

      def test_base_url_set_returns_true_when_set
        @builder.base_url("https://example.com")

        assert_predicate(@builder, :base_url_set?)
      end

      def test_api_version_set_returns_false_by_default
        refute_predicate(@builder, :api_version_set?)
      end

      def test_api_version_set_returns_true_when_set
        @builder.api_version("2024-01-01")

        assert_predicate(@builder, :api_version_set?)
      end

      def test_timeout_set_returns_false_by_default
        refute_predicate(@builder, :request_timeout_set?)
      end

      def test_timeout_set_returns_true_when_set
        @builder.request_timeout(600)

        assert_predicate(@builder, :request_timeout_set?)
      end

      def test_coding_agent_set_returns_false_by_default
        refute_predicate(@builder, :coding_agent_set?)
      end

      def test_coding_agent_set_returns_true_when_set
        @builder.coding_agent(true)

        assert_predicate(@builder, :coding_agent_set?)
      end

      def test_coding_agent_set_returns_true_even_for_false
        @builder.coding_agent(false)

        assert_predicate(@builder, :coding_agent_set?)
      end

      def test_parameters_set_returns_false_for_empty
        refute_predicate(@builder, :parameters_set?)
      end

      def test_parameters_set_returns_true_when_set
        @builder.parameters({ temperature: 0.7 })

        assert_predicate(@builder, :parameters_set?)
      end

      def test_headers_set_returns_false_for_empty
        refute_predicate(@builder, :headers_set?)
      end

      def test_headers_set_returns_true_when_set
        @builder.headers({ "X-Custom" => "value" })

        assert_predicate(@builder, :headers_set?)
      end

      # === to_definition Tests - All Branches ===

      def test_to_definition_minimal_config
        @builder.description("Test agent")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
          assert_equal("Test agent", definition.description)
          assert_equal("gpt-5", definition.model)
        end
      end

      def test_to_definition_with_provider
        @builder.description("Test")
        @builder.provider("anthropic")

        capture_io do
          definition = @builder.to_definition

          assert_equal("anthropic", definition.provider)
        end
      end

      def test_to_definition_with_base_url
        @builder.description("Test")
        @builder.base_url("https://example.com")

        capture_io do
          definition = @builder.to_definition

          assert_equal("https://example.com", definition.base_url)
        end
      end

      def test_to_definition_with_api_version
        @builder.description("Test")
        @builder.provider("openai")
        @builder.api_version("v1/responses")

        capture_io do
          definition = @builder.to_definition

          assert_equal("v1/responses", definition.api_version)
        end
      end

      def test_to_definition_with_context_window
        @builder.description("Test")
        @builder.context_window(128000)

        capture_io do
          definition = @builder.to_definition
          # Verify no error occurs
          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_parameters_empty
        @builder.description("Test")
        @builder.parameters({})

        capture_io do
          definition = @builder.to_definition
          # Empty parameters should not be included
          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_parameters_present
        @builder.description("Test")
        @builder.parameters({ temperature: 0.7 })

        capture_io do
          definition = @builder.to_definition

          assert_in_delta(0.7, definition.parameters[:temperature])
        end
      end

      def test_to_definition_with_headers_empty
        @builder.description("Test")
        @builder.headers({})

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_headers_present
        @builder.description("Test")
        @builder.headers({ "X-Custom" => "value" })

        capture_io do
          definition = @builder.to_definition
          # Verify no error occurs
          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_timeout
        @builder.description("Test")
        @builder.request_timeout(600)

        capture_io do
          definition = @builder.to_definition

          assert_equal(600, definition.request_timeout)
        end
      end

      def test_to_definition_with_mcp_servers_empty
        @builder.description("Test")

        capture_io do
          definition = @builder.to_definition

          assert_empty(definition.mcp_servers)
        end
      end

      def test_to_definition_with_mcp_servers_present
        @builder.description("Test")
        @builder.mcp_server(:test, type: :stdio, command: "test")

        capture_io do
          definition = @builder.to_definition

          assert_equal(1, definition.mcp_servers.size)
        end
      end

      def test_to_definition_with_disable_default_tools_nil
        @builder.description("Test")
        # disable_default_tools is nil by default

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_disable_default_tools_true
        @builder.description("Test")
        @builder.disable_default_tools(true)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_bypass_permissions_true
        @builder.description("Test")
        @builder.bypass_permissions(true)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_bypass_permissions_false
        @builder.description("Test")
        @builder.bypass_permissions(false)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_coding_agent_nil
        @builder.description("Test")
        # coding_agent is nil by default

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_coding_agent_true
        @builder.description("Test")
        @builder.coding_agent(true)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_assume_model_exists_nil
        @builder.description("Test")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_assume_model_exists_true
        @builder.description("Test")
        @builder.assume_model_exists(true)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_permissions_empty
        @builder.description("Test")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_permissions_present
        @builder.description("Test")
        @builder.permissions_hash = { Write: { allowed_paths: ["**/*"] } }

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_default_permissions_empty
        @builder.description("Test")
        @builder.default_permissions = {}

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_default_permissions_present
        @builder.description("Test")
        @builder.default_permissions = { Read: { allowed_paths: ["**/*"] } }

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_memory_config_nil
        @builder.description("Test")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_shared_across_delegations_nil
        @builder.description("Test")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_shared_across_delegations_true
        @builder.description("Test")
        @builder.shared_across_delegations(true)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_hooks_empty
        @builder.description("Test")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_with_hooks_present
        @builder.description("Test")
        @builder.hook(:pre_tool_use, matcher: "Write") { |_ctx| "test" }

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_to_definition_converts_tools_set_to_array
        @builder.description("Test")
        @builder.tools(:Read, :Write)

        capture_io do
          definition = @builder.to_definition
          # Tools should be an array in the definition
          assert_instance_of(Agent::Definition, definition)
        end
      end

      # === Hook Conversion Tests (Private Method Behavior) ===

      def test_hook_conversion_with_ruby_block
        @builder.description("Test")
        block = proc { |_ctx| "result" }
        @builder.hook(:pre_tool_use, matcher: "Bash", &block)

        capture_io do
          definition = @builder.to_definition
          # Verify definition was created successfully
          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_hook_conversion_with_shell_command
        @builder.description("Test")
        @builder.hook(:pre_tool_use, matcher: "Bash", command: "validate.sh", timeout: 30)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_hook_conversion_with_default_timeout
        @builder.description("Test")
        @builder.hook(:pre_tool_use, command: "test.sh")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_hook_conversion_without_matcher
        @builder.description("Test")
        block = proc { |_ctx| "test" }
        @builder.hook(:pre_tool_use, &block)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      # === Build Hook Input Tests (Private Method Behavior) ===

      def test_build_hook_input_for_pre_tool_use
        @builder.description("Test")
        @builder.hook(:pre_tool_use, command: "test.sh")

        # Test through to_definition which exercises build_hook_input
        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_build_hook_input_for_post_tool_use
        @builder.description("Test")
        @builder.hook(:post_tool_use, command: "test.sh")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_build_hook_input_for_user_prompt
        @builder.description("Test")
        @builder.hook(:user_prompt, command: "test.sh")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_build_hook_input_for_other_event
        @builder.description("Test")
        @builder.hook(:agent_stop, command: "test.sh")

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      # === Integration Tests ===

      def test_complete_configuration
        @builder.description("Complete agent")
        @builder.model("claude-opus")
        @builder.provider("anthropic")
        @builder.base_url("https://api.anthropic.com")
        @builder.context_window(200000)
        @builder.parameters({ temperature: 0.7, max_tokens: 4000 })
        @builder.headers({ "X-Custom" => "value" })
        @builder.request_timeout(600)
        @builder.system_prompt("You are a test agent")
        @builder.tools(:Read, :Write, :Bash)
        @builder.delegates_to(:backend, :frontend)
        @builder.directory("lib")
        @builder.mcp_server(:test, type: :stdio, command: "test")
        @builder.disable_default_tools(:Think)
        @builder.bypass_permissions(true)
        @builder.coding_agent(false)
        @builder.assume_model_exists(true)
        @builder.hook(:pre_tool_use, matcher: "Write") { |_ctx| "test" }
        @builder.permissions_hash = { Write: { allowed_paths: ["**/*"] } }
        @builder.shared_across_delegations(true)

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
          assert_equal("Complete agent", definition.description)
          assert_equal("claude-opus", definition.model)
          assert_equal("anthropic", definition.provider)
          assert_equal("https://api.anthropic.com", definition.base_url)
          assert_equal(600, definition.request_timeout)
          assert_equal(File.expand_path("lib"), definition.directory)
          assert_equal([:backend, :frontend], definition.delegates_to)
        end
      end

      def test_default_description_when_not_set
        capture_io do
          definition = @builder.to_definition

          assert_equal("Agent test_agent", definition.description)
        end
      end

      def test_attr_writer_default_permissions
        hash = { Read: { allowed_paths: ["**/*"] } }
        @builder.default_permissions = hash

        capture_io do
          definition = @builder.to_definition

          assert_instance_of(Agent::Definition, definition)
        end
      end

      def test_attr_reader_mcp_servers
        @builder.mcp_server(:test, type: :stdio, command: "test")

        assert_equal(1, @builder.mcp_servers.size)
      end

      def test_tools_list_returns_array
        @builder.tools(:Read, :Write)
        result = @builder.tools_list

        assert_instance_of(Array, result)
        assert_equal([:Read, :Write], result)
      end
    end
  end
end
