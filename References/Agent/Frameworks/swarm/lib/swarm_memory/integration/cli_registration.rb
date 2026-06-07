# frozen_string_literal: true

module SwarmMemory
  module Integration
    # Auto-registration for SwarmCLI commands
    #
    # Registers memory management commands with SwarmCLI when available.
    class CliRegistration
      class << self
        # Register memory CLI commands with SwarmCLI
        #
        # This is called automatically when swarm_memory is required.
        #
        # @return [void]
        def register!
          # Only register if SwarmCLI::CommandRegistry is available
          # Check for the specific class, not just the module
          return unless defined?(SwarmCLI::CommandRegistry)

          # Load CLI commands explicitly (Zeitwerk might not have loaded it yet)
          require_relative "../cli/commands"

          # Register memory command
          SwarmCLI::CommandRegistry.register(:memory, SwarmMemory::CLI::Commands)
        rescue StandardError => e
          warn("Warning: Failed to register SwarmMemory CLI commands: #{e.message}")
        end
      end
    end
  end
end
