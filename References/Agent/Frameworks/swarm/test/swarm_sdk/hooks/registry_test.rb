# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Hooks
    class RegistryTest < Minitest::Test
      def setup
        @registry = Registry.new
      end

      def test_register_named_hook
        block = proc { |ctx| puts ctx }
        @registry.register(:test_hook, &block)

        assert_equal(block, @registry.get(:test_hook))
      end

      def test_register_requires_symbol_name
        error = assert_raises(ArgumentError) do
          @registry.register("string_name") { |ctx| puts ctx }
        end

        assert_match(/Hook name must be a symbol/, error.message)
      end

      def test_register_rejects_duplicate_name
        @registry.register(:my_hook) { |ctx| puts ctx }

        error = assert_raises(ArgumentError) do
          @registry.register(:my_hook) { |_ctx| puts "different" }
        end

        assert_match(/Hook my_hook already registered/, error.message)
      end

      def test_register_requires_block
        error = assert_raises(ArgumentError) do
          @registry.register(:test_hook)
        end

        assert_match(/Block required/, error.message)
      end

      def test_get_returns_nil_for_unknown_hook
        assert_nil(@registry.get(:unknown_hook))
      end

      def test_add_default_hook
        block = proc { |ctx| puts ctx }
        @registry.add_default(:pre_tool_use, &block)

        defaults = @registry.get_defaults(:pre_tool_use)

        assert_equal(1, defaults.size)
        assert_instance_of(Definition, defaults.first)
        assert_equal(:pre_tool_use, defaults.first.event)
        assert_equal(block, defaults.first.proc)
      end

      def test_add_default_with_matcher
        @registry.add_default(:pre_tool_use, matcher: "Write|Edit") { |ctx| puts ctx }

        defaults = @registry.get_defaults(:pre_tool_use)
        definition = defaults.first

        # Matcher is converted to Regexp in Definition
        assert_equal(/Write|Edit/, definition.matcher)
      end

      def test_add_default_with_priority
        # Add hooks with different priorities
        @registry.add_default(:pre_tool_use, priority: 5) { |_ctx| puts "priority 5" }
        @registry.add_default(:pre_tool_use, priority: 10) { |_ctx| puts "priority 10" }
        @registry.add_default(:pre_tool_use, priority: 1) { |_ctx| puts "priority 1" }

        defaults = @registry.get_defaults(:pre_tool_use)

        # Should be sorted by priority (highest first)
        assert_equal(10, defaults[0].priority)
        assert_equal(5, defaults[1].priority)
        assert_equal(1, defaults[2].priority)
      end

      def test_add_default_requires_valid_event
        error = assert_raises(ArgumentError) do
          @registry.add_default(:invalid_event) { |ctx| puts ctx }
        end

        assert_match(/Invalid event type/, error.message)
        assert_match(/invalid_event/, error.message)
      end

      def test_add_default_requires_block
        error = assert_raises(ArgumentError) do
          @registry.add_default(:pre_tool_use)
        end

        assert_match(/Block required/, error.message)
      end

      def test_get_defaults_for_event_with_no_hooks
        defaults = @registry.get_defaults(:post_tool_use)

        assert_empty(defaults)
      end

      def test_named_hooks_returns_all_names
        @registry.register(:hook1) { |ctx| puts ctx }
        @registry.register(:hook2) { |ctx| puts ctx }
        @registry.register(:hook3) { |ctx| puts ctx }

        names = @registry.named_hooks

        assert_equal(3, names.size)
        assert_includes(names, :hook1)
        assert_includes(names, :hook2)
        assert_includes(names, :hook3)
      end

      def test_registered_predicate
        @registry.register(:my_hook) { |ctx| puts ctx }

        assert(@registry.registered?(:my_hook))
        refute(@registry.registered?(:other_hook))
      end

      def test_valid_events_constant
        expected_events = [
          :swarm_start,
          :swarm_stop,
          :first_message,
          :user_prompt,
          :agent_step,
          :agent_stop,
          :pre_tool_use,
          :post_tool_use,
          :pre_delegation,
          :post_delegation,
          :context_warning,
          :breakpoint_enter,
          :breakpoint_exit,
        ]

        assert_equal(expected_events, Registry::VALID_EVENTS)
      end

      def test_add_default_accepts_all_valid_events
        Registry::VALID_EVENTS.each do |event|
          registry = Registry.new
          registry.add_default(event) { |_ctx| puts "test" }

          defaults = registry.get_defaults(event)

          assert_equal(1, defaults.size)
        end
      end
    end
  end
end
