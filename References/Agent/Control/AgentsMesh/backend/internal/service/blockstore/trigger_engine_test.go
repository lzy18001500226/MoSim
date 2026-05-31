package blockstoreservice

import (
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/stretchr/testify/assert"
)

// Unit tests for the predicate expression evaluator. Kept distinct from the
// integration test because the evaluator is shared across every trigger and
// needs edge-case coverage.
func TestEvalTriggerPredicate(t *testing.T) {
	data := blockstore.JSONMap{
		"progress": 0.5,
		"status":   "done",
		"count":    5.0,
	}

	cases := []struct {
		name string
		expr string
		want bool
	}{
		{"empty", "", true},
		{"true literal", "true", true},
		{"false literal", "false", false},
		{"numeric lt fail", "{progress} < 0.3", false},
		{"numeric lt pass", "{progress} < 0.8", true},
		{"numeric ge pass", "{progress} >= 0.5", true},
		{"numeric ge fail", "{progress} >= 0.6", false},
		{"string eq pass", `{status} == "done"`, true},
		{"string eq fail", `{status} == "todo"`, false},
		{"string ne pass", `{status} != "todo"`, true},
		{"missing col numeric", "{missing} > 0", false},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := evalTriggerPredicate(tc.expr, data)
			assert.Equal(t, tc.want, got, "expr=%q", tc.expr)
		})
	}
}
