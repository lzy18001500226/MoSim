# frozen_string_literal: true

require_relative "../../swarm_memory_test_helper"

class TitleLookupTest < Minitest::Test
  # Test class that includes TitleLookup for testing
  class TestTool
    include SwarmMemory::Tools::TitleLookup

    attr_reader :storage

    def initialize(storage:)
      @storage = storage
    end
  end

  def setup
    @storage = create_temp_storage
    @tool = TestTool.new(storage: @storage)
  end

  def teardown
    cleanup_storage(@storage)
  end

  def test_lookup_title_returns_title_when_entry_exists
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby classes content",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    title = @tool.lookup_title("concept/ruby/classes.md")

    assert_equal("Ruby Classes", title)
  end

  def test_lookup_title_returns_nil_when_entry_not_found
    title = @tool.lookup_title("nonexistent/path.md")

    assert_nil(title)
  end

  def test_format_memory_path_with_title_includes_title
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby classes content",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    result = @tool.format_memory_path_with_title("concept/ruby/classes.md")

    assert_equal('memory://concept/ruby/classes.md "Ruby Classes"', result)
  end

  def test_format_memory_path_with_title_strips_memory_prefix
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Ruby classes content",
      title: "Ruby Classes",
      metadata: { "type" => "concept" },
    )

    result = @tool.format_memory_path_with_title("memory://concept/ruby/classes.md")

    assert_equal('memory://concept/ruby/classes.md "Ruby Classes"', result)
  end

  def test_format_memory_path_with_title_omits_title_when_not_found
    result = @tool.format_memory_path_with_title("nonexistent/path.md")

    assert_equal("memory://nonexistent/path.md", result)
  end

  def test_format_memory_path_with_title_handles_special_characters_in_title
    @storage.write(
      file_path: "concept/ruby/classes.md",
      content: "Content",
      title: 'Ruby "Classes" & Modules',
      metadata: { "type" => "concept" },
    )

    result = @tool.format_memory_path_with_title("concept/ruby/classes.md")

    assert_equal('memory://concept/ruby/classes.md "Ruby "Classes" & Modules"', result)
  end
end
