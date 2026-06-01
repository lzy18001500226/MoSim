# frozen_string_literal: true

require "test_helper"

module SwarmMemory
  module Core
    class SemanticIndexTest < Minitest::Test
      def setup
        @temp_dir = Dir.mktmpdir
        @adapter = Adapters::FilesystemAdapter.new(directory: @temp_dir)
        @embedder = Embeddings::InformersEmbedder.new
      end

      def teardown
        FileUtils.rm_rf(@temp_dir) if @temp_dir && File.exist?(@temp_dir)
      end

      # Test: Pure semantic search (weight 1.0/0.0) returns full semantic score
      def test_pure_semantic_search_no_keyword_penalty
        # Configure for pure semantic search
        index = SemanticIndex.new(
          adapter: @adapter,
          embedder: @embedder,
          semantic_weight: 1.0,
          keyword_weight: 0.0,
        )

        # Write an entry WITHOUT tags
        storage = Storage.new(adapter: @adapter, embedder: @embedder)
        storage.write(
          file_path: "concept/ruby/blocks.md",
          content: "Ruby blocks are closures that can be passed to methods.",
          title: "Ruby Blocks",
          metadata: {}, # No tags - would normally cause keyword penalty
        )

        results = index.search(query: "closures in ruby", top_k: 1, threshold: 0.0)

        assert_equal(1, results.size)
        # With pure semantic search (1.0/0.0), hybrid score equals semantic score
        assert_in_delta(results.first[:semantic_score], results.first[:similarity], 0.001)
        # Keyword score should be 0 (no tags)
        assert_in_delta(0.0, results.first[:keyword_score])
      end

      # Test: No penalty when keyword_score is zero (fallback to semantic)
      def test_fallback_to_semantic_when_no_keyword_matches
        # Default 50/50 weights
        index = SemanticIndex.new(adapter: @adapter, embedder: @embedder)

        # Write an entry WITHOUT tags
        storage = Storage.new(adapter: @adapter, embedder: @embedder)
        storage.write(
          file_path: "concept/ruby/blocks.md",
          content: "Ruby blocks are closures that can be passed to methods.",
          title: "Ruby Blocks",
          metadata: {}, # No tags
        )

        results = index.search(query: "ruby blocks", top_k: 1, threshold: 0.0)

        assert_equal(1, results.size)
        # Keyword score is 0 because no tags
        assert_in_delta(0.0, results.first[:keyword_score])
        # With fallback behavior, hybrid score equals semantic score (no penalty)
        assert_in_delta(results.first[:semantic_score], results.first[:similarity], 0.001)
      end

      # Test: Custom weights affect hybrid score calculation
      def test_custom_weights_affect_hybrid_score
        # 80% semantic, 20% keyword
        index = SemanticIndex.new(
          adapter: @adapter,
          embedder: @embedder,
          semantic_weight: 0.8,
          keyword_weight: 0.2,
        )

        # Write an entry with tags
        storage = Storage.new(adapter: @adapter, embedder: @embedder)
        storage.write(
          file_path: "concept/ruby/blocks.md",
          content: "Ruby blocks are closures that can be passed to methods.",
          title: "Ruby Blocks",
          metadata: { "tags" => ["ruby", "blocks", "closures"] },
        )

        results = index.search(query: "ruby closures", top_k: 1, threshold: 0.0)

        assert_equal(1, results.size)
        # Verify hybrid score matches expected calculation
        semantic = results.first[:semantic_score]
        keyword = results.first[:keyword_score]
        expected_hybrid = (0.8 * semantic) + (0.2 * keyword)

        assert_in_delta(expected_hybrid, results.first[:similarity], 0.001)
      end

      # Test: Entries with matching tags get keyword boost
      def test_entries_with_tags_get_keyword_boost
        index = SemanticIndex.new(
          adapter: @adapter,
          embedder: @embedder,
          semantic_weight: 0.5,
          keyword_weight: 0.5,
        )

        storage = Storage.new(adapter: @adapter, embedder: @embedder)
        storage.write(
          file_path: "concept/ruby/blocks.md",
          content: "Ruby blocks are closures that can be passed to methods.",
          title: "Ruby Blocks",
          metadata: { "tags" => ["ruby", "blocks", "closures"] },
        )

        # Search with keywords that match tags
        results = index.search(query: "ruby closures", top_k: 1, threshold: 0.0)

        assert_equal(1, results.size)
        # Keyword score should be > 0 because "ruby" and "closures" match tags
        assert_operator(results.first[:keyword_score], :>, 0)
      end

      # Test: Zero keyword weight eliminates tag matching entirely
      def test_zero_keyword_weight_ignores_tags
        index = SemanticIndex.new(
          adapter: @adapter,
          embedder: @embedder,
          semantic_weight: 1.0,
          keyword_weight: 0.0,
        )

        storage = Storage.new(adapter: @adapter, embedder: @embedder)
        storage.write(
          file_path: "concept/ruby/blocks.md",
          content: "Ruby blocks are closures.",
          title: "Ruby Blocks",
          metadata: { "tags" => ["ruby", "blocks"] },
        )

        results = index.search(query: "ruby blocks", top_k: 1, threshold: 0.0)

        assert_equal(1, results.size)
        # Even with matching tags, keyword weight is 0 so hybrid = semantic
        assert_in_delta(results.first[:semantic_score], results.first[:similarity], 0.001)
      end
    end

    # Tests for Storage weight passthrough
    class StorageWeightPassthroughTest < Minitest::Test
      def setup
        @temp_dir = Dir.mktmpdir
        @adapter = Adapters::FilesystemAdapter.new(directory: @temp_dir)
        @embedder = Embeddings::InformersEmbedder.new
      end

      def teardown
        FileUtils.rm_rf(@temp_dir) if @temp_dir && File.exist?(@temp_dir)
      end

      # Test: Storage creates semantic index when embedder provided
      def test_storage_creates_semantic_index_with_embedder
        storage = Storage.new(adapter: @adapter, embedder: @embedder)

        refute_nil(storage.semantic_index)
      end

      # Test: Storage without embedder has no semantic index
      def test_storage_without_embedder_has_no_semantic_index
        storage = Storage.new(adapter: @adapter, embedder: nil)

        assert_nil(storage.semantic_index)
      end

      # Test: Storage passes weights through - verified via search behavior
      def test_storage_passes_pure_semantic_weights
        # Create storage with pure semantic weights
        storage = Storage.new(
          adapter: @adapter,
          embedder: @embedder,
          semantic_weight: 1.0,
          keyword_weight: 0.0,
        )

        # Write entry without tags
        storage.write(
          file_path: "concept/ruby/blocks.md",
          content: "Ruby blocks are closures.",
          title: "Ruby Blocks",
          metadata: {},
        )

        # Search via the storage's semantic index
        results = storage.semantic_index.search(query: "ruby blocks", top_k: 1, threshold: 0.0)

        assert_equal(1, results.size)
        # With pure semantic weights, hybrid score should equal semantic score
        assert_in_delta(results.first[:semantic_score], results.first[:similarity], 0.001)
      end

      # Test: Storage passes custom weights - verified via search behavior
      def test_storage_passes_custom_weights
        storage = Storage.new(
          adapter: @adapter,
          embedder: @embedder,
          semantic_weight: 0.7,
          keyword_weight: 0.3,
        )

        storage.write(
          file_path: "concept/ruby/blocks.md",
          content: "Ruby blocks are closures.",
          title: "Ruby Blocks",
          metadata: { "tags" => ["ruby", "blocks"] },
        )

        results = storage.semantic_index.search(query: "ruby blocks", top_k: 1, threshold: 0.0)

        assert_equal(1, results.size)
        # Verify weights were applied: hybrid = 0.7 * semantic + 0.3 * keyword
        semantic = results.first[:semantic_score]
        keyword = results.first[:keyword_score]
        expected = (0.7 * semantic) + (0.3 * keyword)

        assert_in_delta(expected, results.first[:similarity], 0.001)
      end
    end
  end
end
