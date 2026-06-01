# frozen_string_literal: true

require "test_helper"

module SwarmMemory
  class SkillStateTest < Minitest::Test
    def test_creates_skill_state_with_file_path
      state = SkillState.new(file_path: "skill/debug.md")

      assert_equal("skill/debug.md", state.file_path)
    end

    def test_creates_skill_state_with_tools
      tools = ["Read", "Write", "Grep"]
      state = SkillState.new(file_path: "skill/audit.md", tools: tools)

      assert_equal(tools, state.tools)
    end

    def test_creates_skill_state_with_permissions
      permissions = { "Bash" => { deny_commands: ["rm"] } }
      state = SkillState.new(
        file_path: "skill/safe.md",
        permissions: permissions,
      )

      assert_equal(permissions, state.permissions)
    end

    def test_nil_tools_means_no_restriction
      state = SkillState.new(file_path: "skill/debug.md")

      refute_predicate(
        state,
        :restricts_tools?,
        "nil tools should mean no restriction",
      )
    end

    def test_empty_tools_array_means_no_restriction
      state = SkillState.new(file_path: "skill/minimal.md", tools: [])

      refute_predicate(
        state,
        :restricts_tools?,
        "Empty tools array should mean no restriction (keep all tools)",
      )
    end

    def test_non_empty_tools_array_means_restriction
      state = SkillState.new(
        file_path: "skill/audit.md",
        tools: ["Read", "Grep"],
      )

      assert_predicate(
        state,
        :restricts_tools?,
        "Non-empty tools array should mean restriction",
      )
    end

    def test_allows_tool_when_no_restriction
      state = SkillState.new(file_path: "skill/debug.md")

      assert(
        state.allows_tool?("AnyTool"),
        "Should allow any tool when no restriction",
      )
      assert(
        state.allows_tool?(:AnySymbol),
        "Should allow any tool (symbol) when no restriction",
      )
    end

    def test_allows_tool_when_in_list
      state = SkillState.new(
        file_path: "skill/audit.md",
        tools: ["Read", "Grep"],
      )

      assert(
        state.allows_tool?("Read"),
        "Should allow tool that is in the list",
      )
      assert(
        state.allows_tool?(:Grep),
        "Should allow tool (symbol) that is in the list",
      )
    end

    def test_denies_tool_when_not_in_list
      state = SkillState.new(
        file_path: "skill/audit.md",
        tools: ["Read", "Grep"],
      )

      refute(
        state.allows_tool?("Write"),
        "Should deny tool that is not in the list",
      )
      refute(
        state.allows_tool?(:Bash),
        "Should deny tool (symbol) that is not in the list",
      )
    end

    def test_permissions_for_returns_nil_when_no_permissions
      state = SkillState.new(file_path: "skill/debug.md")

      assert_nil(
        state.permissions_for("Bash"),
        "Should return nil when no permissions set",
      )
    end

    def test_permissions_for_returns_config_when_set
      permissions = { "Bash" => { deny_commands: ["rm"] } }
      state = SkillState.new(
        file_path: "skill/safe.md",
        permissions: permissions,
      )

      assert_equal(
        { deny_commands: ["rm"] },
        state.permissions_for("Bash"),
        "Should return permission config when set",
      )
    end

    def test_permissions_for_supports_symbol_keys
      permissions = { Bash: { deny_commands: ["rm"] } }
      state = SkillState.new(
        file_path: "skill/safe.md",
        permissions: permissions,
      )

      assert_equal(
        { deny_commands: ["rm"] },
        state.permissions_for(:Bash),
        "Should support symbol keys",
      )
    end

    def test_skill_state_is_immutable
      state = SkillState.new(
        file_path: "skill/debug.md",
        tools: ["Read"],
        permissions: { "Bash" => { deny_commands: ["rm"] } },
      )

      assert_predicate(
        state,
        :frozen?,
        "SkillState should be frozen (immutable)",
      )
      assert_predicate(
        state.tools,
        :frozen?,
        "Tools array should be frozen",
      )
      assert_predicate(
        state.permissions,
        :frozen?,
        "Permissions hash should be frozen",
      )
    end

    def test_tools_normalized_to_strings
      state = SkillState.new(
        file_path: "skill/audit.md",
        tools: [:Read, :Write, "Grep"],
      )

      assert_equal(
        ["Read", "Write", "Grep"],
        state.tools,
        "Tools should be normalized to strings",
      )
    end

    def test_defaults_to_empty_permissions
      state = SkillState.new(file_path: "skill/debug.md")

      assert_empty(
        state.permissions,
        "Should default to empty permissions hash",
      )
    end

    def test_tools_can_be_nil
      state = SkillState.new(file_path: "skill/debug.md", tools: nil)

      assert_nil(
        state.tools,
        "Tools can be explicitly nil",
      )
    end

    def test_empty_tools_same_as_nil_tools
      state_nil = SkillState.new(file_path: "skill/debug.md", tools: nil)
      state_empty = SkillState.new(file_path: "skill/minimal.md", tools: [])

      refute_predicate(
        state_nil,
        :restricts_tools?,
        "nil tools should not restrict",
      )
      refute_predicate(
        state_empty,
        :restricts_tools?,
        "empty array should not restrict (same as nil)",
      )
    end
  end
end
