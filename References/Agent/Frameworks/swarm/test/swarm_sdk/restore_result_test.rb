# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  class RestoreResultTest < Minitest::Test
    def test_success_with_no_warnings
      result = RestoreResult.new(
        warnings: [],
        skipped_agents: [],
        skipped_delegations: [],
      )

      assert_predicate(result, :success?)
      refute_predicate(result, :partial_restore?)
      assert_equal("Snapshot restored successfully. All agents restored.", result.summary)
    end

    def test_partial_restore_with_warnings
      result = RestoreResult.new(
        warnings: [{ message: "Agent 'foo' not found" }],
        skipped_agents: [:foo],
        skipped_delegations: [],
      )

      refute_predicate(result, :success?)
      assert_predicate(result, :partial_restore?)
      assert_equal("Snapshot restored with warnings. 1 agents skipped, 0 delegation instances skipped.", result.summary)
    end

    def test_partial_restore_with_skipped_agents_and_delegations
      result = RestoreResult.new(
        warnings: [
          { message: "Agent 'foo' not found" },
          { message: "Agent 'bar' not found" },
          { message: "Delegation 'baz->qux' cannot be restored" },
        ],
        skipped_agents: [:foo, :bar],
        skipped_delegations: ["baz->qux"],
      )

      refute_predicate(result, :success?)
      assert_predicate(result, :partial_restore?)
      assert_equal("Snapshot restored with warnings. 2 agents skipped, 1 delegation instances skipped.", result.summary)
    end

    def test_multiple_skipped_delegations
      result = RestoreResult.new(
        warnings: [
          { message: "Delegation 'a->b' cannot be restored" },
          { message: "Delegation 'c->d' cannot be restored" },
          { message: "Delegation 'e->f' cannot be restored" },
        ],
        skipped_agents: [],
        skipped_delegations: ["a->b", "c->d", "e->f"],
      )

      refute_predicate(result, :success?)
      assert_predicate(result, :partial_restore?)
      assert_equal("Snapshot restored with warnings. 0 agents skipped, 3 delegation instances skipped.", result.summary)
    end

    def test_warnings_accessor
      warnings = [
        { message: "Warning 1", details: "Detail 1" },
        { message: "Warning 2", details: "Detail 2" },
      ]
      result = RestoreResult.new(
        warnings: warnings,
        skipped_agents: [],
        skipped_delegations: [],
      )

      assert_equal(warnings, result.warnings)
    end

    def test_skipped_agents_accessor
      skipped = [:agent1, :agent2, :agent3]
      result = RestoreResult.new(
        warnings: [{ message: "test" }],
        skipped_agents: skipped,
        skipped_delegations: [],
      )

      assert_equal(skipped, result.skipped_agents)
    end

    def test_skipped_delegations_accessor
      skipped = ["delegation1", "delegation2"]
      result = RestoreResult.new(
        warnings: [{ message: "test" }],
        skipped_agents: [],
        skipped_delegations: skipped,
      )

      assert_equal(skipped, result.skipped_delegations)
    end
  end
end
