# frozen_string_literal: true

module SwarmSDK
  # Internal result object for validation phase during snapshot restore
  #
  # Used during restore to track which agents can be restored and which
  # need to be skipped due to configuration mismatches.
  #
  # @api private
  class ValidationResult
    attr_reader :warnings,
      :skipped_agents,
      :restorable_agents,
      :skipped_delegations,
      :restorable_delegations

    # Initialize validation result
    #
    # @param warnings [Array<Hash>] Warning messages with details
    # @param skipped_agents [Array<Symbol>] Names of agents that can't be restored
    # @param restorable_agents [Array<Symbol>] Names of agents that can be restored
    # @param skipped_delegations [Array<String>] Names of delegations that can't be restored
    # @param restorable_delegations [Array<String>] Names of delegations that can be restored
    def initialize(warnings:, skipped_agents:, restorable_agents:,
      skipped_delegations:, restorable_delegations:)
      @warnings = warnings
      @skipped_agents = skipped_agents
      @restorable_agents = restorable_agents
      @skipped_delegations = skipped_delegations
      @restorable_delegations = restorable_delegations
    end
  end
end
