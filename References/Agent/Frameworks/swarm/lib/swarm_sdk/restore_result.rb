# frozen_string_literal: true

module SwarmSDK
  # Result object returned from snapshot restore operations
  #
  # Provides information about the restore process, including any warnings
  # about agents or delegations that couldn't be restored due to configuration
  # mismatches.
  #
  # @example Successful restore
  #   result = swarm.restore(snapshot_data)
  #   if result.success?
  #     puts "All agents restored successfully"
  #   end
  #
  # @example Partial restore with warnings
  #   result = swarm.restore(snapshot_data)
  #   if result.partial_restore?
  #     puts result.summary
  #     result.warnings.each do |warning|
  #       puts "  - #{warning[:message]}"
  #     end
  #   end
  class RestoreResult
    attr_reader :warnings, :skipped_agents, :skipped_delegations

    # Initialize restore result
    #
    # @param warnings [Array<Hash>] Warning messages with details
    # @param skipped_agents [Array<Symbol>] Names of agents that couldn't be restored
    # @param skipped_delegations [Array<String>] Names of delegation instances that couldn't be restored
    def initialize(warnings:, skipped_agents:, skipped_delegations:)
      @warnings = warnings
      @skipped_agents = skipped_agents
      @skipped_delegations = skipped_delegations
    end

    # Check if restore was completely successful
    #
    # @return [Boolean] true if all agents restored without warnings
    def success?
      warnings.empty?
    end

    # Check if restore was partial (some agents skipped)
    #
    # @return [Boolean] true if some agents were skipped
    def partial_restore?
      !warnings.empty?
    end

    # Get human-readable summary of restore result
    #
    # @return [String] Summary message
    def summary
      if success?
        "Snapshot restored successfully. All agents restored."
      else
        "Snapshot restored with warnings. " \
          "#{skipped_agents.size} agents skipped, " \
          "#{skipped_delegations.size} delegation instances skipped."
      end
    end
  end
end
