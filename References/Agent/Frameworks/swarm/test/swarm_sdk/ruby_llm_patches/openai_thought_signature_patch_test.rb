# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module RubyLLMPatches
    class OpenAIThoughtSignaturePatchTest < Minitest::Test
      # ========== parse_tool_calls: standard behavior preserved ==========

      def test_parse_returns_nil_for_nil_input
        result = parse_tool_calls(nil)

        assert_nil(result)
      end

      def test_parse_returns_nil_for_empty_array
        result = parse_tool_calls([])

        assert_nil(result)
      end

      def test_parse_extracts_id_name_and_arguments
        tool_calls = [standard_tool_call]

        result = parse_tool_calls(tool_calls)

        tc = result["call_123"]

        assert_equal("call_123", tc.id)
        assert_equal("Clock", tc.name)
        assert_empty(tc.arguments)
      end

      def test_parse_with_arguments_true_parses_json
        tool_calls = [standard_tool_call("query" => "hello")]

        result = parse_tool_calls(tool_calls, parse_arguments: true)

        assert_equal({ "query" => "hello" }, result["call_123"].arguments)
      end

      def test_parse_with_arguments_false_keeps_raw_string
        tool_calls = [standard_tool_call("query" => "hello")]

        result = parse_tool_calls(tool_calls, parse_arguments: false)

        assert_equal('{"query":"hello"}', result["call_123"].arguments)
      end

      def test_parse_without_thought_signature_sets_nil
        tool_calls = [standard_tool_call]

        result = parse_tool_calls(tool_calls)

        assert_nil(result["call_123"].thought_signature)
      end

      # ========== parse_tool_calls: thought_signature extraction ==========

      def test_parse_extracts_thought_signature_from_extra_content
        tool_calls = [tool_call_with_signature("sig_abc123")]

        result = parse_tool_calls(tool_calls)

        assert_equal("sig_abc123", result["call_123"].thought_signature)
      end

      def test_parse_handles_missing_extra_content_gracefully
        tc = standard_tool_call
        tc.delete("extra_content")

        result = parse_tool_calls([tc])

        assert_nil(result["call_123"].thought_signature)
      end

      # ========== format_tool_calls: standard behavior preserved ==========

      def test_format_returns_nil_for_nil_input
        result = format_tool_calls(nil)

        assert_nil(result)
      end

      def test_format_returns_nil_for_empty_hash
        result = format_tool_calls({})

        assert_nil(result)
      end

      def test_format_serializes_standard_tool_call
        tool_calls = { "call_123" => build_tool_call(thought_signature: nil) }

        result = format_tool_calls(tool_calls)

        assert_equal(1, result.length)
        entry = result.first

        assert_equal("call_123", entry[:id])
        assert_equal("function", entry[:type])
        assert_equal("Clock", entry[:function][:name])
        assert_equal("{}", entry[:function][:arguments])
      end

      def test_format_without_thought_signature_omits_extra_content
        tool_calls = { "call_123" => build_tool_call(thought_signature: nil) }

        result = format_tool_calls(tool_calls)

        refute(result.first.key?(:extra_content))
      end

      # ========== format_tool_calls: thought_signature echoing ==========

      def test_format_includes_extra_content_when_thought_signature_present
        tool_calls = { "call_123" => build_tool_call(thought_signature: "sig_abc123") }

        result = format_tool_calls(tool_calls)

        expected_extra = { google: { thought_signature: "sig_abc123" } }

        assert_equal(expected_extra, result.first[:extra_content])
      end

      # ========== round-trip: parse -> format preserves thought_signature ==========

      def test_round_trip_preserves_thought_signature
        raw = [tool_call_with_signature("sig_round_trip")]

        parsed = parse_tool_calls(raw)
        formatted = format_tool_calls(parsed)

        assert_equal("sig_round_trip", formatted.first.dig(:extra_content, :google, :thought_signature))
      end

      def test_round_trip_without_thought_signature_has_no_extra_content
        raw = [standard_tool_call]

        parsed = parse_tool_calls(raw)
        formatted = format_tool_calls(parsed)

        refute(formatted.first.key?(:extra_content))
      end

      private

      def parse_tool_calls(tool_calls, parse_arguments: true)
        RubyLLM::Providers::OpenAI::Tools.parse_tool_calls(tool_calls, parse_arguments: parse_arguments)
      end

      def format_tool_calls(tool_calls)
        RubyLLM::Providers::OpenAI::Tools.format_tool_calls(tool_calls)
      end

      def standard_tool_call(arguments = {})
        {
          "id" => "call_123",
          "type" => "function",
          "function" => {
            "name" => "Clock",
            "arguments" => JSON.generate(arguments),
          },
        }
      end

      def tool_call_with_signature(signature)
        standard_tool_call.merge(
          "extra_content" => {
            "google" => {
              "thought_signature" => signature,
            },
          },
        )
      end

      def build_tool_call(thought_signature:)
        RubyLLM::ToolCall.new(
          id: "call_123",
          name: "Clock",
          arguments: {},
          thought_signature: thought_signature,
        )
      end
    end
  end
end
