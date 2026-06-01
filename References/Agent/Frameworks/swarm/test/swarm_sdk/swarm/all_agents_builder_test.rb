# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class Swarm
    class AllAgentsBuilderTest < Minitest::Test
      def setup
        @builder = AllAgentsBuilder.new
      end

      def test_initialize_sets_defaults
        assert_empty(@builder.tools_list)
        assert_empty(@builder.hooks)
        assert_empty(@builder.permissions_config)
      end

      def test_model_setter
        @builder.model(:opus)
        config = @builder.to_h

        assert_equal(:opus, config[:model])
      end

      def test_provider_setter
        @builder.provider(:openai)
        config = @builder.to_h

        assert_equal(:openai, config[:provider])
      end

      def test_base_url_setter
        @builder.base_url("http://proxy.com/v1")
        config = @builder.to_h

        assert_equal("http://proxy.com/v1", config[:base_url])
      end

      def test_api_version_setter
        @builder.api_version("2024-01-01")
        config = @builder.to_h

        assert_equal("2024-01-01", config[:api_version])
      end

      def test_timeout_setter
        @builder.request_timeout(180)
        config = @builder.to_h

        assert_equal(180, config[:request_timeout])
      end

      def test_parameters_setter
        params = { temperature: 0.7, max_tokens: 1000 }
        @builder.parameters(params)
        config = @builder.to_h

        assert_equal(params, config[:parameters])
      end

      def test_headers_setter
        headers = { "X-Custom-Header" => "value" }
        @builder.headers(headers)
        config = @builder.to_h

        assert_equal(headers, config[:headers])
      end

      def test_coding_agent_setter
        @builder.coding_agent(false)
        config = @builder.to_h

        refute(config[:coding_agent])
      end

      def test_disable_default_tools_with_boolean
        @builder.disable_default_tools(true)
        config = @builder.to_h

        assert(config[:disable_default_tools])
      end

      def test_disable_default_tools_with_array
        @builder.disable_default_tools([:Think, :TodoWrite])
        config = @builder.to_h

        assert_equal([:Think, :TodoWrite], config[:disable_default_tools])
      end

      def test_tools_adds_to_list
        @builder.tools(:Read, :Write)
        @builder.tools(:Bash)

        assert_equal([:Read, :Write, :Bash], @builder.tools_list)
      end

      def test_hook_with_valid_agent_event
        block = proc { |ctx| puts ctx }
        @builder.hook(:pre_tool_use, matcher: "Write", &block)

        assert_equal(1, @builder.hooks.size)
        hook = @builder.hooks.first

        assert_equal(:pre_tool_use, hook[:event])
        assert_equal("Write", hook[:matcher])
        assert_equal(block, hook[:block])
      end

      def test_hook_with_command
        @builder.hook(:post_tool_use, command: "/path/to/script.sh", timeout: 10)

        hook = @builder.hooks.first

        assert_equal(:post_tool_use, hook[:event])
        assert_equal("/path/to/script.sh", hook[:command])
        assert_equal(10, hook[:timeout])
      end

      def test_hook_rejects_swarm_level_events
        error = assert_raises(ArgumentError) do
          @builder.hook(:swarm_start) { |ctx| puts ctx }
        end

        assert_match(/Invalid all_agents hook: swarm_start/, error.message)
        assert_match(/Swarm-level events.*cannot be used in all_agents block/, error.message)
      end

      def test_hook_rejects_swarm_stop_event
        error = assert_raises(ArgumentError) do
          @builder.hook(:swarm_stop) { |ctx| puts ctx }
        end

        assert_match(/swarm_stop/, error.message)
      end

      def test_hook_accepts_all_valid_agent_events
        valid_events = [
          :pre_tool_use,
          :post_tool_use,
          :user_prompt,
          :agent_stop,
          :first_message,
          :pre_delegation,
          :post_delegation,
          :context_warning,
        ]

        valid_events.each do |event|
          builder = AllAgentsBuilder.new
          builder.hook(event) { |ctx| puts ctx }

          assert_equal(1, builder.hooks.size)
          assert_equal(event, builder.hooks.first[:event])
        end
      end

      def test_permissions_with_block
        # Use hash setter for testing since PermissionsBuilder requires tool constants
        @builder.permissions_hash = {
          Write: {
            allow_paths: ["tmp/**/*"],
            deny_paths: ["tmp/secrets/**"],
          },
        }

        refute_empty(@builder.permissions_config)
      end

      def test_permissions_hash_setter
        hash = {
          Write: {
            allow_paths: ["tmp/**/*"],
            deny_paths: ["tmp/secrets/**"],
          },
        }
        @builder.permissions_hash = hash

        assert_equal(hash, @builder.permissions_config)
      end

      def test_permissions_hash_setter_with_nil
        @builder.permissions_hash = nil

        assert_empty(@builder.permissions_config)
      end

      def test_to_h_includes_all_set_values
        @builder.model(:opus)
        @builder.provider(:openai)
        @builder.base_url("http://proxy.com")
        @builder.request_timeout(180)
        @builder.tools(:Read, :Write)

        config = @builder.to_h

        assert_equal(:opus, config[:model])
        assert_equal(:openai, config[:provider])
        assert_equal("http://proxy.com", config[:base_url])
        assert_equal(180, config[:request_timeout])
        assert_equal([:Read, :Write], config[:tools])
      end

      def test_to_h_excludes_nil_values
        # Only set a few values
        @builder.model(:opus)
        @builder.tools(:Read)

        config = @builder.to_h

        # Should only include non-nil values
        assert_equal([:model, :permissions, :tools], config.keys.sort)
        refute(config.key?(:provider))
        refute(config.key?(:base_url))
        refute(config.key?(:timeout))
      end

      def test_complete_configuration
        @builder.model(:opus)
        @builder.provider(:openai)
        @builder.base_url("http://proxy.com/v1")
        @builder.api_version("2024-01-01")
        @builder.request_timeout(180)
        @builder.parameters({ temperature: 0.7 })
        @builder.headers({ "X-Custom" => "value" })
        @builder.coding_agent(false)
        @builder.disable_default_tools([:Think])
        @builder.tools(:Read, :Write, :Bash)
        @builder.hook(:pre_tool_use, matcher: "Write") { |ctx| puts ctx }
        @builder.permissions_hash = { Write: { allow_paths: ["**/*"] } }

        config = @builder.to_h

        assert_equal(:opus, config[:model])
        assert_equal(:openai, config[:provider])
        assert_equal("http://proxy.com/v1", config[:base_url])
        assert_equal("2024-01-01", config[:api_version])
        assert_equal(180, config[:request_timeout])
        assert_equal({ temperature: 0.7 }, config[:parameters])
        assert_equal({ "X-Custom" => "value" }, config[:headers])
        refute(config[:coding_agent])
        assert_equal([:Think], config[:disable_default_tools])
        assert_equal([:Read, :Write, :Bash], config[:tools])
        assert_equal({ Write: { allow_paths: ["**/*"] } }, config[:permissions])
      end
    end
  end
end
