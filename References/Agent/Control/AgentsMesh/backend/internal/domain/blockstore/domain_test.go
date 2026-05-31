package blockstore

import "testing"

func TestLookupTypeSpec(t *testing.T) {
	spec, ok := LookupTypeSpec(BlockTypeTask)
	if !ok {
		t.Fatal("task spec must exist")
	}
	if len(spec.RequiredDataKey) != 1 || spec.RequiredDataKey[0] != "title" {
		t.Fatalf("task required keys changed: %v", spec.RequiredDataKey)
	}
	if _, ok := LookupTypeSpec("does_not_exist"); ok {
		t.Fatal("unknown type must not resolve")
	}
}

func TestValidateRequiredFields(t *testing.T) {
	if missing := ValidateRequiredFields(BlockTypeTask, JSONMap{"title": "x"}); missing != "" {
		t.Fatalf("expected no missing, got %q", missing)
	}
	if missing := ValidateRequiredFields(BlockTypeTask, JSONMap{}); missing != "title" {
		t.Fatalf("expected 'title' missing, got %q", missing)
	}
	// Unknown types should short-circuit to empty (allowing forward compat).
	if missing := ValidateRequiredFields("custom", JSONMap{}); missing != "" {
		t.Fatalf("unknown type must not fail validation, got %q", missing)
	}
}

func TestIsChildAllowed(t *testing.T) {
	// Pages accept any child by default.
	if !IsChildAllowed(BlockTypePage, BlockTypeParagraph) {
		t.Fatal("page should accept paragraph")
	}
	// Tasks only accept task + paragraph.
	if !IsChildAllowed(BlockTypeTask, BlockTypeParagraph) {
		t.Fatal("task should accept paragraph child")
	}
	if IsChildAllowed(BlockTypeTask, BlockTypePage) {
		t.Fatal("task should not accept page as child")
	}
}

func TestRelSemantics(t *testing.T) {
	if !IsOrderedRel(RelNest) {
		t.Fatal("nest must be ordered")
	}
	if IsOrderedRel(RelMention) {
		t.Fatal("mention must not be ordered")
	}
	if !IsUniqueParentRel(RelNest) {
		t.Fatal("nest must enforce single parent")
	}
	if IsUniqueParentRel(RelMention) {
		t.Fatal("mention must not enforce single parent")
	}
}

func TestJSONMapClone(t *testing.T) {
	src := JSONMap{"title": "x", "count": 1, "nested": JSONMap{"a": 1}}
	dst := src.Clone()
	if dst["title"] != "x" {
		t.Fatal("clone must preserve top-level fields")
	}
	dst["title"] = "changed"
	if src["title"] != "x" {
		t.Fatal("clone must be detached from source")
	}
}
