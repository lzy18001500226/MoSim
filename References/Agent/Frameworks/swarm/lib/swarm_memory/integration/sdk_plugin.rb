# frozen_string_literal: true

module SwarmMemory
  module Integration
    # SwarmSDK plugin implementation for SwarmMemory
    #
    # This plugin integrates SwarmMemory with SwarmSDK, providing:
    # - Persistent memory storage for agents
    # - Memory tools (MemoryWrite, MemoryRead, MemoryEdit, etc.)
    # - LoadSkill tool for dynamic tool swapping
    # - System prompt contributions for memory guidance
    # - Semantic skill discovery on user messages
    #
    # The plugin automatically registers itself when SwarmMemory is loaded
    # alongside SwarmSDK.
    class SDKPlugin < SwarmSDK::Plugin
      def initialize
        super
        # Track storages for each agent: { agent_name => storage }
        # Needed for semantic skill discovery in on_user_message
        @storages = {}
        # Track memory mode for each agent: { agent_name => mode }
        # Modes: :read_write (default), :read_only, :full_access
        @modes = {}
        # Track threshold configuration for each agent: { agent_name => config }
        # Enables per-adapter threshold tuning with ENV fallback
        @threshold_configs = {}
      end

      # Plugin identifier
      #
      # @return [Symbol] Plugin name
      def name
        :memory
      end

      # Tools provided by this plugin
      #
      # Returns all memory tools for PluginRegistry mapping.
      # Tools are auto-registered by ToolConfigurator, then filtered
      # by mode in on_agent_initialized using remove_tool.
      #
      # Note: LoadSkill is NOT included here because it requires special handling.
      # It's registered separately in on_agent_initialized lifecycle hook because
      # it needs chat, tool_configurator, and agent_definition parameters.
      #
      # @return [Array<Symbol>] All memory tool names
      def tools
        [
          :MemoryRead,
          :MemoryGlob,
          :MemoryGrep,
          :MemorySearch,
          :MemoryWrite,
          :MemoryEdit,
          :MemoryDelete,
          :MemoryDefrag,
        ]
      end

      # Get tools for a specific mode
      #
      # @param mode [Symbol] Memory mode
      # @return [Array<Symbol>] Tool names for this mode
      def tools_for_mode(mode)
        case mode
        when :read_only
          # Read-only tools for Q&A agents
          [:MemoryRead, :MemoryGlob, :MemoryGrep, :MemorySearch]
        when :read_write
          # Read + Write + Edit for learning agents (need edit for corrections)
          [:MemoryRead, :MemoryGlob, :MemoryGrep, :MemorySearch, :MemoryWrite, :MemoryEdit]
        when :full_access
          # All tools for knowledge extraction and management
          [
            :MemoryRead,
            :MemoryGlob,
            :MemoryGrep,
            :MemorySearch,
            :MemoryWrite,
            :MemoryEdit,
            :MemoryDelete,
            :MemoryDefrag,
          ]
        else
          # Default to read_write
          [:MemoryRead, :MemoryGlob, :MemoryGrep, :MemorySearch, :MemoryWrite, :MemoryEdit]
        end
      end

      # Create a tool instance
      #
      # @param tool_name [Symbol] Tool name
      # @param context [Hash] Creation context with :storage, :agent_name, :chat, etc.
      # @return [RubyLLM::Tool] Tool instance
      def create_tool(tool_name, context)
        storage = context[:storage]
        agent_name = context[:agent_name]

        # Delegate to SwarmMemory's tool factory
        SwarmMemory.create_tool(tool_name, storage: storage, agent_name: agent_name)
      end

      # Create plugin storage for an agent
      #
      # @param agent_name [Symbol] Agent identifier
      # @param config [Object] Memory configuration (MemoryConfig or Hash)
      # @return [Core::Storage] Storage instance with embeddings enabled
      def create_storage(agent_name:, config:)
        # Extract adapter type and options from config
        adapter_type, adapter_options = if config.respond_to?(:adapter_type)
          # MemoryConfig object (from DSL)
          [config.adapter_type, config.adapter_options]
        elsif config.is_a?(Hash)
          # Hash (from YAML) - symbolize keys for adapter compatibility
          adapter = (config[:adapter] || config["adapter"] || :filesystem).to_sym
          options = config.reject { |k, _v| [:adapter, "adapter", :mode, "mode"].include?(k) }
          # Symbolize keys so adapter receives keyword arguments correctly
          symbolized_options = options.transform_keys { |k| k.to_s.to_sym }
          [adapter, symbolized_options]
        else
          raise SwarmSDK::ConfigurationError, "Invalid memory configuration for #{agent_name}"
        end

        # Get adapter class from registry
        begin
          adapter_class = SwarmMemory.adapter_for(adapter_type)
        rescue ArgumentError => e
          raise SwarmSDK::ConfigurationError, "#{e.message} for agent #{agent_name}"
        end

        # Extract hybrid search weights and other SDK-level config (before passing to adapter)
        # Keys are already symbolized at this point
        semantic_weight = adapter_options.delete(:semantic_weight)
        keyword_weight = adapter_options.delete(:keyword_weight)

        # Remove other SDK-level threshold configs that shouldn't go to adapter
        adapter_options.delete(:discovery_threshold)
        adapter_options.delete(:discovery_threshold_short)
        adapter_options.delete(:adaptive_word_cutoff)

        # Instantiate adapter with options (weights removed, adapter doesn't need them)
        # Note: Adapter is responsible for validating its own requirements
        begin
          adapter = adapter_class.new(**adapter_options)
        rescue ArgumentError => e
          raise SwarmSDK::ConfigurationError,
            "Failed to initialize #{adapter_type} adapter for #{agent_name}: #{e.message}"
        end

        # Create embedder for semantic search
        embedder = Embeddings::InformersEmbedder.new

        # Create storage with embedder and hybrid search weights
        Core::Storage.new(
          adapter: adapter,
          embedder: embedder,
          semantic_weight: semantic_weight,
          keyword_weight: keyword_weight,
        )
      end

      # Parse memory configuration
      #
      # @param raw_config [Object] Raw config (MemoryConfig or Hash)
      # @return [Object] Parsed configuration
      def parse_config(raw_config)
        # Already parsed by Agent::Definition, just return as-is
        raw_config
      end

      # Contribute to agent system prompt
      #
      # @param agent_definition [Agent::Definition] Agent definition
      # @param storage [Core::Storage, nil] Storage instance (may be nil during prompt building)
      # @return [String] Memory prompt contribution
      def system_prompt_contribution(agent_definition:, storage:)
        # Extract mode from memory config
        memory_config = agent_definition.plugin_config(:memory)
        mode = if memory_config.is_a?(SwarmMemory::DSL::MemoryConfig)
          memory_config.mode # MemoryConfig object from DSL
        elsif memory_config.respond_to?(:mode)
          memory_config.mode # Other object with mode method
        elsif memory_config.is_a?(Hash)
          (memory_config[:mode] || memory_config["mode"] || :read_write).to_sym
        else
          :read_write # Default mode
        end

        # Select prompt template based on mode
        prompt_filename = case mode
        when :read_only then "memory_read_only.md.erb"
        when :full_access then "memory_full_access.md.erb"
        else "memory_read_write.md.erb" # Default
        end

        memory_prompt_path = File.expand_path("../prompts/#{prompt_filename}", __dir__)
        template_content = File.read(memory_prompt_path)

        # Render with agent_definition binding
        ERB.new(template_content).result(agent_definition.instance_eval { binding })
      end

      # Check if memory is configured for this agent
      #
      # Delegates adapter-specific validation to the adapter itself.
      # Filesystem adapter requires 'directory', custom adapters may use other keys.
      #
      # @param agent_definition [Agent::Definition] Agent definition
      # @return [Boolean] True if agent has valid memory configuration
      def memory_configured?(agent_definition)
        memory_config = agent_definition.plugin_config(:memory)
        return false if memory_config.nil?

        # MemoryConfig object (from DSL) - delegates to its enabled? method
        return memory_config.enabled? if memory_config.respond_to?(:enabled?)

        # Hash (from YAML)
        return false unless memory_config.is_a?(Hash)
        return false if memory_config.empty?

        adapter = (memory_config[:adapter] || memory_config["adapter"] || :filesystem).to_sym

        case adapter
        when :filesystem
          # Filesystem adapter requires directory
          directory = memory_config[:directory] || memory_config["directory"]
          !directory.nil? && !directory.to_s.strip.empty?
        else
          # Custom adapters: presence of config is sufficient
          # Adapter will validate its own requirements during initialization
          true
        end
      end

      # Contribute to agent serialization
      #
      # Preserves memory configuration when agents are cloned (e.g., in Workflow).
      # This allows memory configuration to persist across node transitions.
      #
      # @param agent_definition [Agent::Definition] Agent definition
      # @return [Hash] Memory config to include in to_h
      def serialize_config(agent_definition:)
        memory_config = agent_definition.plugin_config(:memory)
        return {} unless memory_config

        { memory: memory_config }
      end

      # Snapshot plugin-specific state for an agent
      #
      # Captures memory read tracking state for session persistence.
      # This allows agents to remember which memory entries they've read
      # across sessions.
      #
      # @param agent_name [Symbol] Agent identifier
      # @return [Hash] Plugin-specific state
      def snapshot_agent_state(agent_name)
        entries_with_digests = Core::StorageReadTracker.get_read_entries(agent_name)
        return {} if entries_with_digests.empty?

        { read_entries: entries_with_digests }
      end

      # Restore plugin-specific state for an agent
      #
      # Restores memory read tracking state from snapshot.
      # This is idempotent - calling multiple times with same state
      # produces the same result.
      #
      # @param agent_name [Symbol] Agent identifier
      # @param state [Hash] Previously snapshotted state (with symbol keys)
      # @return [void]
      def restore_agent_state(agent_name, state)
        entries = state[:read_entries] || state["read_entries"]
        return unless entries

        Core::StorageReadTracker.restore_read_entries(agent_name, entries)
      end

      # Get digest for a memory tool result
      #
      # Returns the digest for a MemoryRead tool call, enabling change detection
      # hooks to know if a memory entry has been modified since last read.
      #
      # @param agent_name [Symbol] Agent identifier
      # @param tool_name [String] Name of the tool
      # @param path [String] Path of the memory entry
      # @return [String, nil] Digest string or nil if not a memory tool
      def get_tool_result_digest(agent_name:, tool_name:, path:)
        return unless tool_name == "MemoryRead"

        Core::StorageReadTracker.get_read_entries(agent_name)[path]
      end

      # Translate YAML configuration into DSL calls
      #
      # Called during YAML-to-DSL translation. Handles memory-specific YAML
      # configuration and translates it into DSL method calls on the builder.
      #
      # @param builder [Agent::Builder] Builder instance (self in DSL context)
      # @param agent_config [Hash] Full agent config from YAML
      # @return [void]
      def translate_yaml_config(builder, agent_config)
        memory_config = agent_config[:memory]
        return unless memory_config

        builder.instance_eval do
          memory do
            # Standard options
            directory(memory_config[:directory]) if memory_config[:directory]
            adapter(memory_config[:adapter]) if memory_config[:adapter]
            mode(memory_config[:mode]) if memory_config[:mode]

            # Pass through all custom adapter options
            # Handle both symbol and string keys (YAML may have either)
            standard_keys = [
              :directory,
              :adapter,
              :mode,
              "directory",
              "adapter",
              "mode",
            ]
            custom_keys = memory_config.keys - standard_keys
            custom_keys.each do |key|
              option(key.to_sym, memory_config[key]) # Normalize to symbol
            end
          end
        end
      end

      # Lifecycle: Agent initialized
      #
      # Filters tools by mode (removing non-mode tools), registers LoadSkill,
      # and marks memory tools as immutable.
      #
      # LoadSkill needs special handling because it requires chat, tool_configurator,
      # and agent_definition to perform dynamic tool swapping.
      #
      # @param agent_name [Symbol] Agent identifier
      # @param agent [Agent::Chat] Chat instance
      # @param context [Hash] Initialization context
      def on_agent_initialized(agent_name:, agent:, context:)
        storage = context[:storage]
        agent_definition = context[:agent_definition]
        tool_configurator = context[:tool_configurator]

        return unless storage # Only proceed if memory is enabled for this agent

        # Extract mode from memory config
        memory_config = agent_definition.plugin_config(:memory)
        mode = if memory_config.is_a?(SwarmMemory::DSL::MemoryConfig)
          memory_config.mode # MemoryConfig object from DSL
        elsif memory_config.respond_to?(:mode)
          memory_config.mode # Other object with mode method
        elsif memory_config.is_a?(Hash)
          (memory_config[:mode] || memory_config["mode"] || :interactive).to_sym
        else
          :interactive # Default
        end

        # V7.0: Extract base name for storage tracking (delegation instances share storage)
        base_name = agent_name.to_s.split("@").first.to_sym

        # Store storage and mode using BASE NAME
        @storages[base_name] = storage # ← Changed from agent_name to base_name
        @modes[base_name] = mode # ← Changed from agent_name to base_name
        @threshold_configs[base_name] = extract_threshold_config(memory_config)

        # NOTE: Memory tools are already registered by ToolConfigurator.register_plugin_tools
        # We need to unregister tools not allowed in this mode (Plan 025)

        all_memory_tools = tools
        allowed_tools = tools_for_mode(mode)
        tools_to_remove = all_memory_tools - allowed_tools

        # Unregister tools not allowed in this mode
        tools_to_remove.each do |tool_name|
          agent.tool_registry.unregister(tool_name.to_s)
        end

        # Create and register LoadSkill tool (NOT for read_only mode)
        unless mode == :read_only
          load_skill_tool = SwarmMemory.create_tool(
            :LoadSkill,
            storage: storage,
            agent_name: agent_name,
            chat: agent,
            tool_configurator: tool_configurator,
            agent_definition: agent_definition,
          )

          # Register in tool registry (Plan 025)
          agent.tool_registry.register(
            load_skill_tool,
            source: :plugin,
            metadata: { plugin_name: :memory, mode: mode },
          )
        end

        # NOTE: No need to mark tools immutable - they declare removable? themselves (Plan 025)
      end

      # Lifecycle: User message
      #
      # Performs TWO semantic searches:
      # 1. Skills - For loadable procedures with LoadSkill
      # 2. Memories - For concepts/facts/experiences that provide context
      #
      # Returns system reminders for both if high-confidence matches found.
      #
      # @param agent_name [Symbol] Agent identifier
      # @param prompt [String] User's message
      # @param is_first_message [Boolean] True if first message
      # @return [Array<String>] System reminders (0-2 reminders)
      def on_user_message(agent_name:, prompt:, is_first_message:)
        # V7.0: Extract base name for storage lookup (delegation instances share storage)
        base_name = agent_name.to_s.split("@").first.to_sym
        storage = @storages[base_name] # ← Changed from agent_name to base_name
        config = @threshold_configs[base_name] || {}

        return [] unless storage&.semantic_index
        return [] if prompt.nil? || prompt.empty?

        # Adaptive threshold based on query length
        # Short queries use lower threshold as they have less semantic richness
        # Fallback chain: config → ENV → default
        word_count = prompt.split.size
        word_cutoff = config[:adaptive_word_cutoff] ||
          ENV["SWARM_MEMORY_ADAPTIVE_WORD_CUTOFF"]&.to_i ||
          10

        threshold = if word_count < word_cutoff
          config[:discovery_threshold_short] ||
            ENV["SWARM_MEMORY_DISCOVERY_THRESHOLD_SHORT"]&.to_f ||
            0.25
        else
          config[:discovery_threshold] ||
            ENV["SWARM_MEMORY_DISCOVERY_THRESHOLD"]&.to_f ||
            0.35
        end
        reminders = []

        # Run both searches in parallel with Async
        Async do |task|
          # Search 1: Skills (type = "skill")
          skills_task = task.async do
            storage.semantic_index.search(
              query: prompt,
              top_k: 3,
              threshold: threshold,
              filter: { "type" => "skill" },
            )
          end

          # Search 2: All results (for memories + logging)
          all_results_task = task.async do
            storage.semantic_index.search(
              query: prompt,
              top_k: 10,
              threshold: 0.0, # Get all for logging
              filter: nil,
            )
          end

          # Wait for both searches to complete
          skills = skills_task.wait
          all_results = all_results_task.wait

          # Filter to concepts, facts, experiences (not skills)
          memories = all_results
            .select { |r| ["concept", "fact", "experience"].include?(r.dig(:metadata, "type")) }
            .select { |r| r[:similarity] >= threshold }
            .take(3)

          # Emit log events (include word count for adaptive threshold analysis)
          search_context = { threshold: threshold, word_count: word_count, word_cutoff: word_cutoff }
          emit_skill_search_log(agent_name, prompt, skills, all_results, search_context)
          emit_memory_search_log(agent_name, prompt, memories, all_results, search_context)

          # Build skill reminder if found
          if skills.any?
            reminders << build_skill_discovery_reminder(skills)
          end

          # Build memory reminder if found
          if memories.any?
            reminders << build_memory_discovery_reminder(memories)
          end
        end.wait

        reminders
      end

      private

      # Emit log event for semantic skill search
      #
      # @param agent_name [Symbol] Agent identifier
      # @param prompt [String] User's message
      # @param skills [Array<Hash>] Found skills (filtered)
      # @param all_results [Array<Hash>] All search results (unfiltered)
      # @param search_context [Hash] Search context with :threshold and :word_count
      # @return [void]
      def emit_skill_search_log(agent_name, prompt, skills, all_results, search_context)
        return unless SwarmSDK::LogStream.enabled?

        threshold = search_context[:threshold]
        word_count = search_context[:word_count]
        word_cutoff = search_context[:word_cutoff]

        # Include top 5 results for debugging (even if below threshold or wrong type)
        all_entries_debug = all_results.take(5).map do |result|
          {
            path: result[:path],
            title: result[:title],
            hybrid_score: result[:similarity].round(3),
            semantic_score: result[:semantic_score]&.round(3),
            keyword_score: result[:keyword_score]&.round(3),
            type: result.dig(:metadata, "type"),
            tags: result.dig(:metadata, "tags"),
          }
        end

        # Get actual weights being used (fallback chain: config → ENV → defaults)
        base_name = agent_name.to_s.split("@").first.to_sym
        config = @threshold_configs[base_name] || {}
        semantic_weight = config[:semantic_weight] ||
          ENV["SWARM_MEMORY_SEMANTIC_WEIGHT"]&.to_f ||
          0.5
        keyword_weight = config[:keyword_weight] ||
          ENV["SWARM_MEMORY_KEYWORD_WEIGHT"]&.to_f ||
          0.5

        SwarmSDK::LogStream.emit(
          type: "semantic_skill_search",
          agent: agent_name,
          query: prompt,
          query_word_count: word_count,
          threshold: threshold,
          threshold_type: word_count < word_cutoff ? "short_query" : "normal_query",
          adaptive_cutoff: word_cutoff,
          skills_found: skills.size,
          total_entries_searched: all_results.size,
          search_mode: "hybrid",
          weights: { semantic: semantic_weight, keyword: keyword_weight },
          skills: skills.map do |skill|
            {
              path: skill[:path],
              title: skill[:title],
              hybrid_score: skill[:similarity].round(3),
              semantic_score: skill[:semantic_score]&.round(3),
              keyword_score: skill[:keyword_score]&.round(3),
            }
          end,
          debug_top_results: all_entries_debug,
        )
      end

      # Emit log event for semantic memory search
      #
      # @param agent_name [Symbol] Agent identifier
      # @param prompt [String] User's message
      # @param memories [Array<Hash>] Found memories (concepts/facts/experiences)
      # @param all_results [Array<Hash>] All search results (unfiltered)
      # @param search_context [Hash] Search context with :threshold and :word_count
      # @return [void]
      def emit_memory_search_log(agent_name, prompt, memories, all_results, search_context)
        return unless SwarmSDK::LogStream.enabled?

        threshold = search_context[:threshold]
        word_count = search_context[:word_count]
        word_cutoff = search_context[:word_cutoff]

        # Filter all_results to only concept/fact/experience types for debug output
        memory_entries = all_results.select do |r|
          ["concept", "fact", "experience"].include?(r.dig(:metadata, "type"))
        end

        # Include top 10 memory entries for debugging (even if below threshold)
        debug_all_memories = memory_entries.take(10).map do |result|
          {
            path: result[:path],
            title: result[:title],
            hybrid_score: result[:similarity].round(3),
            semantic_score: result[:semantic_score]&.round(3),
            keyword_score: result[:keyword_score]&.round(3),
            type: result.dig(:metadata, "type"),
            tags: result.dig(:metadata, "tags"),
            domain: result.dig(:metadata, "domain"),
          }
        end

        # Get actual weights being used (fallback chain: config → ENV → defaults)
        base_name = agent_name.to_s.split("@").first.to_sym
        config = @threshold_configs[base_name] || {}
        semantic_weight = config[:semantic_weight] ||
          ENV["SWARM_MEMORY_SEMANTIC_WEIGHT"]&.to_f ||
          0.5
        keyword_weight = config[:keyword_weight] ||
          ENV["SWARM_MEMORY_KEYWORD_WEIGHT"]&.to_f ||
          0.5

        SwarmSDK::LogStream.emit(
          type: "semantic_memory_search",
          agent: agent_name,
          query: prompt,
          query_word_count: word_count,
          threshold: threshold,
          threshold_type: word_count < word_cutoff ? "short_query" : "normal_query",
          adaptive_cutoff: word_cutoff,
          memories_found: memories.size,
          total_memory_entries_searched: memory_entries.size,
          search_mode: "hybrid",
          weights: { semantic: semantic_weight, keyword: keyword_weight },
          memories: memories.map do |memory|
            {
              path: memory[:path],
              title: memory[:title],
              type: memory.dig(:metadata, "type"),
              hybrid_score: memory[:similarity].round(3),
              semantic_score: memory[:semantic_score]&.round(3),
              keyword_score: memory[:keyword_score]&.round(3),
            }
          end,
          debug_top_results: debug_all_memories,
        )
      end

      # Build system reminder for discovered skills
      #
      # @param skills [Array<Hash>] Skill search results
      # @return [String] Formatted system reminder
      def build_skill_discovery_reminder(skills)
        reminder = "<system-reminder>\n"
        reminder += "🎯 Found #{skills.size} skill(s) in memory that may be relevant:\n\n"

        skills.each do |skill|
          match_pct = (skill[:similarity] * 100).round
          reminder += "**#{skill[:title]}** (#{match_pct}% match)\n"
          reminder += "Path: `#{skill[:path]}`\n"
          reminder += "To use: `LoadSkill(file_path: \"#{skill[:path]}\")`\n\n"
        end

        reminder += "**If a skill matches your task:** Load it to get step-by-step instructions and adapted tools.\n"
        reminder += "**If none match (false positive):** Ignore and proceed normally.\n"
        reminder += "</system-reminder>"

        reminder
      end

      # Build system reminder for discovered memories
      #
      # @param memories [Array<Hash>] Memory search results (concepts/facts/experiences)
      # @return [String] Formatted system reminder
      def build_memory_discovery_reminder(memories)
        reminder = "<system-reminder>\n"
        reminder += "📚 Found #{memories.size} memory entr#{memories.size == 1 ? "y" : "ies"} that may provide context:\n\n"

        memories.each do |memory|
          match_pct = (memory[:similarity] * 100).round
          type = memory.dig(:metadata, "type")
          type_emoji = case type
          when "concept" then "💡"
          when "fact" then "📋"
          when "experience" then "🔍"
          else "📄"
          end

          reminder += "#{type_emoji} **#{memory[:title]}** (#{type}, #{match_pct}% match)\n"
          reminder += "Path: `#{memory[:path]}`\n"
          reminder += "Read with: `MemoryRead(file_path: \"#{memory[:path]}\")`\n\n"
        end

        reminder += "**These entries may contain relevant knowledge for your task.**\n"
        reminder += "Read them to inform your approach, or ignore if not helpful.\n"
        reminder += "</system-reminder>"

        reminder
      end

      # Extract threshold configuration from memory config
      #
      # Supports both MemoryConfig objects (from DSL) and Hash configs (from YAML).
      # Extracts semantic search thresholds and hybrid search weights.
      #
      # @param memory_config [MemoryConfig, Hash, nil] Memory configuration
      # @return [Hash] Threshold config with symbol keys
      def extract_threshold_config(memory_config)
        return {} unless memory_config

        threshold_keys = [
          :discovery_threshold,
          :discovery_threshold_short,
          :adaptive_word_cutoff,
          :semantic_weight,
          :keyword_weight,
        ]

        if memory_config.respond_to?(:adapter_options)
          # MemoryConfig object (from DSL)
          memory_config.adapter_options.slice(*threshold_keys)
        elsif memory_config.is_a?(Hash)
          # Hash (from YAML) - handle both symbol and string keys
          result = {}
          threshold_keys.each do |key|
            value = memory_config[key] || memory_config[key.to_s]
            result[key] = value if value
          end
          result
        else
          {}
        end
      end
    end
  end
end
