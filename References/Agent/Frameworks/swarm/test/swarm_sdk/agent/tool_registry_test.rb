# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Agent
    class ToolRegistryTest < Minitest::Test
      # Mock tools for testing
      class MockRemovableTool < SwarmSDK::Tools::Base
        def name
          "MockRemovableTool"
        end

        def description
          "A removable tool"
        end

        def execute
          "executed"
        end
      end

      class MockNonRemovableTool < SwarmSDK::Tools::Base
        removable false

        def name
          "MockNonRemovableTool"
        end

        def description
          "A non-removable tool"
        end

        def execute
          "executed"
        end
      end

      def setup
        @registry = ToolRegistry.new
      end

      def test_registers_tool_with_metadata
        tool = MockRemovableTool.new

        @registry.register(tool, source: :builtin, metadata: { test: true })

        assert(@registry.has_tool?("MockRemovableTool"))
        entry = @registry.get("MockRemovableTool")

        assert_equal(tool, entry.instance)
        assert_equal(:builtin, entry.source)
        assert_equal({ test: true }, entry.metadata)
      end

      def test_infers_removability_from_tool_class
        removable_tool = MockRemovableTool.new
        non_removable_tool = MockNonRemovableTool.new

        @registry.register(removable_tool, source: :builtin)
        @registry.register(non_removable_tool, source: :builtin)

        removable_entry = @registry.get("MockRemovableTool")
        non_removable_entry = @registry.get("MockNonRemovableTool")

        assert_predicate(removable_entry, :removable)
        refute_predicate(non_removable_entry, :removable)
      end

      def test_stores_base_instance_for_permission_override
        base_tool = MockRemovableTool.new
        wrapped_tool = Object.new
        def wrapped_tool.name
          "MockRemovableTool"
        end

        def wrapped_tool.removable?
          true
        end

        @registry.register(wrapped_tool, base_tool: base_tool, source: :builtin)

        entry = @registry.get("MockRemovableTool")

        assert_equal(wrapped_tool, entry.instance)
        assert_equal(base_tool, entry.base_instance)
      end

      def test_unregister_removes_tool
        tool = MockRemovableTool.new
        @registry.register(tool, source: :builtin)

        assert(@registry.has_tool?("MockRemovableTool"))

        @registry.unregister("MockRemovableTool")

        refute(@registry.has_tool?("MockRemovableTool"))
      end

      def test_tool_names_returns_all_registered_tool_names
        tool1 = MockRemovableTool.new
        tool2 = MockNonRemovableTool.new

        @registry.register(tool1, source: :builtin)
        @registry.register(tool2, source: :builtin)

        names = @registry.tool_names

        assert_includes(names, "MockRemovableTool")
        assert_includes(names, "MockNonRemovableTool")
      end

      def test_non_removable_tool_names_returns_only_non_removable
        removable = MockRemovableTool.new
        non_removable = MockNonRemovableTool.new

        @registry.register(removable, source: :builtin)
        @registry.register(non_removable, source: :builtin)

        non_removable_names = @registry.non_removable_tool_names

        assert_includes(non_removable_names, "MockNonRemovableTool")
        refute_includes(non_removable_names, "MockRemovableTool")
      end

      def test_active_tools_returns_all_when_no_skill
        tool1 = MockRemovableTool.new
        tool2 = MockNonRemovableTool.new

        @registry.register(tool1, source: :builtin)
        @registry.register(tool2, source: :builtin)

        active = @registry.active_tools(skill_state: nil)

        assert_equal(2, active.size)
        assert_equal(tool1, active["MockRemovableTool"])
        assert_equal(tool2, active["MockNonRemovableTool"])
      end

      def test_active_tools_with_skill_returns_skill_tools_plus_non_removable
        removable1 = MockRemovableTool.new
        removable2 = Object.new
        def removable2.name
          "OtherRemovableTool"
        end

        def removable2.removable?
          true
        end
        non_removable = MockNonRemovableTool.new

        @registry.register(removable1, source: :builtin)
        @registry.register(removable2, source: :builtin)
        @registry.register(non_removable, source: :builtin)

        # Skill only wants MockRemovableTool
        skill_state = SwarmMemory::SkillState.new(
          file_path: "skill/test.md",
          tools: ["MockRemovableTool"],
        )

        active = @registry.active_tools(skill_state: skill_state)

        assert_equal(2, active.size)
        assert_includes(active, "MockRemovableTool")
        assert_includes(active, "MockNonRemovableTool")
        refute_includes(active, "OtherRemovableTool")
      end

      def test_active_tools_with_nil_tools_returns_all
        tool1 = MockRemovableTool.new
        tool2 = MockNonRemovableTool.new

        @registry.register(tool1, source: :builtin)
        @registry.register(tool2, source: :builtin)

        # Skill with nil tools (no restriction)
        skill_state = SwarmMemory::SkillState.new(file_path: "skill/test.md", tools: nil)

        active = @registry.active_tools(skill_state: skill_state)

        assert_equal(2, active.size)
      end

      def test_active_tools_with_empty_tools_returns_all
        removable = MockRemovableTool.new
        non_removable = MockNonRemovableTool.new

        @registry.register(removable, source: :builtin)
        @registry.register(non_removable, source: :builtin)

        # Skill with empty tools (no restriction - same as nil)
        skill_state = SwarmMemory::SkillState.new(file_path: "skill/test.md", tools: [])

        active = @registry.active_tools(skill_state: skill_state)

        assert_equal(2, active.size)
        assert_includes(active, "MockNonRemovableTool")
        assert_includes(active, "MockRemovableTool")
      end

      def test_active_tools_skips_tools_not_in_registry
        tool = MockRemovableTool.new
        @registry.register(tool, source: :builtin)

        # Skill wants a tool that doesn't exist
        skill_state = SwarmMemory::SkillState.new(
          file_path: "skill/test.md",
          tools: ["MockRemovableTool", "NonExistentTool"],
        )

        active = @registry.active_tools(skill_state: skill_state)

        assert_includes(active, "MockRemovableTool")
        refute_includes(active, "NonExistentTool")
      end

      def test_active_tools_with_permission_override
        # Mock wrapped tool class
        Class.new do
          def initialize(base_tool, permissions)
            @base_tool = base_tool
            @permissions = permissions
          end

          def name
            "MockRemovableTool"
          end

          def removable?
            true
          end
        end

        # Mock tool configurator
        tool_configurator = Object.new
        def tool_configurator.wrap_tool_with_permissions(base_tool, permissions, _agent_definition)
          # Return a new instance that's different from base_tool
          wrapped = Object.new
          def wrapped.name
            "MockRemovableTool"
          end

          def wrapped.wrapped?
            true
          end
          wrapped
        end

        # Mock agent definition
        agent_definition = Object.new

        base_tool = MockRemovableTool.new
        @registry.register(base_tool, base_tool: base_tool, source: :builtin)

        skill_state = SwarmMemory::SkillState.new(
          file_path: "skill/test.md",
          tools: ["MockRemovableTool"],
          permissions: { "MockRemovableTool" => { deny_commands: ["rm"] } },
        )

        active = @registry.active_tools(
          skill_state: skill_state,
          tool_configurator: tool_configurator,
          agent_definition: agent_definition,
        )

        # Should have wrapped tool, not base tool
        wrapped = active["MockRemovableTool"]

        refute_equal(base_tool, wrapped)
        assert_respond_to(wrapped, :wrapped?)
      end

      def test_active_tools_without_permission_override_uses_registered_instance
        base_tool = MockRemovableTool.new
        wrapped_tool = Object.new
        def wrapped_tool.name
          "MockRemovableTool"
        end

        def wrapped_tool.removable?
          true
        end

        @registry.register(wrapped_tool, base_tool: base_tool, source: :builtin)

        skill_state = SwarmMemory::SkillState.new(
          file_path: "skill/test.md",
          tools: ["MockRemovableTool"],
          # No permissions - should use registered (already wrapped) instance
        )

        active = @registry.active_tools(skill_state: skill_state)

        # Should use the registered wrapped instance
        assert_equal(wrapped_tool, active["MockRemovableTool"])
      end
    end
  end
end
