# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Permissions
    class PathMatcherTest < Minitest::Test
      def test_matches_with_simple_wildcard
        assert(PathMatcher.matches?("*.rb", "test.rb"))
        assert(PathMatcher.matches?("*.rb", "foo.rb"))
        refute(PathMatcher.matches?("*.rb", "test.txt"))
        refute(PathMatcher.matches?("*.rb", "dir/test.rb")) # FNM_PATHNAME: * doesn't cross /
      end

      def test_matches_with_recursive_wildcard
        assert(PathMatcher.matches?("**/*.rb", "test.rb"))
        assert(PathMatcher.matches?("**/*.rb", "dir/test.rb"))
        assert(PathMatcher.matches?("**/*.rb", "dir/subdir/test.rb"))
        refute(PathMatcher.matches?("**/*.rb", "test.txt"))
      end

      def test_matches_with_specific_path
        assert(PathMatcher.matches?("tmp/file.txt", "tmp/file.txt"))
        refute(PathMatcher.matches?("tmp/file.txt", "tmp/other.txt"))
        refute(PathMatcher.matches?("tmp/file.txt", "other/file.txt"))
      end

      def test_matches_with_question_mark
        assert(PathMatcher.matches?("file?.txt", "file1.txt"))
        assert(PathMatcher.matches?("file?.txt", "fileA.txt"))
        refute(PathMatcher.matches?("file?.txt", "file12.txt"))
      end

      def test_matches_with_bracket_patterns
        assert(PathMatcher.matches?("file[123].txt", "file1.txt"))
        assert(PathMatcher.matches?("file[123].txt", "file2.txt"))
        refute(PathMatcher.matches?("file[123].txt", "file4.txt"))
      end

      def test_matches_with_brace_expansion
        assert(PathMatcher.matches?("*.{rb,js}", "test.rb"))
        assert(PathMatcher.matches?("*.{rb,js}", "test.js"))
        refute(PathMatcher.matches?("*.{rb,js}", "test.txt"))
      end

      def test_matches_with_negation_prefix_removed
        # Negation prefix ! should be stripped before matching
        assert(PathMatcher.matches?("!*.rb", "test.rb")) # ! is removed, then matches
        assert(PathMatcher.matches?("!tmp/**/*", "tmp/file.txt"))
      end

      def test_matches_with_directory_prefix
        assert(PathMatcher.matches?("src/**/*.rb", "src/lib/file.rb"))
        assert(PathMatcher.matches?("src/**/*.rb", "src/file.rb"))
        refute(PathMatcher.matches?("src/**/*.rb", "lib/file.rb"))
      end

      def test_matches_with_complex_pattern
        assert(PathMatcher.matches?("test/**/fixtures/*.{yml,yaml}", "test/fixtures/sample.yml"))
        assert(PathMatcher.matches?("test/**/fixtures/*.{yml,yaml}", "test/sub/fixtures/sample.yaml"))
        refute(PathMatcher.matches?("test/**/fixtures/*.{yml,yaml}", "test/fixtures/sample.rb"))
      end

      def test_matches_handles_absolute_paths
        assert(PathMatcher.matches?("/tmp/*.log", "/tmp/test.log"))
        refute(PathMatcher.matches?("/tmp/*.log", "/var/test.log"))
      end

      def test_matches_with_empty_pattern
        refute(PathMatcher.matches?("", "test.rb"))
      end

      def test_matches_with_empty_path
        refute(PathMatcher.matches?("*.rb", ""))
      end

      def test_matches_case_sensitive
        refute(PathMatcher.matches?("*.RB", "test.rb"))
        assert(PathMatcher.matches?("*.RB", "test.RB"))
      end
    end
  end
end
