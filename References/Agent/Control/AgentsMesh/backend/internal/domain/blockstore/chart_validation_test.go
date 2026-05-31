package blockstore

import "testing"

// Regression for chart block schema: the bootstrap spec declares
// EnumValues["type"] = bar|line|pie|area|scatter|radar, and NonEmptyArrayKeys
// = ["series"]. Any data that fails these checks must be rejected by
// ValidateRecord — without which garbage ("type":"3d_sphere", "series":[])
// reaches the DB and breaks the renderer.

func TestChartSpec_Validation(t *testing.T) {
	spec, ok := LookupTypeSpec(BlockTypeChart)
	if !ok {
		t.Fatal("chart spec not registered")
	}

	valid := JSONMap{
		"type": "bar",
		"series": []any{
			map[string]any{"name": "A", "data": []any{map[string]any{"x": 1, "value": 10}}},
		},
	}
	if key, reason := spec.ValidateRecord(valid); key != "" {
		t.Fatalf("valid chart rejected: key=%q reason=%q", key, reason)
	}

	cases := []struct {
		name    string
		data    JSONMap
		wantKey string
	}{
		{"unknown chart type", JSONMap{"type": "3d_sphere", "series": []any{map[string]any{"data": []any{}}}}, "type"},
		{"empty series", JSONMap{"type": "bar", "series": []any{}}, "series"},
		{"series not an array", JSONMap{"type": "bar", "series": "not-an-array"}, "series"},
		{"missing type", JSONMap{"series": []any{map[string]any{"data": []any{}}}}, "type"},
		{"missing series", JSONMap{"type": "bar"}, "series"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			gotKey, reason := spec.ValidateRecord(tc.data)
			if gotKey == "" {
				t.Fatalf("expected rejection on key %q, got success", tc.wantKey)
			}
			if gotKey != tc.wantKey {
				t.Fatalf("rejected key=%q reason=%q, wanted key=%q", gotKey, reason, tc.wantKey)
			}
		})
	}
}
