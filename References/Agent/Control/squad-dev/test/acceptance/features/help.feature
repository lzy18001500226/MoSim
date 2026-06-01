Feature: Help screen

  Scenario: Show help with --help flag
    When I run "squad --help"
    Then the output contains "Usage:"
    And the output contains "Commands:"
    And the output contains "init"
    And the exit code is 0

  Scenario: Show help with help command
    When I run "squad help"
    Then the output contains "Usage:"
    And the exit code is 0
