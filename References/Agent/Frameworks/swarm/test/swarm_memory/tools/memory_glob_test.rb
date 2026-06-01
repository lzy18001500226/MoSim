# frozen_string_literal: true

require_relative "../../swarm_memory_test_helper"

class MemoryGlobToolTest < Minitest::Test
  def setup
    @storage = create_temp_storage
    @tool = SwarmMemory::Tools::MemoryGlob.new(storage: @storage)
  end

  def teardown
    cleanup_storage(@storage)
  end

  def test_returns_entries_with_titles
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby classes content",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )
    @storage.write(
      file_path: "concept/ruby/modules.md",
      content: "Ruby modules content",
      title: "Ruby Modules",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "concept/ruby/**")

    assert_match(/Memory entries matching/, result)
    assert_match(%r{- memory://concept/ruby/classes\.md "Ruby Classes"}, result)
    assert_match(%r{- memory://concept/ruby/modules\.md "Ruby Modules"}, result)
  end

  def test_returns_entries_with_size
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby classes content here",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "concept/**")

    # Should include size in bytes
    assert_match(/\(\d+B\)/, result)
  end

  def test_single_entry_shows_singular
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Content",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "concept/ruby/**")

    assert_match(/1 entry/, result)
  end

  def test_multiple_entries_shows_plural
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Content",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )
    @storage.write(
      file_path: "concept/ruby/modules.md",
      content: "Content",
      title: "Ruby Modules",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "concept/ruby/**")

    assert_match(/2 entries/, result)
  end

  def test_no_matches_returns_message
    result = @tool.execute(pattern: "nonexistent/**")

    assert_match(/No entries found matching pattern/, result)
  end

  def test_recursive_glob_finds_nested_entries
    @storage.write(
      file_path: "fact/people/john.md",
      content: "John info",
      title: "John Smith",
      metadata: { "type" => "fact" },
    )
    @storage.write(
      file_path: "fact/api/endpoints.md",
      content: "API endpoints",
      title: "API Endpoints",
      metadata: { "type" => "fact" },
    )

    result = @tool.execute(pattern: "fact/**")

    assert_match(%r{memory://fact/people/john\.md "John Smith"}, result)
    assert_match(%r{memory://fact/api/endpoints\.md "API Endpoints"}, result)
  end

  def test_single_level_glob_only_finds_direct_children
    @storage.write(
      file_path: "skill/debugging.md",
      content: "Debugging",
      title: "Debugging Skills",
      metadata: { "type" => "skill" },
    )
    @storage.write(
      file_path: "skill/ruby/profiling.md",
      content: "Profiling",
      title: "Ruby Profiling",
      metadata: { "type" => "skill" },
    )

    result = @tool.execute(pattern: "skill/*")

    assert_match(%r{memory://skill/debugging\.md "Debugging Skills"}, result)
    # Nested file should not be found with single-level glob
    refute_match(/profiling/, result)
  end

  def test_glob_all_categories
    @storage.write(
      file_path: "concept/test.md",
      content: "Concept",
      title: "Test Concept",
      metadata: { "type" => "concept" },
    )
    @storage.write(
      file_path: "fact/test.md",
      content: "Fact",
      title: "Test Fact",
      metadata: { "type" => "fact" },
    )
    @storage.write(
      file_path: "skill/test.md",
      content: "Skill",
      title: "Test Skill",
      metadata: { "type" => "skill" },
    )
    @storage.write(
      file_path: "experience/test.md",
      content: "Experience",
      title: "Test Experience",
      metadata: { "type" => "experience" },
    )

    result = @tool.execute(pattern: "**/*")

    assert_match(/Test Concept/, result)
    assert_match(/Test Fact/, result)
    assert_match(/Test Skill/, result)
    assert_match(/Test Experience/, result)
  end

  def test_format_bytes_kilobytes
    # Create a file larger than 1KB
    large_content = "x" * 1500
    @storage.write(
      file_path: "concept/large.md",
      content: large_content,
      title: "Large Entry",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "concept/**")

    assert_match(/\d+\.\d+KB/, result)
  end

  def test_title_with_special_characters
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Content",
      title: "Ruby's \"Classes\" & More",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "concept/**")

    assert_match(/Ruby's "Classes" & More/, result)
  end
end
