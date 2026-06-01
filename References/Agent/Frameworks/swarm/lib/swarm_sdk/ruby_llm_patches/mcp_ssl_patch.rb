# frozen_string_literal: true

# Patches ruby_llm-mcp HTTPX connections to configure SSL verification
#
# OpenSSL 3.6 enforces CRL (Certificate Revocation List) checking by default.
# Most certificates don't provide accessible CRL endpoints (industry moved to OCSP),
# which breaks HTTPS MCP connections with:
#   "certificate verify failed (unable to get certificate CRL)"
#
# This patch injects SSL options into all 5 HTTPX connection creation paths:
#
# Via HTTPClient.build_connection (paths 1-3):
#   1. StreamableHTTP#create_connection
#   2. StreamableHTTP#create_connection_with_streaming_callbacks
#   3. SSE#send_request
#
# Direct HTTPX.plugin calls (paths 4-5):
#   4. StreamableHTTP#create_connection_with_sse_callbacks
#   5. SSE#create_sse_client
#
# Default: VERIFY_PEER (validates cert chain without CRL checking)
# Configurable: VERIFY_NONE for local development via SwarmSDK.config.mcp_ssl_verify

require "openssl"

module SwarmSDK
  # Module-level SSL configuration for MCP HTTPX connections
  #
  # Set ssl_options before creating MCP clients. The patched HTTPX methods
  # read from this accessor to configure SSL on every connection.
  #
  # @example Default (validates cert chain, skips CRL)
  #   McpSslPatch.ssl_options #=> { verify_mode: OpenSSL::SSL::VERIFY_PEER }
  #
  # @example Disable SSL verification (local dev only)
  #   McpSslPatch.ssl_options = { verify_mode: OpenSSL::SSL::VERIFY_NONE }
  module McpSslPatch
    @ssl_options = { verify_mode: OpenSSL::SSL::VERIFY_PEER }

    class << self
      # @return [Hash] SSL options hash passed to HTTPX .with(ssl: ...)
      attr_accessor :ssl_options

      # Clear the thread-local HTTPX connection cache
      #
      # Must be called after changing ssl_options so that HTTPClient.build_connection
      # runs again with the updated options.
      #
      # @return [void]
      def reset_connection!
        Thread.current[:ruby_llm_mcp_client_connection] = nil
      end
    end
  end
end

# Patch 1: HTTPClient.build_connection
#
# Covers paths 1-3: StreamableHTTP#create_connection,
# StreamableHTTP#create_connection_with_streaming_callbacks, SSE#send_request
#
# These all chain from HTTPClient.connection which calls build_connection.
module RubyLLM
  module MCP
    module Transports
      module Support
        class HTTPClient
          class << self
            def build_connection
              HTTPX.with(
                pool_options: {
                  max_connections: RubyLLM::MCP.config.max_connections,
                  pool_timeout: RubyLLM::MCP.config.pool_timeout,
                },
                ssl: SwarmSDK::McpSslPatch.ssl_options,
              )
            end
          end
        end
      end
    end
  end
end

# Patch 2: StreamableHTTP#create_connection_with_sse_callbacks
#
# This method calls HTTPX.plugin(:callbacks) directly, bypassing HTTPClient.
# Merges SSL options with ALPN protocol when version is :http1.
module SwarmSDK
  module McpSslPatch
    module StreamableHttpSslPatch
      private

      def create_connection_with_sse_callbacks(options, headers)
        client = HTTPX.plugin(:callbacks)
        client = add_on_response_body_chunk_callback(client, options)

        ssl = SwarmSDK::McpSslPatch.ssl_options.dup
        ssl[:alpn_protocols] = ["http/1.1"] if @version == :http1

        client = client.with(
          timeout: {
            connect_timeout: 10,
            read_timeout: @request_timeout / 1000,
            write_timeout: @request_timeout / 1000,
            operation_timeout: @request_timeout / 1000,
          },
          headers: headers,
          ssl: ssl,
        )

        register_client(client)
      end
    end
  end
end

# Patch 3: SSE#create_sse_client
#
# This method calls HTTPX.plugin(:stream) directly, bypassing HTTPClient.
# Merges SSL options with ALPN protocol when version is :http1.
module SwarmSDK
  module McpSslPatch
    module SseSslPatch
      private

      def create_sse_client
        stream_headers = build_request_headers

        ssl = SwarmSDK::McpSslPatch.ssl_options.dup
        ssl[:alpn_protocols] = ["http/1.1"] if @version == :http1

        HTTPX.plugin(:stream).with(
          headers: stream_headers,
          ssl: ssl,
        )
      end
    end
  end
end

# Apply prepend patches for direct HTTPX.plugin calls
RubyLLM::MCP::Transports::StreamableHTTP.prepend(SwarmSDK::McpSslPatch::StreamableHttpSslPatch)
RubyLLM::MCP::Transports::SSE.prepend(SwarmSDK::McpSslPatch::SseSslPatch)
