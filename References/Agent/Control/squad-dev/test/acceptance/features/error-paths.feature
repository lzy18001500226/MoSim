Feature: Error paths

  Scenario: Unknown command with special characters
    When I run "squad @invalid!cmd"
    Then the output contains "Unknown command"
    And the exit code is 1

  Scenario: Invalid flag is treated as unknown command
    When I run "squad --nonexistent-flag"
    Then the output contains "Unknown command"
    And the exit code is 1

  Scenario: Unknown command suggests help
    When I run "squad foobar"
    Then the output contains "squad help"
    And the exit code is 1
