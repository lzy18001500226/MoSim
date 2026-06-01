# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Tools
    class BaseTest < Minitest::Test
      # Test tool classes for various scenarios
      class RemovableTool < SwarmSDK::Tools::Base
        def name
          "RemovableTool"
        end

        def description
          "A tool that can be removed"
        end

        def execute
          "executed"
        end
      end

      class NonRemovableTool < SwarmSDK::Tools::Base
        removable false

        def name
          "NonRemovableTool"
        end

        def description
          "A tool that cannot be removed"
        end

        def execute
          "executed"
        end
      end

      class ExplicitlyRemovableTool < SwarmSDK::Tools::Base
        removable true

        def name
          "ExplicitlyRemovableTool"
        end

        def description
          "A tool that is explicitly removable"
        end

        def execute
          "executed"
        end
      end

      def test_default_removability_is_true
        tool = RemovableTool.new

        assert_predicate(tool, :removable?, "Tools should be removable by default")
        assert_predicate(RemovableTool, :removable?, "Tool class should be removable by default")
      end

      def test_can_mark_tool_as_non_removable
        tool = NonRemovableTool.new

        refute_predicate(tool, :removable?, "Tool marked with removable false should not be removable")
        refute_predicate(NonRemovableTool, :removable?, "Tool class marked with removable false should not be removable")
      end

      def test_can_explicitly_mark_tool_as_removable
        tool = ExplicitlyRemovableTool.new

        assert_predicate(tool, :removable?, "Tool marked with removable true should be removable")
        assert_predicate(ExplicitlyRemovableTool, :removable?, "Tool class marked with removable true should be removable")
      end

      def test_removability_is_class_level_attribute
        # Create instances to verify class-level attribute
        tool1 = RemovableTool.new
        tool2 = RemovableTool.new

        assert_equal(
          tool1.removable?,
          tool2.removable?,
          "Removability should be consistent across instances",
        )
      end

      def test_inherits_from_ruby_llm_tool
        tool = RemovableTool.new

        assert_kind_of(
          RubyLLM::Tool,
          tool,
          "BaseTool should inherit from RubyLLM::Tool",
        )
      end

      def test_tool_can_execute
        tool = RemovableTool.new

        assert_equal(
          "executed",
          tool.execute,
          "Tool should be able to execute",
        )
      end

      def test_non_removable_tool_can_execute
        tool = NonRemovableTool.new

        assert_equal(
          "executed",
          tool.execute,
          "Non-removable tool should be able to execute",
        )
      end
    end
  end
end
