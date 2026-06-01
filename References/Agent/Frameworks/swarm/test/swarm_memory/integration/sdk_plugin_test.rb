# frozen_string_literal: true

require "test_helper"

module SwarmMemory
  module Integration
    class SDKPluginTest < Minitest::Test
      def setup
        @plugin = SDKPlugin.new
      end

      # memory_configured? tests (moved from SwarmSDK::Agent::Definition)
      # These test the plugin's ability to determine if memory is configured

      def test_memory_configured_with_nil
        agent_def = create_agent_definition(memory: nil)

        refute(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_hash_and_directory
        agent_def = create_agent_definition(memory: { directory: "/tmp/memory" })

        assert(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_hash_and_string_key
        agent_def = create_agent_definition(memory: { "directory" => "/tmp/memory" })

        assert(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_empty_directory
        agent_def = create_agent_definition(memory: { directory: "" })

        refute(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_whitespace_directory
        agent_def = create_agent_definition(memory: { directory: "   " })

        refute(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_memory_config_object_enabled
        # Create a mock MemoryConfig object
        memory_config = Object.new
        def memory_config.enabled? = true

        agent_def = create_agent_definition(memory: memory_config)

        assert(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_memory_config_object_disabled
        # Create a mock MemoryConfig object that is disabled
        memory_config = Object.new
        def memory_config.enabled? = false

        agent_def = create_agent_definition(memory: memory_config)

        refute(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_no_memory_key
        agent_def = create_agent_definition

        refute(@plugin.memory_configured?(agent_def))
      end

      # translate_yaml_config tests

      def test_translate_yaml_config_with_full_config
        builder = MockBuilder.new
        agent_config = {
          memory: {
            directory: "/tmp/memory",
            adapter: :filesystem,
            mode: :full_access,
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal("/tmp/memory", builder.memory_config[:directory])
        assert_equal(:filesystem, builder.memory_config[:adapter])
        assert_equal(:full_access, builder.memory_config[:mode])
      end

      def test_translate_yaml_config_with_partial_config
        builder = MockBuilder.new
        agent_config = {
          memory: {
            directory: "/tmp/memory",
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal("/tmp/memory", builder.memory_config[:directory])
        assert_nil(builder.memory_config[:adapter])
        assert_nil(builder.memory_config[:mode])
      end

      def test_translate_yaml_config_without_memory
        builder = MockBuilder.new
        agent_config = { tools: [:Read] }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_nil(builder.memory_config)
      end

      def test_translate_yaml_config_with_custom_adapter_options
        builder = MockBuilder.new
        agent_config = {
          memory: {
            adapter: :multi_bank_postgres,
            agent_id: "business_consultant",
            default_bank: "working",
            banks: { working: { max_size: 10485760 } },
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal(:multi_bank_postgres, builder.memory_config[:adapter])
        assert_equal("business_consultant", builder.memory_config[:agent_id])
        assert_equal("working", builder.memory_config[:default_bank])
        assert_equal({ working: { max_size: 10485760 } }, builder.memory_config[:banks])
      end

      def test_translate_yaml_config_with_threshold_options
        builder = MockBuilder.new
        agent_config = {
          memory: {
            directory: "/tmp/memory",
            discovery_threshold: 0.5,
            discovery_threshold_short: 0.3,
            semantic_weight: 0.6,
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal("/tmp/memory", builder.memory_config[:directory])
        assert_in_delta(0.5, builder.memory_config[:discovery_threshold])
        assert_in_delta(0.3, builder.memory_config[:discovery_threshold_short])
        assert_in_delta(0.6, builder.memory_config[:semantic_weight])
      end

      # memory_configured? tests for custom adapters

      def test_memory_configured_with_custom_adapter
        agent_def = create_agent_definition(memory: {
          adapter: :multi_bank_postgres,
          agent_id: "test",
        })

        assert(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_custom_adapter_no_directory
        agent_def = create_agent_definition(memory: {
          adapter: :custom_adapter,
          connection_string: "postgres://localhost",
        })

        assert(@plugin.memory_configured?(agent_def))
      end

      def test_memory_configured_with_empty_hash
        agent_def = create_agent_definition(memory: {})

        refute(@plugin.memory_configured?(agent_def))
      end

      # Threshold configuration tests (testing private extract_threshold_config through public API)

      def test_on_agent_initialized_stores_threshold_config_from_hash
        agent_def = create_agent_definition(memory: {
          directory: "/tmp/memory",
          discovery_threshold: 0.6,
          semantic_weight: 0.7,
        })

        # Create minimal mocks
        storage = Object.new
        agent = MockAgent.new

        context = {
          storage: storage,
          agent_definition: agent_def,
          tool_configurator: nil,
        }

        # This should not raise and should store the threshold config internally
        assert_silent { @plugin.on_agent_initialized(agent_name: :test_agent, agent: agent, context: context) }
      end

      def test_on_agent_initialized_handles_nil_threshold_config
        agent_def = create_agent_definition(memory: { directory: "/tmp/memory" })

        storage = Object.new
        agent = MockAgent.new

        context = {
          storage: storage,
          agent_definition: agent_def,
          tool_configurator: nil,
        }

        # Should not raise even without threshold config
        assert_silent { @plugin.on_agent_initialized(agent_name: :test_agent, agent: agent, context: context) }
      end

      def test_on_user_message_uses_threshold_config_with_fallback
        # Setup: Create agent with threshold config
        agent_def = create_agent_definition(memory: {
          directory: "/tmp/memory",
          discovery_threshold: 0.6,
          adaptive_word_cutoff: 8,
        })

        # Mock storage with semantic_index that tracks what threshold was used
        semantic_index = MockSemanticIndex.new
        storage = MockStorage.new(semantic_index)

        agent = MockAgent.new

        context = {
          storage: storage,
          agent_definition: agent_def,
          tool_configurator: nil,
        }

        # Initialize agent (this stores threshold config)
        @plugin.on_agent_initialized(agent_name: :test_agent, agent: agent, context: context)

        # Now test on_user_message uses the stored config
        # Query with 10 words (>= adaptive_word_cutoff of 8) should use discovery_threshold
        @plugin.on_user_message(
          agent_name: :test_agent,
          prompt: "one two three four five six seven eight nine ten",
          is_first_message: true,
        )

        # Verify threshold from config was used (0.6, not default 0.35)
        skills_search = semantic_index.search_params.find { |p| p[:filter] == { "type" => "skill" } }

        assert_in_delta(0.6, skills_search[:threshold], 0.001)
      end

      def test_on_user_message_falls_back_to_defaults_without_config
        # Setup: Create agent WITHOUT threshold config
        agent_def = create_agent_definition(memory: { directory: "/tmp/memory" })

        # Mock storage
        semantic_index = MockSemanticIndex.new
        storage = MockStorage.new(semantic_index)

        agent = MockAgent.new

        context = {
          storage: storage,
          agent_definition: agent_def,
          tool_configurator: nil,
        }

        # Initialize agent
        @plugin.on_agent_initialized(agent_name: :test_agent, agent: agent, context: context)

        # Test on_user_message falls back to default (0.35 for normal queries)
        @plugin.on_user_message(
          agent_name: :test_agent,
          prompt: "one two three four five six seven eight nine ten",
          is_first_message: true,
        )

        # Verify default threshold was used
        skills_search = semantic_index.search_params.find { |p| p[:filter] == { "type" => "skill" } }

        assert_in_delta(0.35, skills_search[:threshold], 0.001)
      end

      # create_storage weight extraction tests

      def test_create_storage_extracts_semantic_weight_from_config
        temp_dir = Dir.mktmpdir
        begin
          config = SwarmMemory::DSL::MemoryConfig.new
          config.directory(temp_dir)
          config.semantic_weight(1.0)
          config.keyword_weight(0.0)

          storage = @plugin.create_storage(agent_name: :test, config: config)

          # Verify weights were passed through by testing search behavior
          storage.write(
            file_path: "concept/test/entry.md",
            content: "Test content for search",
            title: "Test Entry",
            metadata: {},
          )

          results = storage.semantic_index.search(query: "test content", top_k: 1, threshold: 0.0)
          # With pure semantic weights, hybrid score should equal semantic score
          assert_in_delta(results.first[:semantic_score], results.first[:similarity], 0.001)
        ensure
          FileUtils.rm_rf(temp_dir)
        end
      end

      def test_create_storage_extracts_weights_from_hash_config_symbol_keys
        temp_dir = Dir.mktmpdir
        begin
          config = {
            directory: temp_dir,
            semantic_weight: 0.8,
            keyword_weight: 0.2,
          }

          storage = @plugin.create_storage(agent_name: :test, config: config)

          storage.write(
            file_path: "concept/test/entry.md",
            content: "Test content",
            title: "Test Entry",
            metadata: { "tags" => ["test"] },
          )

          results = storage.semantic_index.search(query: "test", top_k: 1, threshold: 0.0)
          # Verify 0.8/0.2 weights were applied
          semantic = results.first[:semantic_score]
          keyword = results.first[:keyword_score]
          expected = (0.8 * semantic) + (0.2 * keyword)

          assert_in_delta(expected, results.first[:similarity], 0.001)
        ensure
          FileUtils.rm_rf(temp_dir)
        end
      end

      def test_create_storage_extracts_weights_from_hash_config_string_keys
        temp_dir = Dir.mktmpdir
        begin
          config = {
            "directory" => temp_dir,
            "semantic_weight" => 1.0,
            "keyword_weight" => 0.0,
          }

          storage = @plugin.create_storage(agent_name: :test, config: config)

          storage.write(
            file_path: "concept/test/entry.md",
            content: "Test content",
            title: "Test Entry",
            metadata: {},
          )

          results = storage.semantic_index.search(query: "test content", top_k: 1, threshold: 0.0)
          # With pure semantic weights, hybrid score should equal semantic score
          assert_in_delta(results.first[:semantic_score], results.first[:similarity], 0.001)
        ensure
          FileUtils.rm_rf(temp_dir)
        end
      end

      def test_create_storage_filters_sdk_level_options_from_adapter
        temp_dir = Dir.mktmpdir
        begin
          # Config with all SDK-level options that should NOT go to adapter
          config = {
            directory: temp_dir,
            semantic_weight: 0.9,
            keyword_weight: 0.1,
            discovery_threshold: 0.5,
            discovery_threshold_short: 0.3,
            adaptive_word_cutoff: 8,
          }

          # Should not raise (adapter would error on unknown kwargs)
          storage = @plugin.create_storage(agent_name: :test, config: config)

          refute_nil(storage)
        ensure
          FileUtils.rm_rf(temp_dir)
        end
      end

      def test_create_storage_uses_defaults_when_weights_not_specified
        temp_dir = Dir.mktmpdir
        begin
          # Config WITHOUT weights - should use SemanticIndex defaults (ENV or 0.5/0.5)
          config = { directory: temp_dir }

          storage = @plugin.create_storage(agent_name: :test, config: config)

          # Write entry without tags
          storage.write(
            file_path: "concept/test/entry.md",
            content: "Test content for default weights",
            title: "Test Entry",
            metadata: {},
          )

          results = storage.semantic_index.search(query: "test content", top_k: 1, threshold: 0.0)

          assert_equal(1, results.size)
          # With default weights and no tags (keyword_score=0),
          # fallback behavior: hybrid score equals semantic score (no penalty)
          assert_in_delta(results.first[:semantic_score], results.first[:similarity], 0.001)
        ensure
          FileUtils.rm_rf(temp_dir)
        end
      end

      # translate_yaml_config tests for loadskill_preserve_delegation

      def test_translate_yaml_config_with_loadskill_preserve_delegation_true
        builder = MockBuilder.new
        agent_config = {
          memory: {
            directory: "/tmp/memory",
            loadskill_preserve_delegation: true,
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal("/tmp/memory", builder.memory_config[:directory])
        assert(builder.memory_config[:loadskill_preserve_delegation])
      end

      def test_translate_yaml_config_with_loadskill_preserve_delegation_false
        builder = MockBuilder.new
        agent_config = {
          memory: {
            directory: "/tmp/memory",
            loadskill_preserve_delegation: false,
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal("/tmp/memory", builder.memory_config[:directory])
        refute(builder.memory_config[:loadskill_preserve_delegation])
      end

      def test_translate_yaml_config_with_string_key_loadskill_preserve_delegation
        builder = MockBuilder.new
        agent_config = {
          memory: {
            directory: "/tmp/memory",
            "loadskill_preserve_delegation" => false, # String key from YAML
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal("/tmp/memory", builder.memory_config[:directory])
        refute(builder.memory_config[:loadskill_preserve_delegation])
      end

      def test_translate_yaml_config_without_loadskill_preserve_delegation_omits_it
        builder = MockBuilder.new
        agent_config = {
          memory: {
            directory: "/tmp/memory",
            # No loadskill_preserve_delegation specified - should use DSL default
          },
        }

        @plugin.translate_yaml_config(builder, agent_config)

        assert_equal("/tmp/memory", builder.memory_config[:directory])
        # Key should NOT be present - will use MemoryConfig default
        refute(builder.memory_config.key?(:loadskill_preserve_delegation))
      end

      # serialize_config tests

      def test_serialize_config_with_memory
        memory_config = { directory: "/tmp/memory", mode: :full_access }
        agent_def = create_agent_definition(memory: memory_config)

        result = @plugin.serialize_config(agent_definition: agent_def)

        assert_equal({ memory: memory_config }, result)
      end

      def test_serialize_config_without_memory
        agent_def = create_agent_definition
        result = @plugin.serialize_config(agent_definition: agent_def)

        assert_empty(result)
      end

      private

      def create_agent_definition(memory: :not_set)
        config = {
          description: "Test agent",
          system_prompt: "Test prompt",
          directory: ".",
        }
        config[:memory] = memory unless memory == :not_set

        SwarmSDK::Agent::Definition.new(:test_agent, config)
      end

      # Mock builder for testing translate_yaml_config
      class MockBuilder
        attr_reader :memory_config

        def memory(&block)
          @memory_builder = MemoryBuilder.new
          @memory_builder.instance_eval(&block)
          @memory_config = @memory_builder.to_h
        end

        class MemoryBuilder
          def initialize
            @config = {}
          end

          def directory(value)
            @config[:directory] = value
          end

          def adapter(value)
            @config[:adapter] = value
          end

          def mode(value)
            @config[:mode] = value
          end

          def loadskill_preserve_delegation(value)
            @config[:loadskill_preserve_delegation] = value
          end

          def option(key, value)
            @config[key] = value
          end

          def to_h
            @config
          end
        end
      end

      # Mock classes for threshold testing
      class MockSemanticIndex
        attr_reader :search_params

        def initialize
          @search_params = []
        end

        def search(**params)
          @search_params << params
          []
        end
      end

      class MockStorage
        attr_reader :semantic_index

        def initialize(semantic_index)
          @semantic_index = semantic_index
        end
      end

      class MockAgent
        attr_reader :tool_registry

        def initialize
          @tool_registry = SwarmSDK::Agent::ToolRegistry.new
        end
      end
    end
  end
end
