# frozen_string_literal: true

# Patches RubyLLM::Providers::OpenAI::Tools to preserve thought_signature
# through the OpenAI-compatible streaming pipeline.
#
# Vertex AI Gemini 3 models with "thinking" enabled return a thought_signature
# in tool call responses via extra_content.google.thought_signature. This must
# be echoed back in subsequent requests or the API rejects the request with:
#
#   "function call is missing a thought_signature"
#
# The native Gemini provider handles this correctly, but the OpenAI provider
# (used for OpenAI-compatible proxies) drops thought_signature in both
# parse_tool_calls and format_tool_calls. The rest of the pipeline
# (StreamAccumulator, ToolCall) already supports thought_signature.
#
# This patch:
# - Extracts thought_signature from extra_content during tool call parsing
# - Echoes thought_signature back in extra_content during serialization

module RubyLLM
  module Providers
    class OpenAI
      module Tools
        # rubocop:disable Style/ModuleFunction -- required to replace singleton method copy

        module_function

        # Parse tool calls from OpenAI-format response data
        #
        # @param tool_calls [Array<Hash>] Raw tool call data from API response
        # @param parse_arguments [Boolean] Whether to JSON-parse arguments (false during streaming)
        # @return [Hash{String => ToolCall}, nil] Parsed tool calls keyed by ID
        def parse_tool_calls(tool_calls, parse_arguments: true)
          return unless tool_calls&.any?

          tool_calls.to_h do |tc|
            thought_sig = tc.dig("extra_content", "google", "thought_signature")

            [
              tc["id"],
              ToolCall.new(
                id: tc["id"],
                name: tc.dig("function", "name"),
                arguments: if parse_arguments
                             parse_tool_call_arguments(tc)
                           else
                             tc.dig("function", "arguments")
                           end,
                thought_signature: thought_sig,
              ),
            ]
          end
        end

        # Serialize tool calls into OpenAI-format request data
        #
        # @param tool_calls [Hash{String => ToolCall}] Tool calls to serialize
        # @return [Array<Hash>, nil] Serialized tool calls for API request
        def format_tool_calls(tool_calls)
          return unless tool_calls&.any?

          tool_calls.map do |_, tc|
            entry = {
              id: tc.id,
              type: "function",
              function: {
                name: tc.name,
                arguments: JSON.generate(tc.arguments),
              },
            }

            if tc.thought_signature
              entry[:extra_content] = { google: { thought_signature: tc.thought_signature } }
            end

            entry
          end
        end

        # Parse tool call arguments from raw hash
        #
        # @param tool_call [Hash] Raw tool call hash
        # @return [Hash] Parsed arguments
        def parse_tool_call_arguments(tool_call)
          arguments = tool_call.dig("function", "arguments")

          if arguments.nil? || arguments.empty?
            {}
          else
            JSON.parse(arguments)
          end
        end
        # rubocop:enable Style/ModuleFunction
      end
    end
  end
end
