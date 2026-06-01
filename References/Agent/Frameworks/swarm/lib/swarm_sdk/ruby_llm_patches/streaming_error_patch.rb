# frozen_string_literal: true

# Hardens RubyLLM::Providers::OpenAI::Streaming#parse_streaming_error against
# non-standard error response shapes returned by OpenAI-compatible proxies
# (e.g. Gemini via Vertex AI).
#
# The upstream implementation assumes `error_data['error']` is always a Hash,
# but some proxies return a bare String ({"error": "message"}) or an Array
# top-level, causing TypeError: no implicit conversion of String into Integer.
#
# This patch adds type guards while preserving the exact original behavior
# for well-formed OpenAI error responses.
#
# Upstream issue: https://github.com/crmne/ruby_llm/issues/XXX

module RubyLLM
  module Providers
    class OpenAI
      module Streaming
        # rubocop:disable Style/ModuleFunction -- module_function is required here
        # to replace both the singleton and instance method copies created by the
        # original module_function call in upstream RubyLLM. extend self would only
        # add a delegation layer and not override the existing singleton method.

        module_function

        def parse_streaming_error(data)
          error_data = JSON.parse(data)
          return unless error_data.is_a?(Hash)

          error = error_data["error"]
          return unless error

          # Some proxies return {"error": "message"} instead of {"error": {"type": ..., "message": ...}}
          return [500, error.to_s] unless error.is_a?(Hash)

          case error["type"]
          when "server_error"
            [500, error["message"]]
          when "rate_limit_exceeded", "insufficient_quota"
            [429, error["message"]]
          else
            [400, error["message"]]
          end
        end
        # rubocop:enable Style/ModuleFunction
      end
    end
  end
end
