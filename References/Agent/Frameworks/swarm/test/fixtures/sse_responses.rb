# frozen_string_literal: true

require "securerandom"

module Fixtures
  # SSE (Server-Sent Events) streaming response fixtures for testing
  #
  # Provides realistic SSE streams for OpenAI and Anthropic providers
  # to test streaming LLM responses with WebMock.
  module SSEResponses
    class << self
      # OpenAI-style SSE streaming response
      #
      # Format: data: {json}\n\ndata: {json}\n\ndata: [DONE]\n\n
      #
      # @param chunks [Array<Hash>] Array of chunk data
      #   Each chunk can have: content, tool_calls (partial), model, finish_reason
      # @param model [String] Model ID (default: "gpt-4")
      # @return [String] Complete SSE stream
      #
      # @example Simple content streaming
      #   SSEResponses.openai_stream([
      #     { content: "Hello" },
      #     { content: " world" },
      #     { content: "!" }
      #   ])
      #
      # @example Tool call streaming
      #   SSEResponses.openai_stream([
      #     { content: "I'll read" },
      #     { tool_calls: [{ id: "call_123", function: { name: "Read", arguments: "{\"file" }}] },
      #     { tool_calls: [{ id: "call_123", function: { arguments: "_path\":\"test\"}" }}] }
      #   ])
      def openai_stream(chunks, model: "gpt-4", id: nil)
        id ||= "chatcmpl-#{SecureRandom.hex(12)}"
        created = Time.now.to_i

        # Build SSE stream
        sse_lines = chunks.map.with_index do |chunk_data, index|
          delta = {}
          delta["content"] = chunk_data[:content] if chunk_data[:content]

          if chunk_data[:tool_calls]
            delta["tool_calls"] = chunk_data[:tool_calls].map do |tc|
              {
                index: tc[:index] || 0,
                id: tc[:id],
                type: "function",
                function: {
                  name: tc[:function]&.dig(:name),
                  arguments: tc[:function]&.dig(:arguments),
                }.compact,
              }.compact
            end
          end

          chunk = {
            id: id,
            object: "chat.completion.chunk",
            created: created,
            model: chunk_data[:model] || model,
            choices: [
              {
                index: 0,
                delta: delta,
                finish_reason: chunk_data[:finish_reason],
              }.compact,
            ],
          }

          # Add usage to last chunk
          if index == chunks.size - 1
            chunk[:usage] = {
              prompt_tokens: chunk_data.dig(:usage, :prompt_tokens) || 10,
              completion_tokens: chunk_data.dig(:usage, :completion_tokens) || 20,
              total_tokens: chunk_data.dig(:usage, :total_tokens) || 30,
            }
          end

          "data: #{chunk.to_json}\n\n"
        end

        # Add [DONE] terminator
        sse_lines << "data: [DONE]\n\n"

        sse_lines.join
      end

      # Anthropic-style SSE streaming response
      #
      # Format similar to OpenAI but with Anthropic-specific fields
      #
      # @param chunks [Array<Hash>] Array of chunk data
      # @param model [String] Model ID (default: "claude-sonnet-4")
      # @return [String] Complete SSE stream
      #
      # @example
      #   SSEResponses.anthropic_stream([
      #     { type: "content_block_delta", delta: { text: "Hello" } },
      #     { type: "content_block_delta", delta: { text: " world" } }
      #   ])
      def anthropic_stream(chunks, model: "claude-sonnet-4", id: nil)
        sse_lines = chunks.map.with_index do |chunk_data, index|
          # Anthropic has different event types
          event_type = chunk_data[:type] || "content_block_delta"

          chunk = {
            type: event_type,
            index: chunk_data[:index] || 0,
          }

          # Add delta for content_block_delta events
          if event_type == "content_block_delta" && chunk_data[:delta]
            chunk[:delta] = chunk_data[:delta]
          end

          # Add content_block for content_block_start events
          if event_type == "content_block_start" && chunk_data[:content_block]
            chunk[:content_block] = chunk_data[:content_block]
          end

          # Add usage to last chunk (message_delta event)
          if index == chunks.size - 1
            chunk = {
              type: "message_delta",
              delta: { stop_reason: chunk_data[:stop_reason] || "end_turn" },
              usage: {
                output_tokens: chunk_data.dig(:usage, :output_tokens) || 20,
              },
            }
          end

          "data: #{chunk.to_json}\n\n"
        end

        # Anthropic uses message_stop instead of [DONE]
        sse_lines << "data: #{({ type: "message_stop" }).to_json}\n\n"

        sse_lines.join
      end

      # Simple content-only streaming (provider-agnostic)
      #
      # Creates a simple SSE stream with just content chunks
      #
      # @param content_chunks [Array<String>] Array of content strings
      # @param model [String] Model ID
      # @return [String] SSE stream
      #
      # @example
      #   SSEResponses.simple_content_stream(["Hello", " ", "world", "!"])
      def simple_content_stream(content_chunks, model: "gpt-4")
        openai_stream(
          content_chunks.map { |content| { content: content } },
          model: model,
        )
      end

      # Tool call streaming (OpenAI format)
      #
      # Simulates tool call streaming with partial JSON arguments
      #
      # @param tool_name [String] Tool name
      # @param arguments_fragments [Array<String>] JSON fragments that build up to complete args
      # @param id [String] Tool call ID
      # @return [String] SSE stream
      #
      # @example
      #   SSEResponses.tool_call_stream(
      #     "Read",
      #     ["{\"file", "_path\":\"", "/test.rb", "\"}"],
      #     id: "call_123"
      #   )
      def tool_call_stream(tool_name, arguments_fragments, id: nil, model: "gpt-4")
        id ||= "call_#{SecureRandom.hex(12)}"

        chunks = []

        # First chunk: tool call start with name
        chunks << {
          tool_calls: [{
            id: id,
            index: 0,
            function: { name: tool_name, arguments: "" },
          }],
        }

        # Subsequent chunks: argument fragments
        arguments_fragments.each do |fragment|
          chunks << {
            tool_calls: [{
              id: id,
              index: 0,
              function: { arguments: fragment },
            }],
          }
        end

        # Final chunk with finish_reason
        chunks.last[:finish_reason] = "tool_calls"

        openai_stream(chunks, model: model)
      end

      # Mixed content and tool call streaming
      #
      # Simulates: content chunks → tool call chunks
      #
      # @param content_text [String] Content before tool call
      # @param tool_name [String] Tool name
      # @param tool_arguments [Hash] Complete tool arguments
      # @return [String] SSE stream
      #
      # @example
      #   SSEResponses.content_then_tool_stream(
      #     "Let me read that file",
      #     "Read",
      #     { file_path: "/test.rb" }
      #   )
      def content_then_tool_stream(content_text, tool_name, tool_arguments, model: "gpt-4")
        chunks = []

        # Split content into words for realistic chunking
        content_text.split.each do |word|
          chunks << { content: "#{word} " }
        end

        # Tool call chunks
        tool_id = "call_#{SecureRandom.hex(12)}"
        args_json = tool_arguments.to_json

        # First tool chunk with name
        chunks << {
          content: nil,
          tool_calls: [{
            id: tool_id,
            index: 0,
            function: { name: tool_name, arguments: "" },
          }],
        }

        # Split arguments into fragments
        fragment_size = [args_json.length / 3, 1].max
        args_json.scan(/.{1,#{fragment_size}}/m).each do |fragment|
          chunks << {
            tool_calls: [{
              id: tool_id,
              index: 0,
              function: { arguments: fragment },
            }],
          }
        end

        chunks.last[:finish_reason] = "tool_calls"

        openai_stream(chunks, model: model)
      end
    end
  end
end
