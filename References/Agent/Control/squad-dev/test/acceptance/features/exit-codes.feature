Feature: Exit codes

  Scenario: Version command exits with code 0
    When I run "squad --version"
    Then the exit code is 0

  Scenario: Help command exits with code 0
    When I run "squad help"
    Then the exit code is 0

  Scenario: Unknown command exits with non-zero code
    When I run "squad nonexistent-cmd"
    Then the exit code is 1
