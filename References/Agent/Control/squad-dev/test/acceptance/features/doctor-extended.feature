Feature: Doctor diagnostic extended

  Scenario: Doctor shows diagnostic header
    Given the current directory has a ".squad" directory
    When I run "squad doctor"
    Then the output contains "Squad Doctor"
    And the exit code is 0

  Scenario: Doctor shows summary with pass count
    Given the current directory has a ".squad" directory
    When I run "squad doctor"
    Then the output contains "Summary:"
    And the output matches pattern "\d+ passed"
    And the exit code is 0
