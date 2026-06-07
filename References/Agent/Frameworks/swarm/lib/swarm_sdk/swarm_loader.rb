# frozen_string_literal: true

module SwarmSDK
  # Loader for creating swarm instances from multiple sources
  #
  # SwarmLoader loads swarm configurations from:
  # - Files: .rb (DSL) or .yml (YAML)
  # - YAML strings: Direct YAML content
  # - DSL blocks: Inline Ruby blocks
  #
  # All loaded swarms get hierarchical swarm_id and parent_swarm_id.
  #
  # ## Features
  # - Supports Ruby DSL (.rb files or blocks)
  # - Supports YAML (.yml/.yaml files or strings)
  # - Sets hierarchical swarm_id based on parent + registration name
  # - Isolates loading in separate context
  # - Proper error handling for missing/invalid sources
  #
  # ## Examples
  #
  #   # From file
  #   swarm = SwarmLoader.load_from_file(
  #     "./swarms/code_review.rb",
  #     swarm_id: "main/code_review",
  #     parent_swarm_id: "main"
  #   )
  #
  #   # From YAML string
  #   swarm = SwarmLoader.load_from_yaml_string(
  #     "version: 2\nswarm:\n  name: Test\n...",
  #     swarm_id: "main/testing",
  #     parent_swarm_id: "main"
  #   )
  #
  #   # From block
  #   swarm = SwarmLoader.load_from_block(
  #     proc { id "team"; name "Team"; agent :dev { ... } },
  #     swarm_id: "main/team",
  #     parent_swarm_id: "main"
  #   )
  #
  class SwarmLoader
    class << self
      # Load a swarm from a file (.rb or .yml)
      #
      # @param file_path [String] Path to swarm file
      # @param swarm_id [String] Hierarchical swarm ID to assign
      # @param parent_swarm_id [String] Parent swarm ID
      # @return [Swarm] Loaded swarm instance with overridden IDs
      # @raise [ConfigurationError] If file not found or unsupported type
      def load_from_file(file_path, swarm_id:, parent_swarm_id:)
        path = Pathname.new(file_path).expand_path

        raise ConfigurationError, "Swarm file not found: #{path}" unless path.exist?

        # Determine file type and load
        case path.extname
        when ".rb"
          load_from_ruby_file(path, swarm_id, parent_swarm_id)
        when ".yml", ".yaml"
          load_from_yaml_file(path, swarm_id, parent_swarm_id)
        else
          raise ConfigurationError, "Unsupported swarm file type: #{path.extname}. Use .rb, .yml, or .yaml"
        end
      end

      # Load a swarm from YAML string
      #
      # @param yaml_content [String] YAML configuration content
      # @param swarm_id [String] Hierarchical swarm ID to assign
      # @param parent_swarm_id [String] Parent swarm ID
      # @return [Swarm] Loaded swarm instance with overridden IDs
      # @raise [ConfigurationError] If YAML is invalid
      def load_from_yaml_string(yaml_content, swarm_id:, parent_swarm_id:)
        # Use Configuration to parse YAML string
        config = Configuration.new(yaml_content, base_dir: Dir.pwd)
        config.load_and_validate
        swarm = config.to_swarm

        # Override swarm_id and parent_swarm_id
        swarm.override_swarm_ids(swarm_id: swarm_id, parent_swarm_id: parent_swarm_id)

        swarm
      end

      # Load a swarm from DSL block
      #
      # @param block [Proc] Block containing SwarmSDK DSL
      # @param swarm_id [String] Hierarchical swarm ID to assign
      # @param parent_swarm_id [String] Parent swarm ID
      # @return [Swarm] Loaded swarm instance with overridden IDs
      def load_from_block(block, swarm_id:, parent_swarm_id:)
        # Execute block in Builder context
        builder = Swarm::Builder.new
        builder.instance_eval(&block)
        swarm = builder.build_swarm

        # Override swarm_id and parent_swarm_id
        swarm.override_swarm_ids(swarm_id: swarm_id, parent_swarm_id: parent_swarm_id)

        swarm
      end

      private

      # Load swarm from Ruby DSL file
      #
      # @param path [Pathname] Path to .rb file
      # @param swarm_id [String] Swarm ID to assign
      # @param parent_swarm_id [String] Parent swarm ID
      # @return [Swarm] Loaded swarm with overridden IDs
      def load_from_ruby_file(path, swarm_id, parent_swarm_id)
        content = File.read(path)

        # Execute DSL in isolated context
        # The DSL should return a swarm via SwarmSDK.build { ... }
        swarm = eval(content, binding, path.to_s) # rubocop:disable Security/Eval

        # Override swarm_id and parent_swarm_id
        # These must be set after build to ensure hierarchical structure
        swarm.override_swarm_ids(swarm_id: swarm_id, parent_swarm_id: parent_swarm_id)

        swarm
      end

      # Load swarm from YAML file
      #
      # @param path [Pathname] Path to .yml file
      # @param swarm_id [String] Swarm ID to assign
      # @param parent_swarm_id [String] Parent swarm ID
      # @return [Swarm] Loaded swarm with overridden IDs
      def load_from_yaml_file(path, swarm_id, parent_swarm_id)
        # Use Configuration to load and convert YAML to swarm
        config = Configuration.load_file(path.to_s)
        swarm = config.to_swarm

        # Override swarm_id and parent_swarm_id
        swarm.override_swarm_ids(swarm_id: swarm_id, parent_swarm_id: parent_swarm_id)

        swarm
      end
    end
  end
end
