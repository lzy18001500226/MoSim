Feature: Hostile — Invalid input handling

  Scenario: Empty string argument shows help and exits cleanly
    When I run hostile command with empty argument
    Then the process does not crash
    And the exit code is 0

  Scenario: Command with control characters
    When I run hostile command with control characters
    Then the process does not crash
    And the exit code is not null

  Scenario: Extremely long argument (10KB+)
    When I run hostile command with a 10KB argument
    Then the process does not crash
    And the exit code is not null

  Scenario: Command with null bytes is rejected by Node runtime
    When I run hostile command with null bytes
    Then the null byte error is caught gracefully

  Scenario: Command with only whitespace shows help and exits cleanly
    When I run hostile command with whitespace-only argument
    Then the process does not crash
    And the exit code is 0
