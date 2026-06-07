# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  # Pre-defined tool classes for testing (avoids reflection)
  module TestTools
    class WeatherTool < RubyLLM::Tool
      description "Get weather for a city"
      param :city, type: "string", required: true

      def execute(city:)
        "Weather in #{city}: Sunny"
      end
    end

    class StockPrice < RubyLLM::Tool
      description "Get stock price"
      param :ticker, type: "string", required: true

      def execute(ticker:)
        "#{ticker}: $150.00"
      end
    end

    class SimpleTool < RubyLLM::Tool
      description "A simple test tool"
      param :message, type: "string", required: true

      def execute(message:)
        "Echo: #{message}"
      end
    end

    class ContextAwareTool < RubyLLM::Tool
      class << self
        def creation_requirements
          [:agent_name, :directory]
        end
      end

      attr_reader :agent_name, :directory

      description "A tool that uses agent context"

      def initialize(agent_name:, directory:)
        super()
        @agent_name = agent_name
        @directory = directory
      end

      def execute
        "Agent: #{@agent_name}, Dir: #{@directory}"
      end
    end

    class AgentOnlyTool < RubyLLM::Tool
      class << self
        def creation_requirements
          [:agent_name]
        end
      end

      attr_reader :agent_name

      description "A tool that needs only agent name"

      def initialize(agent_name:)
        super()
        @agent_name = agent_name
      end

      def execute
        "Agent: #{@agent_name}"
      end
    end

    # Nested module for testing namespaced class name inference
    module Nested
      class DeepTool < RubyLLM::Tool
        description "A deeply nested tool"

        def execute
          "Deep!"
        end
      end
    end
  end

  class CustomToolRegistryTest < Minitest::Test
    def setup
      @temp_dir = Dir.mktmpdir
      # Clear any previously registered custom tools
      CustomToolRegistry.clear
    end

    def teardown
      CustomToolRegistry.clear
      FileUtils.rm_rf(@temp_dir) if @temp_dir && File.exist?(@temp_dir)
    end

    # --- Registration Tests ---

    def test_register_with_explicit_name
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      assert(CustomToolRegistry.registered?(:MyTool))
      assert_equal(TestTools::SimpleTool, CustomToolRegistry.get(:MyTool))
    end

    def test_register_with_symbol_and_string_name
      CustomToolRegistry.register("StringName", TestTools::SimpleTool)

      assert(CustomToolRegistry.registered?(:StringName))
      assert(CustomToolRegistry.registered?("StringName"))
    end

    def test_register_requires_rubyllm_tool_subclass
      not_a_tool = Class.new

      error = assert_raises(ArgumentError) do
        CustomToolRegistry.register(:NotATool, not_a_tool)
      end

      assert_includes(error.message, "must inherit from RubyLLM::Tool")
    end

    def test_register_prevents_duplicate_registration
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      error = assert_raises(ArgumentError) do
        CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)
      end

      assert_includes(error.message, "already registered")
    end

    def test_register_prevents_override_of_builtin_tools
      error = assert_raises(ArgumentError) do
        CustomToolRegistry.register(:Read, TestTools::SimpleTool)
      end

      assert_includes(error.message, "built-in tool")
    end

    def test_register_prevents_override_of_plugin_tools
      # Skip if SwarmMemory plugin isn't registered (it provides :MemoryRead)
      skip unless PluginRegistry.plugin_tool?(:MemoryRead)

      error = assert_raises(ArgumentError) do
        CustomToolRegistry.register(:MemoryRead, TestTools::SimpleTool)
      end

      assert_includes(error.message, "already provided by a plugin")
    end

    # --- Lookup Tests ---

    def test_registered_returns_true_for_registered_tool
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      assert(CustomToolRegistry.registered?(:MyTool))
    end

    def test_registered_returns_false_for_unknown_tool
      refute(CustomToolRegistry.registered?(:UnknownTool))
    end

    def test_registered_works_with_string_and_symbol
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      assert(CustomToolRegistry.registered?(:MyTool))
      assert(CustomToolRegistry.registered?("MyTool"))
    end

    def test_get_returns_tool_class
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      assert_equal(TestTools::SimpleTool, CustomToolRegistry.get(:MyTool))
    end

    def test_get_returns_nil_for_unknown_tool
      assert_nil(CustomToolRegistry.get(:UnknownTool))
    end

    def test_tool_names_returns_registered_names
      CustomToolRegistry.register(:ToolA, TestTools::SimpleTool)
      CustomToolRegistry.register(:ToolB, TestTools::WeatherTool)

      names = CustomToolRegistry.tool_names

      assert_includes(names, :ToolA)
      assert_includes(names, :ToolB)
      assert_equal(2, names.size)
    end

    # --- Creation Tests ---

    def test_create_simple_tool
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      tool = CustomToolRegistry.create(:MyTool, {})

      # Tool is wrapped with NamedToolWrapper for name consistency
      assert_instance_of(CustomToolRegistry::NamedToolWrapper, tool)
      # But delegates to the actual tool
      assert_kind_of(TestTools::SimpleTool, tool.__getobj__)
      # And the registered name is used
      assert_equal("MyTool", tool.name)
      # Execute should work via delegation
      assert_equal("Echo: hello", tool.execute(message: "hello"))
    end

    def test_create_tool_with_context_requirements
      CustomToolRegistry.register(:ContextTool, TestTools::ContextAwareTool)

      context = { agent_name: :test_agent, directory: @temp_dir }
      tool = CustomToolRegistry.create(:ContextTool, context)

      # Tool is wrapped with NamedToolWrapper
      assert_instance_of(CustomToolRegistry::NamedToolWrapper, tool)
      # But delegates to the actual tool
      assert_kind_of(TestTools::ContextAwareTool, tool.__getobj__)
      # And preserves context via delegation
      assert_equal(:test_agent, tool.agent_name)
      assert_equal(@temp_dir, tool.directory)
      # Name returns the registered name
      assert_equal("ContextTool", tool.name)
    end

    def test_create_raises_for_unknown_tool
      error = assert_raises(ConfigurationError) do
        CustomToolRegistry.create(:UnknownTool, {})
      end

      assert_includes(error.message, "Unknown custom tool")
    end

    def test_create_raises_for_missing_context
      CustomToolRegistry.register(:ContextTool, TestTools::ContextAwareTool)

      error = assert_raises(ConfigurationError) do
        CustomToolRegistry.create(:ContextTool, { agent_name: :test }) # Missing directory
      end

      assert_includes(error.message, "requires 'directory'")
    end

    def test_create_with_string_name
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      tool = CustomToolRegistry.create("MyTool", {})

      assert_respond_to(tool, :execute)
    end

    def test_create_tool_with_agent_only_requirement
      CustomToolRegistry.register(:AgentTool, TestTools::AgentOnlyTool)

      context = { agent_name: :my_agent }
      tool = CustomToolRegistry.create(:AgentTool, context)

      # Tool is wrapped with NamedToolWrapper
      assert_instance_of(CustomToolRegistry::NamedToolWrapper, tool)
      assert_kind_of(TestTools::AgentOnlyTool, tool.__getobj__)
      # Context is preserved via delegation
      assert_equal(:my_agent, tool.agent_name)
      # Name returns the registered name
      assert_equal("AgentTool", tool.name)
    end

    # --- Name Inference Tests ---

    def test_infer_name_removes_tool_suffix
      inferred = CustomToolRegistry.infer_name(TestTools::WeatherTool)

      assert_equal(:Weather, inferred)
    end

    def test_infer_name_without_tool_suffix
      inferred = CustomToolRegistry.infer_name(TestTools::StockPrice)

      assert_equal(:StockPrice, inferred)
    end

    def test_infer_name_from_nested_class
      inferred = CustomToolRegistry.infer_name(TestTools::Nested::DeepTool)

      assert_equal(:Deep, inferred)
    end

    def test_infer_name_strips_only_trailing_tool
      # SimpleTool -> Simple
      inferred = CustomToolRegistry.infer_name(TestTools::SimpleTool)

      assert_equal(:Simple, inferred)
    end

    # --- Unregister Tests ---

    def test_unregister_removes_tool
      CustomToolRegistry.register(:MyTool, TestTools::SimpleTool)

      assert(CustomToolRegistry.registered?(:MyTool))

      removed = CustomToolRegistry.unregister(:MyTool)

      assert_equal(TestTools::SimpleTool, removed)
      refute(CustomToolRegistry.registered?(:MyTool))
    end

    def test_unregister_returns_nil_for_unknown_tool
      removed = CustomToolRegistry.unregister(:UnknownTool)

      assert_nil(removed)
    end

    # --- Clear Tests ---

    def test_clear_removes_all_tools
      CustomToolRegistry.register(:ToolA, TestTools::SimpleTool)
      CustomToolRegistry.register(:ToolB, TestTools::WeatherTool)

      CustomToolRegistry.clear

      refute(CustomToolRegistry.registered?(:ToolA))
      refute(CustomToolRegistry.registered?(:ToolB))
      assert_empty(CustomToolRegistry.tool_names)
    end
  end

  # Test the SwarmSDK convenience methods
  class SwarmSDKToolRegistrationTest < Minitest::Test
    def setup
      @temp_dir = Dir.mktmpdir
      SwarmSDK.clear_custom_tools!
    end

    def teardown
      SwarmSDK.clear_custom_tools!
      FileUtils.rm_rf(@temp_dir) if @temp_dir && File.exist?(@temp_dir)
    end

    def test_register_tool_with_inferred_name
      result = SwarmSDK.register_tool(TestTools::WeatherTool)

      assert_equal(:Weather, result)
      assert(SwarmSDK.custom_tool_registered?(:Weather))
    end

    def test_register_tool_with_explicit_name
      result = SwarmSDK.register_tool(:GetWeather, TestTools::WeatherTool)

      assert_equal(:GetWeather, result)
      assert(SwarmSDK.custom_tool_registered?(:GetWeather))
    end

    def test_custom_tool_registered_returns_false_for_unknown
      refute(SwarmSDK.custom_tool_registered?(:UnknownTool))
    end

    def test_custom_tools_returns_list_of_names
      SwarmSDK.register_tool(:ToolA, TestTools::SimpleTool)
      SwarmSDK.register_tool(:ToolB, TestTools::WeatherTool)

      names = SwarmSDK.custom_tools

      assert_includes(names, :ToolA)
      assert_includes(names, :ToolB)
    end

    def test_unregister_tool
      SwarmSDK.register_tool(:MyTool, TestTools::SimpleTool)

      removed = SwarmSDK.unregister_tool(:MyTool)

      assert_equal(TestTools::SimpleTool, removed)
      refute(SwarmSDK.custom_tool_registered?(:MyTool))
    end

    def test_clear_custom_tools
      SwarmSDK.register_tool(:ToolA, TestTools::SimpleTool)
      SwarmSDK.register_tool(:ToolB, TestTools::WeatherTool)

      SwarmSDK.clear_custom_tools!

      assert_empty(SwarmSDK.custom_tools)
    end

    def test_register_same_tool_with_different_names
      SwarmSDK.register_tool(:ToolA, TestTools::SimpleTool)
      SwarmSDK.register_tool(:ToolB, TestTools::SimpleTool)

      assert(SwarmSDK.custom_tool_registered?(:ToolA))
      assert(SwarmSDK.custom_tool_registered?(:ToolB))
    end
  end
end
