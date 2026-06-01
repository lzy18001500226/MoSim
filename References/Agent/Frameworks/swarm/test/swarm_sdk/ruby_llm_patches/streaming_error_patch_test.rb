# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module RubyLLMPatches
    class StreamingErrorPatchTest < Minitest::Test
      # ========== Standard OpenAI error responses (existing behavior) ==========

      def test_parses_server_error
        data = { "error" => { "type" => "server_error", "message" => "Internal error" } }.to_json

        result = parse(data)

        assert_equal([500, "Internal error"], result)
      end

      def test_parses_rate_limit_error
        data = { "error" => { "type" => "rate_limit_exceeded", "message" => "Too many requests" } }.to_json

        result = parse(data)

        assert_equal([429, "Too many requests"], result)
      end

      def test_parses_insufficient_quota_error
        data = { "error" => { "type" => "insufficient_quota", "message" => "Quota exceeded" } }.to_json

        result = parse(data)

        assert_equal([429, "Quota exceeded"], result)
      end

      def test_parses_unknown_error_type_as_400
        data = { "error" => { "type" => "invalid_request", "message" => "Bad request" } }.to_json

        result = parse(data)

        assert_equal([400, "Bad request"], result)
      end

      def test_returns_nil_when_no_error_key
        data = { "id" => "123", "choices" => [] }.to_json

        result = parse(data)

        assert_nil(result)
      end

      # ========== Non-standard proxy responses (new guards) ==========

      def test_handles_string_error_value
        data = { "error" => "Something went wrong" }.to_json

        result = parse(data)

        assert_equal([500, "Something went wrong"], result)
      end

      def test_handles_array_top_level
        data = [{ "error" => { "type" => "server_error", "message" => "fail" } }].to_json

        result = parse(data)

        assert_nil(result)
      end

      def test_handles_integer_error_value
        data = { "error" => 500 }.to_json

        result = parse(data)

        assert_equal([500, "500"], result)
      end

      def test_handles_null_error_value
        data = { "error" => nil }.to_json

        result = parse(data)

        assert_nil(result)
      end

      private

      def parse(data)
        RubyLLM::Providers::OpenAI::Streaming.parse_streaming_error(data)
      end
    end
  end
end
