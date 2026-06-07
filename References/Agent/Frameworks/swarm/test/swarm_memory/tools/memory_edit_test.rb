# frozen_string_literal: true

require_relative "../../swarm_memory_test_helper"

class MemoryEditToolTest < Minitest::Test
  def setup
    @storage = create_temp_storage
    @agent_name = :test_agent

    # Create MemoryRead tool for read-before-edit tracking
    @read_tool = SwarmMemory::Tools::MemoryRead.new(storage: @storage, agent_name: @agent_name)

    # Create MemoryEdit tool
    @edit_tool = SwarmMemory::Tools::MemoryEdit.new(storage: @storage, agent_name: @agent_name)

    # Write a test entry with full metadata
    @storage.write(
      file_path: "test/example.md",
      content: "# Original Content\n\nThis is the original content that will be edited.",
      title: "Example Entry",
      metadata: {
        "type" => "concept",
        "confidence" => "high",
        "tags" => ["ruby", "test", "example"],
        "domain" => "programming/ruby",
        "source" => "documentation",
        "last_verified" => "2025-01-01",
        "related" => ["memory://test/related.md"],
      },
    )
  end

  def teardown
    cleanup_storage(@storage)
  end

  # Basic functionality tests

  def test_edit_replaces_content
    # Read entry first (required for edit)
    @read_tool.execute(file_path: "test/example.md")

    result = @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "original content",
      new_string: "updated content",
    )

    assert_match(/Successfully replaced/, result)
    assert_match(%r{memory://test/example.md}, result)

    # Verify content was updated
    entry = @storage.read_entry(file_path: "test/example.md")

    assert_match(/updated content/, entry.content)
    refute_match(/original content/, entry.content)
  end

  def test_edit_with_multiline_string
    # Read entry first
    @read_tool.execute(file_path: "test/example.md")

    old_text = "# Original Content\n\nThis is the original content"
    new_text = "# Updated Content\n\nThis is the updated content"

    result = @edit_tool.execute(
      file_path: "test/example.md",
      old_string: old_text,
      new_string: new_text,
    )

    assert_match(/Successfully replaced/, result)

    entry = @storage.read_entry(file_path: "test/example.md")

    assert_match(/Updated Content/, entry.content)
  end

  # Metadata preservation tests (the critical bug we fixed)

  def test_preserves_all_metadata_after_edit
    # Read entry first
    @read_tool.execute(file_path: "test/example.md")

    # Edit the content
    @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "original",
      new_string: "modified",
    )

    # Verify ALL metadata is preserved
    entry = @storage.read_entry(file_path: "test/example.md")

    assert_equal("concept", entry.metadata["type"], "Type should be preserved")
    assert_equal("high", entry.metadata["confidence"], "Confidence should be preserved")
    assert_equal(["ruby", "test", "example"], entry.metadata["tags"], "Tags should be preserved")
    assert_equal("programming/ruby", entry.metadata["domain"], "Domain should be preserved")
    assert_equal("documentation", entry.metadata["source"], "Source should be preserved")
    assert_equal("2025-01-01", entry.metadata["last_verified"], "Last verified should be preserved")
    assert_equal(["memory://test/related.md"], entry.metadata["related"], "Related should be preserved")
  end

  def test_preserves_title_after_edit
    # Read entry first
    @read_tool.execute(file_path: "test/example.md")

    # Edit the content
    @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "original content",
      new_string: "updated content",
    )

    entry = @storage.read_entry(file_path: "test/example.md")

    assert_equal("Example Entry", entry.title, "Title should be preserved")
  end

  def test_preserves_metadata_with_empty_fields
    # Write entry with minimal metadata
    @storage.write(
      file_path: "test/minimal.md",
      content: "Minimal content",
      title: "Minimal",
      metadata: {
        "type" => "fact",
        "confidence" => "low",
        "tags" => [],
        "related" => [],
      },
    )

    @read_tool.execute(file_path: "test/minimal.md")

    @edit_tool.execute(
      file_path: "test/minimal.md",
      old_string: "Minimal",
      new_string: "Modified",
    )

    entry = @storage.read_entry(file_path: "test/minimal.md")

    assert_equal("fact", entry.metadata["type"])
    assert_equal("low", entry.metadata["confidence"])
    assert_empty(entry.metadata["tags"])
    assert_empty(entry.metadata["related"])
  end

  def test_preserves_skill_metadata_with_tools_and_permissions
    # Write a skill with tools and permissions
    @storage.write(
      file_path: "skill/test-skill.md",
      content: "# Test Skill\n\nStep-by-step instructions.",
      title: "Test Skill",
      metadata: {
        "type" => "skill",
        "confidence" => "high",
        "tags" => ["testing", "automation"],
        "tools" => ["Read", "Write", "Bash"],
        "permissions" => {
          "Bash" => { "allowed_commands" => ["^npm"] },
        },
      },
    )

    @read_tool.execute(file_path: "skill/test-skill.md")

    @edit_tool.execute(
      file_path: "skill/test-skill.md",
      old_string: "instructions",
      new_string: "procedures",
    )

    entry = @storage.read_entry(file_path: "skill/test-skill.md")

    assert_equal("skill", entry.metadata["type"])
    assert_equal(["Read", "Write", "Bash"], entry.metadata["tools"])
    assert_equal({ "Bash" => { "allowed_commands" => ["^npm"] } }, entry.metadata["permissions"])
  end

  # Read-before-edit enforcement tests

  def test_requires_read_before_edit
    # Clear read tracker to ensure clean state
    SwarmMemory::Core::StorageReadTracker.clear(@agent_name)

    # Don't read the entry first
    result = @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "original",
      new_string: "updated",
    )

    assert_match(/<tool_use_error>/, result)
    assert_match(/Cannot edit memory entry without reading/i, result)
    assert_match(/MemoryRead/, result)
  end

  def test_allows_edit_after_read
    # Read entry first - should allow edit
    @read_tool.execute(file_path: "test/example.md")

    # Should succeed
    result = @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "original",
      new_string: "updated",
    )

    assert_match(/Successfully replaced/, result)
  end

  # Error handling tests

  def test_fails_on_nonexistent_file
    @read_tool.execute(file_path: "test/example.md")

    result = @edit_tool.execute(
      file_path: "test/nonexistent.md",
      old_string: "anything",
      new_string: "something",
    )

    assert_match(/<tool_use_error>/, result)
    assert_match(/not found|does not exist/i, result)
  end

  def test_fails_when_old_string_not_found
    @read_tool.execute(file_path: "test/example.md")

    result = @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "this text does not exist in the file",
      new_string: "replacement",
    )

    assert_match(/<tool_use_error>/, result)
    assert_match(/not found/i, result)
  end

  def test_fails_when_old_string_not_unique
    @read_tool.execute(file_path: "test/example.md")

    # Write content with duplicate strings
    @storage.write(
      file_path: "test/duplicate.md",
      content: "test test test",
      title: "Duplicate",
      metadata: { "type" => "fact" },
    )

    @read_tool.execute(file_path: "test/duplicate.md")

    result = @edit_tool.execute(
      file_path: "test/duplicate.md",
      old_string: "test",
      new_string: "updated",
    )

    assert_match(/<tool_use_error>/, result)
    assert_match(/3 occurrences/i, result)
  end

  def test_fails_with_empty_old_string
    @read_tool.execute(file_path: "test/example.md")

    result = @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "",
      new_string: "something",
    )

    assert_match(/<tool_use_error>/, result)
    assert_match(/old_string.*required/i, result)
  end

  def test_allows_empty_new_string_for_deletion
    @read_tool.execute(file_path: "test/example.md")

    # Should allow empty new_string (effectively deleting the text)
    result = @edit_tool.execute(
      file_path: "test/example.md",
      old_string: " that will be edited",
      new_string: "",
    )

    assert_match(/Successfully replaced/, result)

    entry = @storage.read_entry(file_path: "test/example.md")

    refute_match(/that will be edited/, entry.content)
  end

  # Edge cases

  def test_edit_preserves_special_characters
    @storage.write(
      file_path: "test/special.md",
      content: "Code: `const x = 5;` and **bold** text",
      title: "Special Chars",
      metadata: {
        "type" => "fact",
        "tags" => ["code"],
      },
    )

    @read_tool.execute(file_path: "test/special.md")

    @edit_tool.execute(
      file_path: "test/special.md",
      old_string: "`const x = 5;`",
      new_string: "`const x = 10;`",
    )

    entry = @storage.read_entry(file_path: "test/special.md")

    assert_match(/`const x = 10;`/, entry.content)
    assert_match(/\*\*bold\*\*/, entry.content)
  end

  def test_edit_with_regex_special_characters
    @storage.write(
      file_path: "test/regex.md",
      content: "Price: $100.00 (including tax)",
      title: "Regex Test",
      metadata: { "type" => "fact" },
    )

    @read_tool.execute(file_path: "test/regex.md")

    # These characters should be treated literally, not as regex
    @edit_tool.execute(
      file_path: "test/regex.md",
      old_string: "$100.00",
      new_string: "$150.00",
    )

    entry = @storage.read_entry(file_path: "test/regex.md")

    assert_match(/\$150\.00/, entry.content)
  end

  def test_consecutive_edits_on_same_file
    @read_tool.execute(file_path: "test/example.md")

    # First edit
    @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "original content",
      new_string: "modified content",
    )

    # Read again for second edit
    @read_tool.execute(file_path: "test/example.md")

    # Second edit on the updated content
    @edit_tool.execute(
      file_path: "test/example.md",
      old_string: "modified content",
      new_string: "final content",
    )

    entry = @storage.read_entry(file_path: "test/example.md")

    assert_match(/final content/, entry.content)
    refute_match(/original content/, entry.content)
    refute_match(/modified content/, entry.content)

    # Verify metadata still preserved after multiple edits
    assert_equal("concept", entry.metadata["type"])
    assert_equal(["ruby", "test", "example"], entry.metadata["tags"])
  end

  def test_edit_normalizes_file_path
    @read_tool.execute(file_path: "test/example") # Without .md

    # Edit with different path format
    result = @edit_tool.execute(
      file_path: "test/example", # Without .md
      old_string: "original",
      new_string: "updated",
    )

    assert_match(/Successfully replaced/, result)

    # Should work with either format
    entry = @storage.read_entry(file_path: "test/example.md")

    assert_match(/updated/, entry.content)
  end
end
