# frozen_string_literal: true

module SwarmMemory
  module Tools
    # Tool for semantic search across memory entries
    #
    # Searches content stored in memory using AI embeddings to find
    # conceptually related entries even when exact keywords don't match.
    # Each agent has its own isolated memory storage.
    class MemorySearch < SwarmSDK::Tools::Base
      removable false # Memory tools are always available
      description <<~DESC
        Perform semantic search across memory entries using natural language queries.

        This tool uses AI embeddings to find conceptually related memories even when
        exact keywords don't match. Results are ranked by semantic similarity and
        filtered by specified criteria.

        Use this tool when:
        - Looking for concepts related to a topic (e.g., "authentication patterns")
        - Exploring connections between ideas
        - Finding memories when you don't know exact terminology
        - Researching a subject area

        Use MemoryGrep instead when:
        - Searching for exact text or regex patterns
        - Looking for specific code snippets or examples

        Use MemoryGlob instead when:
        - Browsing by path structure (e.g., "concept/ruby/*")
        - Listing all memories in a category

        Examples:
          MemorySearch(query: "authentication patterns", top_k: 5, threshold: 0.5)
          MemorySearch(query: "async programming", filter_type: "concept")
          MemorySearch(query: "API design", filter_domain: "programming")
      DESC

      param :query,
        type: "string",
        desc: "Natural language search query describing what you're looking for",
        required: true

      param :top_k,
        type: "integer",
        desc: "Maximum number of results to return (default: 10, max: 100)",
        required: false

      param :threshold,
        type: "number",
        desc: "Minimum similarity score 0.0-1.0 (default: 0.0, higher = stricter)",
        required: false

      param :filter_type,
        type: "string",
        desc: "Filter by type: 'concept', 'fact', 'skill', 'experience', or comma-separated list",
        required: false

      param :filter_domain,
        type: "string",
        desc: "Filter by domain prefix (e.g., 'programming/ruby')",
        required: false

      # Maximum results to prevent context overflow
      MAX_RESULTS = 50

      # Initialize with storage instance
      #
      # @param storage [Core::Storage] Storage instance
      # @param agent_name [String, Symbol] Agent identifier
      def initialize(storage:, agent_name:)
        super()
        @storage = storage
        @agent_name = agent_name.to_sym
      end

      # Override name to return simple "MemorySearch"
      def name
        "MemorySearch"
      end

      # Execute the tool
      #
      # @param query [String] Natural language search query
      # @param top_k [Integer] Maximum number of results
      # @param threshold [Float] Minimum similarity score
      # @param filter_type [String, nil] Type filter
      # @param filter_domain [String, nil] Domain filter
      # @return [String] Formatted search results
      def execute(query:, top_k: 10, threshold: 0.0, filter_type: nil, filter_domain: nil)
        # Reset state for multiple types post-filtering
        @requested_types = nil

        # 1. Check semantic index availability
        unless @storage.semantic_index
          return validation_error("Semantic search not available (no embedder configured)")
        end

        # 2. Validate parameters
        top_k = validate_top_k(top_k)
        return top_k if top_k.is_a?(String) # Error message

        threshold = validate_threshold(threshold)
        return threshold if threshold.is_a?(String) # Error message

        # 3. Build filter hash (may set @requested_types for multi-type filtering)
        filter = build_filter(filter_type, filter_domain)

        # 4. Perform semantic search
        # For multiple types, we get extra results to compensate for post-filtering
        search_top_k = @requested_types && @requested_types.size > 1 ? top_k * 3 : top_k
        results = @storage.semantic_index.search(
          query: query,
          top_k: search_top_k,
          threshold: threshold,
          filter: filter,
        )

        # 5. Format and return results (handles multi-type post-filtering)
        format_results(results, query, threshold, top_k)
      rescue StandardError => e
        validation_error("Search failed: #{e.message}")
      end

      private

      def validation_error(message)
        "<tool_use_error>InputValidationError: #{message}</tool_use_error>"
      end

      def validate_top_k(value)
        k = value.to_i
        if k <= 0
          return validation_error("top_k must be positive (got: #{value})")
        end

        [k, MAX_RESULTS].min
      end

      def validate_threshold(value)
        t = value.to_f
        if t < 0.0 || t > 1.0
          return validation_error("threshold must be between 0.0 and 1.0 (got: #{value})")
        end

        t
      end

      def build_filter(filter_type, filter_domain)
        filter = {}

        # IMPORTANT: SemanticIndex's apply_filters uses equality checks (==)
        # So filter["type"] = ["concept", "fact"] won't match metadata["type"] = "concept"
        # For multiple types, we pass nil filter and post-filter results in Ruby
        if filter_type
          types = filter_type.split(",").map(&:strip)
          if types.size == 1
            # Single type: use SemanticIndex filter
            filter["type"] = types.first
          else
            # Multiple types: will be filtered in format_results
            # Store for post-filtering but don't add to SemanticIndex filter
            @requested_types = types
          end
        end

        # Domain can be used in filter (it's a string comparison)
        filter["domain"] = filter_domain if filter_domain

        filter.empty? ? nil : filter
      end

      def format_results(results, query, threshold, top_k)
        # Post-filter for multiple types (if requested)
        # This is needed because SemanticIndex's apply_filters only does equality checks
        if @requested_types && @requested_types.size > 1
          results = results.select do |result|
            type = result.dig(:metadata, "type") || result.dig(:metadata, :type)
            @requested_types.include?(type)
          end
        end

        # Limit to requested top_k after filtering
        results = results.take(top_k)

        if results.empty?
          return format_no_results(query, threshold)
        end

        header = "Found #{results.size} #{pluralize("memory", results.size)} " \
          "matching \"#{query}\" (similarity >= #{threshold}):\n\n"

        entries = results.map.with_index(1) do |result, idx|
          format_result_entry(idx, result)
        end

        footer = "\n\nUse MemoryRead to view full content of any memory."

        header + entries.join("\n\n") + footer
      end

      def format_no_results(query, threshold)
        msg = "No memories found matching \"#{query}\""
        msg += " with similarity >= #{threshold}" if threshold > 0.0
        msg + ".\n\nTry:\n" \
          "- Using a more general query\n" \
          "- Lowering the threshold\n" \
          "- Using MemoryGrep for keyword search\n" \
          "- Using MemoryGlob to browse by path"
      end

      def format_result_entry(index, result)
        lines = []
        lines << "#{index}. memory://#{result[:path]} \"#{result[:title]}\" (score: #{format_score(result[:similarity])})"

        # Add metadata for context (access nested metadata correctly)
        metadata_parts = []
        tags = result.dig(:metadata, "tags") || result.dig(:metadata, :tags)
        domain = result.dig(:metadata, "domain") || result.dig(:metadata, :domain)
        type = result.dig(:metadata, "type") || result.dig(:metadata, :type)

        metadata_parts << "Tags: #{tags.join(", ")}" if tags&.any?
        metadata_parts << "Domain: #{domain}" if domain
        metadata_parts << "Type: #{type}" if type

        lines << "   #{metadata_parts.join(" | ")}" if metadata_parts.any?

        lines.join("\n")
      end

      def format_score(score)
        format("%.2f", score)
      end

      def pluralize(word, count)
        count == 1 ? word : "#{word.sub(/y$/, "ie")}s" # memory -> memories
      end
    end
  end
end
