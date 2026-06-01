Feature: Doctor diagnostic

  Scenario: Run doctor in project with squad setup
    Given the current directory has a ".squad" directory
    When I run "squad doctor"
    Then the exit code is 0
