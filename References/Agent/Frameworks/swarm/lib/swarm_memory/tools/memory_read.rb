# frozen_string_literal: true

module SwarmMemory
  module Tools
    # Tool for reading content from memory storage
    #
    # Retrieves content stored by this agent using memory_write.
    # Each agent has its own isolated memory storage.
    class MemoryRead < SwarmSDK::Tools::Base
      removable false # Memory tools are always available

      include TitleLookup

      description <<~DESC
        Read content from your memory storage.

        REQUIRED: Provide the file_path parameter - the path to the memory entry you want to read.

        **Parameters:**
        - file_path (REQUIRED): Path to memory entry - MUST start with concept/, fact/, skill/, or experience/

        **MEMORY STRUCTURE - EXACTLY 4 Top-Level Categories (NEVER create others):**
        ALL paths MUST start with one of these 4 fixed categories:
        - concept/{domain}/{name}.md - Abstract ideas (e.g., concept/ruby/classes.md)
        - fact/{subfolder}/{name}.md - Concrete info (e.g., fact/people/john.md)
        - skill/{domain}/{name}.md - Procedures (e.g., skill/debugging/api-errors.md)
        - experience/{name}.md - Lessons (e.g., experience/fixed-bug.md)

        INVALID: documentation/, reference/, tutorial/, parallel/, analysis/, notes/

        **Returns:**
        Markdown content with line numbers (same format as 'cat -n').
        If the entry has related memories, a system-reminder section is appended listing them.

        **Examples:**
        - MemoryRead(file_path: "concept/ruby/classes.md") - Read a concept
        - MemoryRead(file_path: "fact/people/john.md") - Read a fact
        - MemoryRead(file_path: "skill/debugging/api-errors.md") - Read a skill before loading it

        **Important:**
        - Always read entries before editing them with MemoryEdit
        - Line numbers in output are for reference only - don't include them when editing
        - Each read is tracked to enforce read-before-edit patterns
        - Related memories in the system-reminder can be read with MemoryRead for additional context
      DESC

      param :file_path,
        desc: "Path to read from memory - MUST start with concept/, fact/, skill/, or experience/ (e.g., 'concept/ruby/classes.md', 'skill/debugging/api.md')",
        required: true

      # Initialize with storage instance and agent name
      #
      # @param storage [Core::Storage] Storage instance
      # @param agent_name [String, Symbol] Agent identifier
      def initialize(storage:, agent_name:)
        super()
        @storage = storage
        @agent_name = agent_name.to_sym
      end

      # Override name to return simple "MemoryRead"
      def name
        "MemoryRead"
      end

      # Execute the tool
      #
      # @param file_path [String] Path to read from
      # @return [String] Content with line numbers and optional related memories reminder
      def execute(file_path:)
        # Read full entry with metadata
        entry = @storage.read_entry(file_path: file_path)

        # Register this read in the tracker with content digest
        Core::StorageReadTracker.register_read(@agent_name, file_path, entry.content)

        # Return plain text with line numbers
        result = format_with_line_numbers(entry.content)

        # Append related memories reminder if present
        related_paths = entry.metadata&.dig("related") || []
        result += format_related_memories_reminder(related_paths) if related_paths.any?

        result
      rescue ArgumentError => e
        validation_error(e.message)
      end

      private

      def validation_error(message)
        "<tool_use_error>InputValidationError: #{message}</tool_use_error>"
      end

      # Format content with line numbers (same format as Read tool)
      #
      # @param content [String] Content to format
      # @return [String] Content with line numbers
      def format_with_line_numbers(content)
        lines = content.lines
        output_lines = lines.each_with_index.map do |line, idx|
          line_number = idx + 1
          display_line = line.chomp
          "#{line_number.to_s.rjust(6)} #{display_line}"
        end
        output_lines.join("\n")
      end

      # Format related memories as a system-reminder section
      #
      # Looks up titles for each related memory path and formats
      # them as a system reminder to help agents discover related content.
      #
      # @param related_paths [Array<String>] Array of memory paths (with or without memory:// prefix)
      # @return [String] Formatted system-reminder section
      def format_related_memories_reminder(related_paths)
        lines = ["\n\n<system-reminder>"]
        lines << "Related memories that may provide additional context:"

        related_paths.each do |path|
          lines << "- #{format_memory_path_with_title(path)}"
        end

        lines << "</system-reminder>"
        lines.join("\n")
      end
    end
  end
end
