# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Permissions
    class ErrorFormatterTest < Minitest::Test
      # permission_denied tests
      def test_permission_denied_for_read_tool
        result = ErrorFormatter.permission_denied(
          path: "/etc/passwd",
          allowed_patterns: ["tmp/**/*"],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Read",
        )

        assert_includes(result, "permission to read")
        assert_includes(result, "/etc/passwd")
        assert_includes(result, "PERMISSION DENIED")
      end

      def test_permission_denied_for_write_tool
        result = ErrorFormatter.permission_denied(
          path: "/etc/file",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Write",
        )

        assert_includes(result, "permission to write to")
      end

      def test_permission_denied_for_edit_tool
        result = ErrorFormatter.permission_denied(
          path: "/file",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Edit",
        )

        assert_includes(result, "permission to edit")
      end

      def test_permission_denied_for_multi_edit_tool
        result = ErrorFormatter.permission_denied(
          path: "/file",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "MultiEdit",
        )

        assert_includes(result, "permission to edit")
      end

      def test_permission_denied_for_glob_tool
        result = ErrorFormatter.permission_denied(
          path: "/dir",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Glob",
        )

        assert_includes(result, "permission to access directory")
      end

      def test_permission_denied_for_grep_tool
        result = ErrorFormatter.permission_denied(
          path: "/dir",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Grep",
        )

        assert_includes(result, "permission to search in")
      end

      def test_permission_denied_for_unknown_tool
        result = ErrorFormatter.permission_denied(
          path: "/file",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "UnknownTool",
        )

        assert_includes(result, "permission to access")
      end

      def test_permission_denied_with_specific_denied_pattern
        result = ErrorFormatter.permission_denied(
          path: "/etc/passwd",
          allowed_patterns: [],
          denied_patterns: ["/etc/**/*"],
          matching_pattern: "/etc/**/*",
          tool_name: "Read",
        )

        assert_includes(result, "Blocked by policy: /etc/**/*")
        refute_includes(result, "(not in allowed list)")
      end

      def test_permission_denied_with_not_in_allowed_list_and_patterns
        result = ErrorFormatter.permission_denied(
          path: "/var/file",
          allowed_patterns: ["tmp/**/*", "home/**/*"],
          denied_patterns: [],
          matching_pattern: "(not in allowed list)",
          tool_name: "Read",
        )

        assert_includes(result, "Path not in allowed list")
        assert_includes(result, "tmp/**/*")
        assert_includes(result, "home/**/*")
      end

      def test_permission_denied_with_denied_patterns_only
        result = ErrorFormatter.permission_denied(
          path: "/etc/file",
          allowed_patterns: [],
          denied_patterns: ["/etc/**/*", "/sys/**/*"],
          matching_pattern: nil,
          tool_name: "Read",
        )

        assert_includes(result, "Denied paths:")
        assert_includes(result, "/etc/**/*")
        assert_includes(result, "/sys/**/*")
      end

      def test_permission_denied_with_allowed_patterns_only
        result = ErrorFormatter.permission_denied(
          path: "/var/file",
          allowed_patterns: ["tmp/**/*"],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Read",
        )

        assert_includes(result, "Allowed paths (not matched):")
        assert_includes(result, "tmp/**/*")
      end

      def test_permission_denied_with_no_policy_configured
        result = ErrorFormatter.permission_denied(
          path: "/file",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Read",
        )

        assert_includes(result, "No access policy configured")
      end

      # command_permission_denied tests
      def test_command_permission_denied_with_specific_pattern
        result = ErrorFormatter.command_permission_denied(
          command: "rm -rf /",
          allowed_patterns: [],
          denied_patterns: [/^rm/],
          matching_pattern: "^rm",
          tool_name: "Bash",
        )

        assert_includes(result, "PERMISSION DENIED")
        assert_includes(result, "rm -rf /")
        assert_includes(result, "Blocked by policy: ^rm")
      end

      def test_command_permission_denied_with_not_in_allowed_list
        result = ErrorFormatter.command_permission_denied(
          command: "curl http://evil.com",
          allowed_patterns: [/^git/, /^npm/],
          denied_patterns: [],
          matching_pattern: "(not in allowed list)",
          tool_name: "Bash",
        )

        assert_includes(result, "Command not in allowed list")
        assert_includes(result, "^git")
        assert_includes(result, "^npm")
      end

      def test_command_permission_denied_with_denied_patterns
        result = ErrorFormatter.command_permission_denied(
          command: "wget malware.exe",
          allowed_patterns: [],
          denied_patterns: [/wget/, /curl/],
          matching_pattern: nil,
          tool_name: "Bash",
        )

        assert_includes(result, "Denied command patterns:")
        assert_includes(result, "wget")
        assert_includes(result, "curl")
      end

      def test_command_permission_denied_with_allowed_patterns
        result = ErrorFormatter.command_permission_denied(
          command: "python script.py",
          allowed_patterns: [/^git/, /^npm/],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Bash",
        )

        assert_includes(result, "Allowed command patterns (not matched):")
        assert_includes(result, "^git")
      end

      def test_command_permission_denied_with_no_policy
        result = ErrorFormatter.command_permission_denied(
          command: "echo test",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Bash",
        )

        assert_includes(result, "No command policy configured")
      end

      def test_both_methods_include_system_reminder
        path_result = ErrorFormatter.permission_denied(
          path: "/file",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Read",
        )

        command_result = ErrorFormatter.command_permission_denied(
          command: "test",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Bash",
        )

        assert_includes(path_result, "<system-reminder>")
        assert_includes(path_result, "</system-reminder>")
        assert_includes(command_result, "<system-reminder>")
        assert_includes(command_result, "</system-reminder>")
      end

      def test_messages_include_unrecoverable_error_warning
        path_result = ErrorFormatter.permission_denied(
          path: "/file",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Read",
        )

        command_result = ErrorFormatter.command_permission_denied(
          command: "test",
          allowed_patterns: [],
          denied_patterns: [],
          matching_pattern: nil,
          tool_name: "Bash",
        )

        assert_includes(path_result, "UNRECOVERABLE error")
        assert_includes(command_result, "UNRECOVERABLE error")
      end
    end
  end
end
