# frozen_string_literal: true

module SwarmMemory
  # Immutable representation of a loaded skill's state
  #
  # This object encapsulates all skill-related state for clean management.
  # Immutability prevents accidental mutation bugs during activation.
  #
  # @example Creating skill state
  #   state = SkillState.new(
  #     file_path: "skill/security/audit.md",
  #     tools: ["Read", "Grep", "WorkWithBackend"],
  #     permissions: { "Bash" => { deny_commands: ["rm"] } }
  #   )
  #
  # @example Checking if skill restricts tools
  #   state.restricts_tools?  # => true (has tool list)
  #
  # @example Checking if tool is allowed
  #   state.allows_tool?("Read")  # => true
  #   state.allows_tool?("Write") # => false
  class SkillState
    attr_reader :file_path, :tools, :permissions

    # Create a new SkillState
    #
    # @param file_path [String] Path to the skill in memory
    # @param tools [Array<String>, nil] Required tools (nil = no tool restriction)
    # @param permissions [Hash] Tool permission overrides
    #
    # @example No tool restriction
    #   SkillState.new(file_path: "skill/debug.md")  # All tools available
    #
    # @example Specific tools only
    #   SkillState.new(
    #     file_path: "skill/audit.md",
    #     tools: ["Read", "Grep"]
    #   )
    #
    # @example With permissions
    #   SkillState.new(
    #     file_path: "skill/safe.md",
    #     tools: ["Bash"],
    #     permissions: { "Bash" => { deny_commands: ["rm", "sudo"] } }
    #   )
    def initialize(file_path:, tools: nil, permissions: {})
      @file_path = file_path
      @tools = tools&.map(&:to_s)&.freeze # Normalize and freeze
      @permissions = permissions.freeze
      freeze # Make entire object immutable
    end

    # Check if skill specifies a tool restriction
    #
    # Returns true if the skill has a NON-EMPTY tools array.
    # Both nil and empty array mean "no restriction" (don't swap tools).
    #
    # @return [Boolean] True if skill restricts toolset
    #
    # @example No restriction (nil)
    #   state = SkillState.new(file_path: "skill/debug.md")
    #   state.restricts_tools?  # => false (nil = no restriction)
    #
    # @example No restriction (empty array)
    #   state = SkillState.new(file_path: "skill/minimal.md", tools: [])
    #   state.restricts_tools?  # => false (empty = no restriction)
    #
    # @example Restriction (specific tools)
    #   state = SkillState.new(file_path: "skill/audit.md", tools: ["Read"])
    #   state.restricts_tools?  # => true (has specific tools)
    def restricts_tools?
      !@tools.nil? && !@tools.empty?
    end

    # Check if a specific tool is allowed by this skill
    #
    # If the skill has no tool restriction (tools is nil), all tools are allowed.
    # If the skill has a tool list, only tools in that list are allowed.
    #
    # @param name [String, Symbol] Tool name
    # @return [Boolean] True if tool is in skill's list (or no restriction)
    #
    # @example No restriction
    #   state = SkillState.new(file_path: "skill/debug.md")
    #   state.allows_tool?("AnyTool")  # => true (no restriction)
    #
    # @example Restricted
    #   state = SkillState.new(file_path: "skill/audit.md", tools: ["Read"])
    #   state.allows_tool?("Read")   # => true
    #   state.allows_tool?("Write")  # => false
    def allows_tool?(name)
      @tools.nil? || @tools.include?(name.to_s)
    end

    # Get permission config for a tool
    #
    # Returns the permission configuration hash for a specific tool,
    # or nil if no custom permissions are set.
    #
    # @param name [String, Symbol] Tool name
    # @return [Hash, nil] Permission config or nil
    #
    # @example No custom permissions
    #   state = SkillState.new(file_path: "skill/debug.md")
    #   state.permissions_for("Bash")  # => nil
    #
    # @example Custom permissions
    #   state = SkillState.new(
    #     file_path: "skill/safe.md",
    #     permissions: { "Bash" => { deny_commands: ["rm"] } }
    #   )
    #   state.permissions_for("Bash")  # => { deny_commands: ["rm"] }
    def permissions_for(name)
      @permissions[name.to_s] || @permissions[name.to_sym]
    end
  end
end
