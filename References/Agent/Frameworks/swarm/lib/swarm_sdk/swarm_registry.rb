# frozen_string_literal: true

module SwarmSDK
  # Registry for managing sub-swarms in composable swarms
  #
  # SwarmRegistry handles lazy loading, caching, and lifecycle management
  # of child swarms registered via the `swarms` DSL block.
  #
  # ## Features
  # - Lazy loading: Sub-swarms are only loaded when first accessed
  # - Caching: Loaded swarms are cached for reuse
  # - Hierarchical IDs: Sub-swarms get IDs based on parent + registration name
  # - Context control: keep_context determines if swarm state persists
  # - Lifecycle management: Cleanup cascades through all sub-swarms
  #
  # ## Example
  #
  #   registry = SwarmRegistry.new(parent_swarm_id: "main_app")
  #   registry.register("code_review", file: "./swarms/code_review.rb", keep_context: true)
  #
  #   # Lazy load on first access
  #   swarm = registry.load_swarm("code_review")
  #   # => Swarm with swarm_id = "main_app/code_review"
  #
  #   # Reset if keep_context: false
  #   registry.reset_if_needed("code_review")
  #
  class SwarmRegistry
    # Initialize a new swarm registry
    #
    # @param parent_swarm_id [String] ID of the parent swarm
    def initialize(parent_swarm_id:)
      @parent_swarm_id = parent_swarm_id
      @registered_swarms = {}
      # Format: { "code_review" => { file: "...", keep_context: true, instance: nil } }
    end

    # Register a sub-swarm for lazy loading
    #
    # @param name [String] Registration name for the swarm
    # @param source [Hash] Source specification with :type and :value
    #   - { type: :file, value: "./path/to/swarm.rb" }
    #   - { type: :yaml, value: "version: 2\n..." }
    #   - { type: :block, value: Proc }
    # @param keep_context [Boolean] Whether to preserve conversation state between calls (default: true)
    # @return [void]
    # @raise [ArgumentError] If swarm with same name already registered
    def register(name, source:, keep_context: true)
      raise ArgumentError, "Swarm '#{name}' already registered" if @registered_swarms.key?(name)

      @registered_swarms[name] = {
        source: source,
        keep_context: keep_context,
        instance: nil, # Lazy load
      }
    end

    # Check if a swarm is registered
    #
    # @param name [String] Swarm registration name
    # @return [Boolean] True if swarm is registered
    def registered?(name)
      @registered_swarms.key?(name)
    end

    # Load a registered swarm (lazy load + cache)
    #
    # Loads the swarm from its source (file, yaml, or block) on first access, then caches it.
    # Sets hierarchical swarm_id based on parent_swarm_id + registration name.
    #
    # @param name [String] Swarm registration name
    # @return [Swarm] Loaded swarm instance
    # @raise [ConfigurationError] If swarm not registered
    def load_swarm(name)
      entry = @registered_swarms[name]
      raise ConfigurationError, "Swarm '#{name}' not registered" unless entry

      # Return cached instance if exists
      return entry[:instance] if entry[:instance]

      # Load from appropriate source
      swarm_id = "#{@parent_swarm_id}/#{name}" # Hierarchical
      source = entry[:source]

      swarm = case source[:type]
      when :file
        SwarmLoader.load_from_file(
          source[:value],
          swarm_id: swarm_id,
          parent_swarm_id: @parent_swarm_id,
        )
      when :yaml
        SwarmLoader.load_from_yaml_string(
          source[:value],
          swarm_id: swarm_id,
          parent_swarm_id: @parent_swarm_id,
        )
      when :block
        SwarmLoader.load_from_block(
          source[:value],
          swarm_id: swarm_id,
          parent_swarm_id: @parent_swarm_id,
        )
      else
        raise ConfigurationError, "Unknown source type: #{source[:type]}"
      end

      entry[:instance] = swarm
      swarm
    end

    # Reset swarm context if keep_context: false
    #
    # @param name [String] Swarm registration name
    # @return [void]
    def reset_if_needed(name)
      entry = @registered_swarms[name]
      return if entry[:keep_context]

      entry[:instance]&.reset_context!
    end

    # Cleanup all registered swarms
    #
    # Stops all loaded swarm instances and clears the registry.
    # Should be called when parent swarm is done.
    #
    # @return [void]
    def shutdown_all
      @registered_swarms.each_value do |entry|
        entry[:instance]&.cleanup
      end
      @registered_swarms.clear
    end
  end
end
