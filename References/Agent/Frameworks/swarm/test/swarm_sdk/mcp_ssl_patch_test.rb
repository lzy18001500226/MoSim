# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class McpSslPatchTest < Minitest::Test
    def setup
      @original_ssl_options = McpSslPatch.ssl_options
    end

    def teardown
      McpSslPatch.ssl_options = @original_ssl_options
      McpSslPatch.reset_connection!
    end

    def test_default_ssl_options_uses_verify_peer
      McpSslPatch.ssl_options = { verify_mode: OpenSSL::SSL::VERIFY_PEER }

      assert_equal({ verify_mode: OpenSSL::SSL::VERIFY_PEER }, McpSslPatch.ssl_options)
    end

    def test_ssl_options_is_settable
      McpSslPatch.ssl_options = { verify_mode: OpenSSL::SSL::VERIFY_NONE }

      assert_equal({ verify_mode: OpenSSL::SSL::VERIFY_NONE }, McpSslPatch.ssl_options)
    end

    def test_reset_connection_clears_thread_local_cache
      Thread.current[:ruby_llm_mcp_client_connection] = "cached_connection"

      McpSslPatch.reset_connection!

      assert_nil(Thread.current[:ruby_llm_mcp_client_connection])
    end

    def test_reset_connection_is_idempotent
      McpSslPatch.reset_connection!
      McpSslPatch.reset_connection!

      assert_nil(Thread.current[:ruby_llm_mcp_client_connection])
    end
  end

  class McpSslPatchConfigTest < Minitest::Test
    def setup
      SwarmSDK.reset_config!
    end

    def teardown
      SwarmSDK.reset_config!
    end

    def test_mcp_ssl_verify_defaults_to_true
      assert(SwarmSDK.config.mcp_ssl_verify)
    end

    def test_mcp_ssl_verify_can_be_set_to_false
      SwarmSDK.config.mcp_ssl_verify = false

      refute(SwarmSDK.config.mcp_ssl_verify)
    end

    def test_mcp_ssl_verify_reads_from_env
      ENV["SWARM_SDK_MCP_SSL_VERIFY"] = "false"
      SwarmSDK.reset_config!

      refute(SwarmSDK.config.mcp_ssl_verify)
    ensure
      ENV.delete("SWARM_SDK_MCP_SSL_VERIFY")
    end

    def test_mcp_ssl_verify_env_true_values
      ["true", "yes", "1", "on", "enabled"].each do |value|
        ENV["SWARM_SDK_MCP_SSL_VERIFY"] = value
        SwarmSDK.reset_config!

        assert(SwarmSDK.config.mcp_ssl_verify, "Expected true for ENV value '#{value}'")
      end
    ensure
      ENV.delete("SWARM_SDK_MCP_SSL_VERIFY")
    end

    def test_mcp_ssl_verify_env_false_values
      ["false", "no", "0", "off", "disabled"].each do |value|
        ENV["SWARM_SDK_MCP_SSL_VERIFY"] = value
        SwarmSDK.reset_config!

        refute(SwarmSDK.config.mcp_ssl_verify, "Expected false for ENV value '#{value}'")
      end
    ensure
      ENV.delete("SWARM_SDK_MCP_SSL_VERIFY")
    end
  end

  class Swarm
    class McpConfiguratorSslTest < Minitest::Test
      # Minimal mock MCP client
      class MockMcpClient
        attr_reader :tools

        def initialize(tools: [])
          @tools = tools
        end
      end

      # Minimal mock tool
      class MockTool
        attr_reader :name

        def initialize(name)
          @name = name
        end
      end

      # Minimal mock chat with tool registry
      class MockToolRegistry
        def register(tool, source:, metadata:); end
      end

      class MockChat
        attr_reader :tool_registry

        def initialize
          @tool_registry = MockToolRegistry.new
        end
      end

      def setup
        @original_ssl_options = McpSslPatch.ssl_options
        @swarm = Swarm.new(name: "SSL Test Swarm")
        @configurator = McpConfigurator.new(@swarm)
        @mock_chat = MockChat.new
      end

      def teardown
        McpSslPatch.ssl_options = @original_ssl_options
        McpSslPatch.reset_connection!
        SwarmSDK.reset_config!
      end

      def test_ssl_configured_to_verify_peer_by_default
        mock_client = MockMcpClient.new(tools: [MockTool.new("test")])

        RubyLLM::MCP.stub(:client, mock_client) do
          server_configs = [{ name: :test_server, type: :stdio, command: "cmd" }]

          _out, _err = capture_io do
            @configurator.register_mcp_servers(@mock_chat, server_configs, agent_name: :test_agent)
          end
        end

        assert_equal(OpenSSL::SSL::VERIFY_PEER, McpSslPatch.ssl_options[:verify_mode])
      end

      def test_per_server_ssl_verify_false_sets_verify_none
        mock_client = MockMcpClient.new(tools: [MockTool.new("test")])

        RubyLLM::MCP.stub(:client, mock_client) do
          server_configs = [{ name: :test_server, type: :stdio, command: "cmd", ssl_verify: false }]

          _out, _err = capture_io do
            @configurator.register_mcp_servers(@mock_chat, server_configs, agent_name: :test_agent)
          end
        end

        assert_equal(OpenSSL::SSL::VERIFY_NONE, McpSslPatch.ssl_options[:verify_mode])
      end

      def test_global_config_ssl_verify_false_sets_verify_none
        SwarmSDK.config.mcp_ssl_verify = false
        mock_client = MockMcpClient.new(tools: [MockTool.new("test")])

        RubyLLM::MCP.stub(:client, mock_client) do
          server_configs = [{ name: :test_server, type: :stdio, command: "cmd" }]

          _out, _err = capture_io do
            @configurator.register_mcp_servers(@mock_chat, server_configs, agent_name: :test_agent)
          end
        end

        assert_equal(OpenSSL::SSL::VERIFY_NONE, McpSslPatch.ssl_options[:verify_mode])
      end

      def test_per_server_ssl_verify_overrides_global_config
        SwarmSDK.config.mcp_ssl_verify = false
        mock_client = MockMcpClient.new(tools: [MockTool.new("test")])

        RubyLLM::MCP.stub(:client, mock_client) do
          server_configs = [{ name: :test_server, type: :stdio, command: "cmd", ssl_verify: true }]

          _out, _err = capture_io do
            @configurator.register_mcp_servers(@mock_chat, server_configs, agent_name: :test_agent)
          end
        end

        assert_equal(OpenSSL::SSL::VERIFY_PEER, McpSslPatch.ssl_options[:verify_mode])
      end

      def test_multiple_servers_each_configure_ssl_independently
        mock_client = MockMcpClient.new(tools: [MockTool.new("test")])
        ssl_options_after_each = []

        RubyLLM::MCP.method(:client)
        call_count = 0

        RubyLLM::MCP.stub(:client, ->(**_kwargs) {
          call_count += 1
          ssl_options_after_each << McpSslPatch.ssl_options.dup
          mock_client
        }) do
          server_configs = [
            { name: :server1, type: :stdio, command: "cmd1", ssl_verify: false },
            { name: :server2, type: :stdio, command: "cmd2", ssl_verify: true },
          ]

          _out, _err = capture_io do
            @configurator.register_mcp_servers(@mock_chat, server_configs, agent_name: :test_agent)
          end
        end

        assert_equal(2, ssl_options_after_each.size)
        assert_equal(OpenSSL::SSL::VERIFY_NONE, ssl_options_after_each[0][:verify_mode])
        assert_equal(OpenSSL::SSL::VERIFY_PEER, ssl_options_after_each[1][:verify_mode])
      end
    end
  end
end
