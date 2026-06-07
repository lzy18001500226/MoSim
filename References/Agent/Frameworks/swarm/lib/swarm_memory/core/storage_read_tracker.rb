# frozen_string_literal: true

module SwarmMemory
  module Core
    # StorageReadTracker manages read-entry tracking for all agents with content digest verification
    #
    # This module maintains a global registry of which memory entries each agent
    # has read during their conversation along with SHA256 digests of the content.
    # This enables enforcement of the "read-before-edit" rule that ensures agents
    # have context before modifying entries, AND prevents editing entries that have
    # changed externally since being read.
    #
    # Each agent maintains an independent map of read entries to content digests.
    module StorageReadTracker
      @read_entries = {} # { agent_id => { entry_path => sha256_digest } }
      @mutex = Mutex.new

      class << self
        # Register that an agent has read a storage entry with content digest
        #
        # @param agent_id [Symbol] The agent identifier
        # @param entry_path [String] The storage entry path
        # @param content [String] Entry content (for digest calculation)
        # @return [String] The calculated SHA256 digest
        def register_read(agent_id, entry_path, content)
          @mutex.synchronize do
            @read_entries[agent_id] ||= {}
            digest = Digest::SHA256.hexdigest(content)
            @read_entries[agent_id][entry_path] = digest
            digest
          end
        end

        # Check if an agent has read an entry AND content hasn't changed
        #
        # @param agent_id [Symbol] The agent identifier
        # @param entry_path [String] The storage entry path
        # @param storage [Storage] Storage instance to read current content
        # @return [Boolean] true if agent read entry and content matches
        def entry_read?(agent_id, entry_path, storage)
          @mutex.synchronize do
            return false unless @read_entries[agent_id]

            stored_digest = @read_entries[agent_id][entry_path]
            return false unless stored_digest

            # Check if entry still matches stored digest
            begin
              current_content = storage.read(file_path: entry_path)
              current_digest = Digest::SHA256.hexdigest(current_content)
              current_digest == stored_digest
            rescue StandardError
              false # Entry deleted or inaccessible
            end
          end
        end

        # Get all read entries with digests for snapshot
        #
        # @param agent_id [Symbol] The agent identifier
        # @return [Hash] { entry_path => digest }
        def get_read_entries(agent_id)
          @mutex.synchronize do
            @read_entries[agent_id]&.dup || {}
          end
        end

        # Restore read entries with digests from snapshot
        #
        # @param agent_id [Symbol] The agent identifier
        # @param entries_with_digests [Hash] { entry_path => digest }
        # @return [void]
        def restore_read_entries(agent_id, entries_with_digests)
          @mutex.synchronize do
            @read_entries[agent_id] = entries_with_digests.dup
          end
        end

        # Clear read history for an agent (useful for testing)
        #
        # @param agent_id [Symbol] The agent identifier
        # @return [void]
        def clear(agent_id)
          @mutex.synchronize do
            @read_entries.delete(agent_id)
          end
        end

        # Clear all read history (useful for testing)
        #
        # @return [void]
        def clear_all
          @mutex.synchronize do
            @read_entries.clear
          end
        end
      end
    end
  end
end
