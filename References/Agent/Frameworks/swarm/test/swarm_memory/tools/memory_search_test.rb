# frozen_string_literal: true

require "test_helper"

module SwarmMemory
  module Tools
    class MemorySearchTest < Minitest::Test
      def setup
        @storage = create_temp_storage_with_embedder
        @tool = SwarmMemory::Tools::MemorySearch.new(storage: @storage, agent_name: :test_agent)
      end

      def teardown
        cleanup_storage(@storage)
      end

      # Basic Functionality Tests

      def test_semantic_search_returns_results
        # Create sample memories
        @storage.write(
          file_path: "concept/auth.md",
          content: "# Authentication\n\nJWT and OAuth patterns for secure authentication.",
          title: "Authentication Patterns",
          metadata: { "type" => "concept", "tags" => ["auth", "security"], "domain" => "programming" },
        )

        @storage.write(
          file_path: "concept/api.md",
          content: "# API Design\n\nRESTful API design principles.",
          title: "API Design",
          metadata: { "type" => "concept", "tags" => ["api", "design"], "domain" => "programming" },
        )

        result = @tool.execute(query: "authentication security")

        assert_match(/Found \d+ memor/, result)
        assert_match(/Authentication Patterns/, result)
        assert_match(/score:/, result)
      end

      def test_results_include_metadata
        @storage.write(
          file_path: "concept/ruby.md",
          content: "# Ruby Language\n\nRuby is a dynamic programming language.",
          title: "Ruby Language",
          metadata: { "type" => "concept", "tags" => ["ruby", "language"], "domain" => "programming/ruby" },
        )

        result = @tool.execute(query: "ruby programming")

        assert_match(/Tags: ruby, language/, result)
        assert_match(%r{Domain: programming/ruby}, result)
        assert_match(/Type: concept/, result)
      end

      def test_results_ranked_by_similarity
        @storage.write(
          file_path: "concept/a.md",
          content: "# Ruby Language\n\nRuby programming details.",
          title: "Ruby Language",
          metadata: { "type" => "concept", "tags" => ["ruby"], "domain" => "programming" },
        )

        @storage.write(
          file_path: "concept/b.md",
          content: "# Python Language\n\nPython programming details.",
          title: "Python Language",
          metadata: { "type" => "concept", "tags" => ["python"], "domain" => "programming" },
        )

        result = @tool.execute(query: "ruby programming language")

        # Both results should be present (ranking depends on embeddings which are random in tests)
        assert_match(/Ruby Language/, result)
        assert_match(/Python Language/, result)
        assert_match(/score:/, result)
      end

      # Parameter Validation Tests

      def test_default_parameters
        @storage.write(
          file_path: "concept/test.md",
          content: "# Test\n\nTest content.",
          title: "Test",
          metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
        )

        result = @tool.execute(query: "test")

        assert_match(/Found \d+ memor/, result)
      end

      def test_custom_top_k
        # Create 5 memories
        5.times do |i|
          @storage.write(
            file_path: "concept/test#{i}.md",
            content: "# Test #{i}\n\nTest content #{i}.",
            title: "Test #{i}",
            metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
          )
        end

        result = @tool.execute(query: "test", top_k: 3)

        assert_match(/Found 3 memor/, result)
      end

      def test_custom_threshold
        @storage.write(
          file_path: "concept/test.md",
          content: "# Test\n\nTest content.",
          title: "Test",
          metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
        )

        result = @tool.execute(query: "completely different query", threshold: 0.99)

        assert_match(/No memories found/, result)
      end

      def test_invalid_top_k_negative
        result = @tool.execute(query: "test", top_k: -5)

        assert_match(/InputValidationError.*top_k must be positive/, result)
      end

      def test_invalid_top_k_zero
        result = @tool.execute(query: "test", top_k: 0)

        assert_match(/InputValidationError.*top_k must be positive/, result)
      end

      def test_invalid_threshold_too_low
        result = @tool.execute(query: "test", threshold: -0.5)

        assert_match(/InputValidationError.*threshold must be between 0.0 and 1.0/, result)
      end

      def test_invalid_threshold_too_high
        result = @tool.execute(query: "test", threshold: 1.5)

        assert_match(/InputValidationError.*threshold must be between 0.0 and 1.0/, result)
      end

      def test_top_k_capped_at_max_results
        # Create 150 memories (more than MAX_RESULTS)
        150.times do |i|
          @storage.write(
            file_path: "concept/test#{i}.md",
            content: "# Test #{i}\n\nTest content #{i}.",
            title: "Test #{i}",
            metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
          )
        end

        result = @tool.execute(query: "test", top_k: 150)

        # Should be capped at 100
        assert_match(/Found 50 memor/, result)
      end

      # Filtering Tests

      def test_filter_by_single_type
        @storage.write(
          file_path: "concept/test1.md",
          content: "# Concept Test\n\nConcept content.",
          title: "Concept Test",
          metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
        )

        @storage.write(
          file_path: "fact/test2.md",
          content: "# Fact Test\n\nFact content.",
          title: "Fact Test",
          metadata: { "type" => "fact", "tags" => ["test"], "domain" => "test" },
        )

        result = @tool.execute(query: "test", filter_type: "concept")

        assert_match(/Concept Test/, result)
        refute_match(/Fact Test/, result)
      end

      def test_filter_by_multiple_types
        @storage.write(
          file_path: "concept/test1.md",
          content: "# Concept Test\n\nConcept content.",
          title: "Concept Test",
          metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
        )

        @storage.write(
          file_path: "fact/test2.md",
          content: "# Fact Test\n\nFact content.",
          title: "Fact Test",
          metadata: { "type" => "fact", "tags" => ["test"], "domain" => "test" },
        )

        @storage.write(
          file_path: "skill/test3.md",
          content: "# Skill Test\n\nSkill content.",
          title: "Skill Test",
          metadata: { "type" => "skill", "tags" => ["test"], "domain" => "test" },
        )

        result = @tool.execute(query: "test", filter_type: "concept,fact")

        assert_match(/Concept Test/, result)
        assert_match(/Fact Test/, result)
        refute_match(/Skill Test/, result)
      end

      def test_filter_by_domain
        @storage.write(
          file_path: "concept/ruby.md",
          content: "# Ruby\n\nRuby programming.",
          title: "Ruby",
          metadata: { "type" => "concept", "tags" => ["ruby"], "domain" => "programming/ruby" },
        )

        @storage.write(
          file_path: "concept/python.md",
          content: "# Python\n\nPython programming.",
          title: "Python",
          metadata: { "type" => "concept", "tags" => ["python"], "domain" => "programming/python" },
        )

        result = @tool.execute(query: "programming", filter_domain: "programming/ruby")

        assert_match(/Ruby/, result)
        refute_match(/Python/, result)
      end

      def test_combined_filters_type_and_domain
        @storage.write(
          file_path: "concept/ruby.md",
          content: "# Ruby Concept\n\nRuby programming concepts.",
          title: "Ruby Concept",
          metadata: { "type" => "concept", "tags" => ["ruby"], "domain" => "programming/ruby" },
        )

        @storage.write(
          file_path: "fact/ruby.md",
          content: "# Ruby Fact\n\nRuby programming facts.",
          title: "Ruby Fact",
          metadata: { "type" => "fact", "tags" => ["ruby"], "domain" => "programming/ruby" },
        )

        @storage.write(
          file_path: "concept/python.md",
          content: "# Python Concept\n\nPython programming concepts.",
          title: "Python Concept",
          metadata: { "type" => "concept", "tags" => ["python"], "domain" => "programming/python" },
        )

        result = @tool.execute(query: "programming", filter_type: "concept", filter_domain: "programming/ruby")

        assert_match(/Ruby Concept/, result)
        refute_match(/Ruby Fact/, result)
        refute_match(/Python Concept/, result)
      end

      # Edge Case Tests

      def test_no_results_found
        result = @tool.execute(query: "nonexistent query that will never match anything")

        assert_match(/No memories found/, result)
        assert_match(/Try:/, result)
        assert_match(/Using a more general query/, result)
      end

      def test_no_semantic_index_error
        # Create storage without embedder
        storage_without_embedder = create_temp_storage
        tool = SwarmMemory::Tools::MemorySearch.new(storage: storage_without_embedder, agent_name: :test_agent)

        result = tool.execute(query: "test")

        assert_match(/InputValidationError.*Semantic search not available/, result)

        cleanup_storage(storage_without_embedder)
      end

      def test_empty_query_string
        @storage.write(
          file_path: "concept/test.md",
          content: "# Test\n\nTest content.",
          title: "Test",
          metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
        )

        # Empty query should still work (returns all results)
        result = @tool.execute(query: "")

        assert_match(/Found \d+ memor/, result)
      end

      def test_no_results_with_high_threshold
        @storage.write(
          file_path: "concept/test.md",
          content: "# Test\n\nTest content.",
          title: "Test",
          metadata: { "type" => "concept", "tags" => ["test"], "domain" => "test" },
        )

        result = @tool.execute(query: "test", threshold: 0.99)

        assert_match(/No memories found.*with similarity >= 0.99/, result)
      end

      # Tool Metadata Tests

      def test_tool_name
        assert_equal("MemorySearch", @tool.name)
      end

      def test_tool_has_description
        description = @tool.class.description

        assert(description)
        assert_match(/semantic search/i, description)
      end
    end
  end
end
