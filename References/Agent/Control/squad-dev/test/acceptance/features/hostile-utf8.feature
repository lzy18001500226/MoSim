Feature: Hostile — UTF-8 edge cases

  Scenario: Emoji in command argument does not crash
    When I run hostile command with emoji argument
    Then the process does not crash
    And the exit code is not null

  Scenario: CJK characters in argument
    When I run hostile command with CJK argument
    Then the process does not crash
    And the exit code is not null

  Scenario: RTL text in argument
    When I run hostile command with RTL argument
    Then the process does not crash
    And the exit code is not null

  Scenario: Zero-width characters in argument
    When I run hostile command with zero-width characters
    Then the process does not crash
    And the exit code is not null

  Scenario: Mixed scripts in argument
    When I run hostile command with mixed unicode scripts
    Then the process does not crash
    And the exit code is not null
