# frozen_string_literal: true

module SwarmMemory
  module Tools
    # Shared module for looking up memory entry titles
    #
    # Provides a consistent way to look up titles for memory entries
    # across different tools (MemoryRead, MemoryGrep, etc.)
    #
    # @example Including in a tool
    #   class MemoryGrep < RubyLLM::Tool
    #     include TitleLookup
    #
    #     def some_method
    #       title = lookup_title("concept/ruby/classes.md")
    #     end
    #   end
    module TitleLookup
      # Look up the title of a memory entry
      #
      # @param path [String] Path to the memory entry
      # @return [String, nil] Title if found, nil otherwise
      #
      # @example
      #   title = lookup_title("concept/ruby/classes.md")
      #   # => "Ruby Classes"
      def lookup_title(path)
        entry = @storage.read_entry(file_path: path)
        entry.title
      rescue StandardError
        nil
      end

      # Format a memory path with its title
      #
      # Normalizes the path (removes memory:// prefix if present) and
      # formats it with the title in quotes if available.
      #
      # @param path [String] Path to the memory entry (with or without memory:// prefix)
      # @return [String] Formatted string like 'memory://path "Title"' or 'memory://path'
      #
      # @example With title found
      #   format_memory_path_with_title("concept/ruby/classes.md")
      #   # => 'memory://concept/ruby/classes.md "Ruby Classes"'
      #
      # @example With memory:// prefix
      #   format_memory_path_with_title("memory://concept/ruby/classes.md")
      #   # => 'memory://concept/ruby/classes.md "Ruby Classes"'
      #
      # @example When title not found
      #   format_memory_path_with_title("nonexistent.md")
      #   # => 'memory://nonexistent.md'
      def format_memory_path_with_title(path)
        normalized_path = path.sub(%r{^memory://}, "")
        title = lookup_title(normalized_path)

        if title
          "memory://#{normalized_path} \"#{title}\""
        else
          "memory://#{normalized_path}"
        end
      end
    end
  end
end
