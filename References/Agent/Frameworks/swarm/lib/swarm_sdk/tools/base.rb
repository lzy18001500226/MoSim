# frozen_string_literal: true

module SwarmSDK
  module Tools
    # Base class for all SwarmSDK tools
    #
    # Provides:
    # - Declarative removability control
    # - Common tool functionality
    # - Standard initialization patterns
    #
    # ## Removability
    #
    # Tools can be marked as non-removable to ensure they're always available:
    #
    #   class Think < Base
    #     removable false
    #   end
    #
    # Non-removable tools are included even when skills specify a limited toolset.
    #
    # @example Removable tool (default)
    #   class Read < Base
    #     # removable true  # Default, can omit
    #   end
    #
    # @example Non-removable tool
    #   class Think < Base
    #     removable false  # Always available
    #   end
    class Base < RubyLLM::Tool
      class << self
        # Whether this tool can be deactivated by LoadSkill
        #
        # Non-removable tools are ALWAYS active regardless of skill toolset.
        # Use for essential tools that agents should never lose.
        #
        # @return [Boolean] True if removable (default: true)
        def removable?
          @removable.nil? ? true : @removable
        end

        # Mark tool as removable or non-removable
        #
        # @param value [Boolean] Whether tool can be removed
        # @return [void]
        #
        # @example Make tool always available
        #   removable false
        def removable(value)
          @removable = value
        end
      end

      # Instance method for checking removability
      #
      # @return [Boolean]
      def removable?
        self.class.removable?
      end
    end
  end
end
