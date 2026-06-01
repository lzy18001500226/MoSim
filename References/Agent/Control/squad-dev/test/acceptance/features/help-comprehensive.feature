Feature: Help comprehensive

  Scenario: Help lists all core commands
    When I run "squad help"
    Then the output contains "Usage:"
    And the output contains "Commands:"
    And the output contains "init"
    And the output contains "upgrade"
    And the output contains "status"
    And the output contains "doctor"
    And the exit code is 0

  Scenario: Help includes flags section
    When I run "squad help"
    Then the output contains "Flags"
    And the output contains "--version"
    And the output contains "--help"
    And the exit code is 0
