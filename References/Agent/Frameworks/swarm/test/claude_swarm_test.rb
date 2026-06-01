# frozen_string_literal: true

require "test_helper"

class ClaudeSwarmTest < Minitest::Test
  def test_that_it_has_a_version_number
    refute_nil(::ClaudeSwarm::VERSION)
  end

  def test_cli_exists
    assert_kind_of(Class, ClaudeSwarm::CLI)
  end
end
