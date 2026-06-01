# frozen_string_literal: true

require "simplecov"
SimpleCov.external_at_exit = true
SimpleCov.start do
  enable_coverage :branch
  add_filter "/test/"
  add_filter "/vendor/"
  add_filter "/version.rb"
  add_group "Library", "lib"
  track_files "{lib}/**/*.rb"
end

$LOAD_PATH.unshift(File.expand_path("../lib", __dir__))

require "claude_swarm"
require "swarm_sdk"
require "swarm_memory"
require "minitest/autorun"

# WebMock for mocking HTTP requests in tests
require "webmock/minitest"

require_relative "fixtures/swarm_configs"
require_relative "fixtures/sse_responses"
require_relative "helpers/test_helpers"
require_relative "helpers/llm_mock_helper"

# Configure WebMock to block all external HTTP requests except localhost
WebMock.disable_net_connect!(allow_localhost: true)

# Disable streaming by default in tests (WebMock doesn't support SSE)
# Tests can explicitly enable streaming: true if they want to test streaming behavior
SwarmSDK.configure do |config|
  config.streaming = false
end

# Include LLM mocking helpers in all tests
module Minitest
  class Test
    include LLMMockHelper

    # Ensure streaming is disabled for all tests after each test's setup runs
    # This is important because some tests call SwarmSDK.reset_config! in their setup
    # which would otherwise reset streaming back to true (the production default)
    #
    # NOTE: This runs AFTER each individual test's setup method
    def after_setup
      super
      # Disable streaming for tests (WebMock doesn't support SSE)
      SwarmSDK.config.streaming = false
    end
  end
end

# Set up a temporary home directory for all tests
require "tmpdir"
test_swarm_home = Dir.mktmpdir("claude-swarm-test")
original_home_dir = ENV["CLAUDE_SWARM_HOME"]
ENV["CLAUDE_SWARM_HOME"] = test_swarm_home

# Clean up the test home directory after all tests
Minitest.after_run do
  FileUtils.rm_rf(test_swarm_home)
  ENV["CLAUDE_SWARM_HOME"] = original_home_dir
end
