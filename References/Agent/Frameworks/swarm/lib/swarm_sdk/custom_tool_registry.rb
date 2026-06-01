# frozen_string_literal: true

require "delegate"

module SwarmSDK
  # Registry for user-defined custom tools
  #
  # Provides a simple way to register custom tools without creating a full plugin.
  # Custom tools are registered globally and available to all agents that request them.
  #
  # ## When to Use Custom Tools vs Plugins
  #
  # **Use Custom Tools when:**
  # - You have simple, stateless tools
  # - Tools don't need persistent storage
  # - Tools don't need lifecycle hooks
  # - Tools don't need system prompt contributions
  #
  # **Use Plugins when:**
  # - Tools need persistent storage per agent
  # - Tools need lifecycle hooks (on_agent_initialized, on_user_message, etc.)
  # - Tools need to contribute to system prompts
  # - You have a suite of related tools that share configuration
  #
  # @example Register a simple tool
  #   class WeatherTool < RubyLLM::Tool
  #     description "Get weather for a city"
  #     param :city, type: "string", required: true
  #
  #     def execute(city:)
  #       "Weather in #{city}: Sunny"
  #     end
  #   end
  #
  #   SwarmSDK.register_tool(WeatherTool)
  #
  # @example Register with explicit name
  #   SwarmSDK.register_tool(:Weather, WeatherTool)
  #
  # @example Tool with creation requirements
  #   class AgentAwareTool < RubyLLM::Tool
  #     def self.creation_requirements
  #       [:agent_name, :directory]
  #     end
  #
  #     def initialize(agent_name:, directory:)
  #       super()
  #       @agent_name = agent_name
  #       @directory = directory
  #     end
  #
  #     def execute
  #       "Agent: #{@agent_name}, Dir: #{@directory}"
  #     end
  #   end
  #
  #   SwarmSDK.register_tool(AgentAwareTool)
  #
  module CustomToolRegistry
    # Wrapper that overrides the tool's name to match the registered name
    #
    # This ensures that when a user registers a tool with a specific name,
    # that name is what gets used for tool lookup (has_tool?) and LLM tool calls.
    class NamedToolWrapper < SimpleDelegator
      def initialize(tool, registered_name)
        super(tool)
        @registered_name = registered_name.to_s
      end

      # Override name to return the registered name
      def name
        @registered_name
      end
    end

    @tools = {}

    class << self
      # Register a custom tool
      #
      # @param name [Symbol] Tool name
      # @param tool_class [Class] Tool class (must be a RubyLLM::Tool subclass)
      # @raise [ArgumentError] If tool_class is not a RubyLLM::Tool subclass
      # @raise [ArgumentError] If a tool with the same name is already registered
      # @return [void]
      def register(name, tool_class)
        name = name.to_sym

        unless tool_class.is_a?(Class) && tool_class < RubyLLM::Tool
          raise ArgumentError, "Tool class must inherit from RubyLLM::Tool"
        end

        if @tools.key?(name)
          raise ArgumentError, "Custom tool '#{name}' is already registered"
        end

        if PluginRegistry.plugin_tool?(name)
          raise ArgumentError, "Tool '#{name}' is already provided by a plugin"
        end

        if Tools::Registry.exists?(name)
          raise ArgumentError, "Tool '#{name}' is a built-in tool and cannot be overridden"
        end

        @tools[name] = tool_class
      end

      # Check if a custom tool is registered
      #
      # @param name [Symbol, String] Tool name
      # @return [Boolean]
      def registered?(name)
        @tools.key?(name.to_sym)
      end

      # Get a registered tool class
      #
      # @param name [Symbol, String] Tool name
      # @return [Class, nil] Tool class or nil if not found
      def get(name)
        @tools[name.to_sym]
      end

      # Get all registered custom tool names
      #
      # @return [Array<Symbol>]
      def tool_names
        @tools.keys
      end

      # Create a tool instance
      #
      # Uses the tool's `creation_requirements` class method (if defined) to determine
      # what parameters to pass to the constructor. The created tool is wrapped with
      # NamedToolWrapper to ensure the registered name is used for tool lookup.
      #
      # @param name [Symbol, String] Tool name
      # @param context [Hash] Available context for tool creation
      # @option context [Symbol] :agent_name Agent identifier
      # @option context [String] :directory Agent's working directory
      # @return [RubyLLM::Tool] Instantiated tool (wrapped with registered name)
      # @raise [ConfigurationError] If tool is unknown or has unmet requirements
      def create(name, context = {})
        name_sym = name.to_sym
        tool_class = @tools[name_sym]

        raise ConfigurationError, "Unknown custom tool: #{name}" unless tool_class

        # Create the tool instance
        tool = if tool_class.respond_to?(:creation_requirements)
          requirements = tool_class.creation_requirements
          params = extract_params(requirements, context, name)
          tool_class.new(**params)
        else
          # No requirements - simple instantiation
          tool_class.new
        end

        # Wrap with NamedToolWrapper to ensure registered name is used
        NamedToolWrapper.new(tool, name_sym)
      end

      # Unregister a custom tool
      #
      # @param name [Symbol, String] Tool name
      # @return [Class, nil] The unregistered tool class, or nil if not found
      def unregister(name)
        @tools.delete(name.to_sym)
      end

      # Clear all registered custom tools
      #
      # Primarily useful for testing.
      #
      # @return [void]
      def clear
        @tools.clear
      end

      # Infer tool name from class name
      #
      # @param tool_class [Class] Tool class
      # @return [Symbol] Inferred tool name
      #
      # @example
      #   infer_name(WeatherTool) #=> :Weather
      #   infer_name(MyApp::Tools::StockPrice) #=> :StockPrice
      #   infer_name(MyApp::Tools::StockPriceTool) #=> :StockPrice
      def infer_name(tool_class)
        # Get the class name without module prefix
        class_name = tool_class.name.split("::").last

        # Remove "Tool" suffix if present
        name = class_name.sub(/Tool\z/, "")

        name.to_sym
      end

      private

      # Extract required parameters from context
      #
      # @param requirements [Array<Symbol>] Required parameter names
      # @param context [Hash] Available context
      # @param tool_name [Symbol] Tool name for error messages
      # @return [Hash] Parameters to pass to tool constructor
      # @raise [ConfigurationError] If required parameter is missing
      def extract_params(requirements, context, tool_name)
        params = {}

        requirements.each do |req|
          unless context.key?(req)
            raise ConfigurationError,
              "Custom tool '#{tool_name}' requires '#{req}' but it was not provided. " \
                "Ensure the tool's `creation_requirements` only includes supported keys: " \
                ":agent_name, :directory"
          end

          params[req] = context[req]
        end

        params
      end
    end
  end
end
