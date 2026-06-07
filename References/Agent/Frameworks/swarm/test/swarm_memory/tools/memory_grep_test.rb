# frozen_string_literal: true

require_relative "../../swarm_memory_test_helper"

class MemoryGrepToolTest < Minitest::Test
  def setup
    @storage = create_temp_storage
    @tool = SwarmMemory::Tools::MemoryGrep.new(storage: @storage)
  end

  def teardown
    cleanup_storage(@storage)
  end

  # files_with_matches output mode tests

  def test_files_with_matches_includes_titles
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby classes are blueprints for objects",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )
    @storage.write(
      file_path: "concept/ruby/modules.md",
      content: "Ruby modules provide mixins",
      title: "Ruby Modules",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "Ruby")

    assert_match(/Memory entries matching/, result)
    assert_match(%r{- memory://concept/ruby/classes\.md "Ruby Classes"}, result)
    assert_match(%r{- memory://concept/ruby/modules\.md "Ruby Modules"}, result)
  end

  def test_files_with_matches_single_entry
    @storage.write(
      file_path: "fact/people/john.md",
      content: "John is a developer",
      title: "John Smith",
      metadata: { "type" => "fact" },
    )

    result = @tool.execute(pattern: "developer")

    assert_match(/1 entry/, result)
    assert_match(%r{- memory://fact/people/john\.md "John Smith"}, result)
  end

  def test_files_with_matches_no_results
    result = @tool.execute(pattern: "nonexistent")

    assert_match(/No matches found/, result)
  end

  def test_files_with_matches_with_path_filter
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby classes",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )
    @storage.write(
      file_path: "skill/ruby/debugging.md",
      content: "Ruby debugging",
      title: "Ruby Debugging",
      metadata: { "type" => "skill" },
    )

    result = @tool.execute(pattern: "Ruby", path: "concept/")

    assert_match(%r{- memory://concept/ruby/classes\.md "Ruby Classes"}, result)
    refute_match(/debugging/, result)
  end

  def test_files_with_matches_case_insensitive
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "RUBY classes",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "ruby", case_insensitive: true)

    assert_match(%r{- memory://concept/ruby/classes\.md "Ruby Classes"}, result)
  end

  # content output mode tests

  def test_content_mode_shows_matching_lines
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Line 1\nRuby classes here\nLine 3",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "Ruby", output_mode: "content")

    assert_match(%r{memory://concept/ruby/classes\.md:}, result)
    assert_match(/2:.*Ruby classes here/, result)
  end

  def test_content_mode_shows_match_counts
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby one\nRuby two\nRuby three",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "Ruby", output_mode: "content")

    assert_match(/3 matches/, result)
  end

  # count output mode tests

  def test_count_mode_shows_match_counts
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby one\nRuby two",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )
    @storage.write(
      file_path: "concept/ruby/modules.md",
      content: "Ruby modules",
      title: "Ruby Modules",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "Ruby", output_mode: "count")

    assert_match(/3 total matches/, result)
    assert_match(%r{memory://concept/ruby/classes\.md: 2 matches}, result)
    assert_match(%r{memory://concept/ruby/modules\.md: 1 match}, result)
  end

  # error handling tests

  def test_invalid_regex_returns_error
    result = @tool.execute(pattern: "[invalid")

    assert_match(/InputValidationError/, result)
    assert_match(/Invalid regex pattern/, result)
  end

  def test_invalid_output_mode_returns_error
    @storage.write(
      file_path: "concept/test.md",
      content: "test",
      title: "Test",
      metadata: { "type" => "concept" },
    )

    result = @tool.execute(pattern: "test", output_mode: "invalid")

    assert_match(/InputValidationError/, result)
  end

  # Result limiting tests (MAX_RESULTS = 50)

  def test_files_with_matches_truncates_at_max_results
    # Create 75 entries (exceeds MAX_RESULTS of 50)
    75.times do |i|
      @storage.write(
        file_path: "concept/test#{i}.md",
        content: "matching content",
        title: "Test #{i}",
        metadata: { "type" => "concept" },
      )
    end

    result = @tool.execute(pattern: "matching")

    # Should show truncation message
    assert_match(/showing 50 of 75 entries/, result)
    assert_match(/Results limited to first 50 matches/, result)
    assert_match(/Consider:/, result)
    assert_match(/more specific regex pattern/, result)
  end

  def test_content_mode_truncates_at_max_results
    # Create 60 entries (exceeds MAX_RESULTS of 50)
    60.times do |i|
      @storage.write(
        file_path: "fact/entry#{i}.md",
        content: "Line 1\nmatching line\nLine 3",
        title: "Entry #{i}",
        metadata: { "type" => "fact" },
      )
    end

    result = @tool.execute(pattern: "matching", output_mode: "content")

    # Should show truncation in header
    assert_match(/showing 50 of 60 entries/, result)
    # Should have truncation reminder
    assert_match(/Results limited to first 50 entries/, result)
    assert_match(/returned 60 total entries/, result)
  end

  def test_count_mode_truncates_at_max_results
    # Create 80 entries (exceeds MAX_RESULTS of 50)
    80.times do |i|
      @storage.write(
        file_path: "skill/task#{i}.md",
        content: "match match match", # 3 matches per entry
        title: "Task #{i}",
        metadata: { "type" => "skill" },
      )
    end

    result = @tool.execute(pattern: "match", output_mode: "count")

    # Should show truncation: 50 of 80 entries, 150 of 240 matches (80*3=240)
    assert_match(/showing 50 of 80 entries/, result)
    assert_match(/150 of 240 total matches/, result)
    # Should have truncation reminder
    assert_match(/Results limited to first 50 entries/, result)
    assert_match(/returned 80 total entries with 240 matches/, result)
  end

  def test_no_truncation_when_under_max_results
    # Create only 10 entries (well under MAX_RESULTS)
    10.times do |i|
      @storage.write(
        file_path: "concept/small#{i}.md",
        content: "matching content",
        title: "Small #{i}",
        metadata: { "type" => "concept" },
      )
    end

    result = @tool.execute(pattern: "matching")

    # Should NOT show truncation message
    refute_match(/showing.*of.*entries/, result)
    refute_match(/Results limited/, result)
    # Should show normal count
    assert_match(/10 entries/, result)
  end

  def test_truncation_message_suggests_path_filter
    # Create 60 entries in different paths
    60.times do |i|
      @storage.write(
        file_path: "concept/large#{i}.md",
        content: "matching",
        title: "Large #{i}",
        metadata: { "type" => "concept" },
      )
    end

    result = @tool.execute(pattern: "matching")

    # Verify helpful suggestions in reminder
    assert_match(/path filter to narrow scope/, result)
    assert_match(%r{path: "fact/api-design/"}, result)
    assert_match(/more specific regex pattern/, result)
    assert_match(/specific memory category/, result)
  end
end
