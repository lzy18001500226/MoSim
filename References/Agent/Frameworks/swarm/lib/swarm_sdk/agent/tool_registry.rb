# frozen_string_literal: true

module SwarmSDK
  module Agent
    # Per-agent tool registry managing available and active tools
    #
    # ## Architecture
    #
    # - **Available tools**: All tool instances the agent CAN use (registry)
    # - **Active tools**: Subset sent to LLM based on skill state
    #
    # ## Thread Safety
    #
    # Registry access is protected by Async::Semaphore for fiber-safe operations.
    #
    # @example Registering tools
    #   registry = ToolRegistry.new
    #   registry.register(Read.new, source: :builtin)
    #   registry.register(delegate_tool, source: :delegation, metadata: { delegate_name: :backend })
    #
    # @example Getting active tools (no skill)
    #   active = registry.active_tools(skill_state: nil)
    #   # Returns ALL available tools
    #
    # @example Getting active tools (with skill)
    #   skill_state = SkillState.new(  # From SwarmMemory plugin
    #     file_path: "skill/audit.md",
    #     tools: ["Read", "Grep"],
    #     permissions: { "Bash" => { deny_commands: ["rm"] } }
    #   )
    #   active = registry.active_tools(skill_state: skill_state)
    #   # Returns: skill's tools + non-removable tools
    class ToolRegistry
      # Tool metadata stored in registry
      #
      # @!attribute instance [r] Tool instance (possibly wrapped with permissions)
      # @!attribute base_instance [r] Unwrapped tool instance (for skill permission override)
      # @!attribute removable [r] Can be deactivated by skills
      # @!attribute source [r] Tool source (:builtin, :delegation, :mcp, :plugin, :custom)
      # @!attribute metadata [r] Source-specific metadata
      ToolEntry = Data.define(:instance, :base_instance, :removable, :source, :metadata)

      def initialize
        @available_tools = {} # String name => ToolEntry
        @mutex = Async::Semaphore.new(1) # Fiber-safe mutex
      end

      # Register a tool in the available tools registry
      #
      # @param tool [RubyLLM::Tool] Tool instance (possibly wrapped)
      # @param base_tool [RubyLLM::Tool, nil] Unwrapped instance (for permission override)
      # @param source [Symbol] Tool source (:builtin, :delegation, :mcp, :plugin, :custom)
      # @param metadata [Hash] Source-specific metadata (server_name, plugin_name, etc.)
      # @return [void]
      #
      # @example Register builtin tool
      #   registry.register(Read.new, source: :builtin)
      #
      # @example Register delegation tool
      #   registry.register(delegate_tool, source: :delegation, metadata: { delegate_name: :backend })
      #
      # @example Register MCP tool
      #   registry.register(mcp_tool, source: :mcp, metadata: { server_name: "codebase" })
      #
      # @example Register with permission wrapper
      #   wrapped_tool = PermissionWrapper.new(base_tool, permissions)
      #   registry.register(wrapped_tool, base_tool: base_tool, source: :builtin)
      def register(tool, base_tool: nil, source:, metadata: {})
        @mutex.acquire do
          # Infer removability from tool class
          removable = tool.respond_to?(:removable?) ? tool.removable? : true

          @available_tools[tool.name] = ToolEntry.new(
            instance: tool,
            base_instance: base_tool || tool, # If no base, use same instance
            removable: removable,
            source: source,
            metadata: metadata,
          )
        end
      end

      # Unregister a tool (for testing/cleanup)
      #
      # @param name [String, Symbol] Tool name
      # @return [ToolEntry, nil] Removed entry
      def unregister(name)
        @mutex.acquire do
          @available_tools.delete(name.to_s)
        end
      end

      # Get active tools based on skill state
      #
      # Returns Hash of tool instances ready for RubyLLM::Chat.
      #
      # Logic:
      # - If skill_state is nil: Return ALL available tools
      # - If skill_state restricts tools: Return skill's tools + non-removable tools
      # - Skill permissions are applied during activation (wrapping base_instance)
      #
      # @param skill_state [Object, nil] Skill state object (from plugin), or nil for all
      # @param tool_configurator [ToolConfigurator, nil] For permission wrapping
      # @param agent_definition [Agent::Definition, nil] For permission wrapping
      # @return [Hash{String => RubyLLM::Tool}] name => instance mapping
      #
      # @example No skill loaded - all tools
      #   registry.active_tools(skill_state: nil)
      #   # => { "Read" => <Read>, "WorkWithBackend" => <Delegate>, ... }
      #
      # @example Skill loaded with focused toolset
      #   registry.active_tools(skill_state: skill_state)
      #   # => { "Read" => <Read>, "WorkWithBackend" => <Delegate>, "Think" => <Think>, "MemoryRead" => <MemoryRead> }
      #   # Includes: requested tools + non-removable tools
      def active_tools(skill_state: nil, tool_configurator: nil, agent_definition: nil)
        @mutex.acquire do
          result = if skill_state&.restricts_tools?
            # Skill loaded with tool restriction - only skill's tools + non-removable
            filtered = {}

            # Always include non-removable tools (use wrapped instance)
            @available_tools.each do |name, entry|
              filtered[name] = entry.instance unless entry.removable
            end

            # Add requested tools from skill
            skill_state.tools.each do |name|
              entry = @available_tools[name.to_s]
              next unless entry

              # Check if skill has custom permissions for this tool
              skill_permissions = skill_state.permissions_for(name)

              if skill_permissions && tool_configurator && agent_definition
                # Skill overrides permissions - wrap the BASE instance
                wrapped = tool_configurator.wrap_tool_with_permissions(
                  entry.base_instance,
                  skill_permissions,
                  agent_definition,
                )
                filtered[name.to_s] = wrapped
              else
                # No skill permission override - use registered instance
                filtered[name.to_s] = entry.instance
              end
            end

            filtered
          else
            # No skill OR skill doesn't restrict tools - all available tools
            @available_tools.transform_values(&:instance)
          end

          result
        end
      end

      # Check if tool exists in registry
      #
      # @param name [String, Symbol] Tool name
      # @return [Boolean]
      def has_tool?(name)
        @available_tools.key?(name.to_s)
      end

      # Get all available tool names
      #
      # @return [Array<String>]
      def tool_names
        @available_tools.keys
      end

      # Get tool entry with metadata
      #
      # @param name [String, Symbol] Tool name
      # @return [ToolEntry, nil]
      def get(name)
        @available_tools[name.to_s]
      end

      # Get all non-removable tool names
      #
      # @return [Array<String>]
      def non_removable_tool_names
        @available_tools.select { |_name, entry| !entry.removable }.keys
      end
    end
  end
end
