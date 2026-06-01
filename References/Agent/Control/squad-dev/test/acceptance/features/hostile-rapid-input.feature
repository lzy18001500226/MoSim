Feature: Hostile — Rapid consecutive commands

  Scenario: Multiple version checks in rapid succession
    When I run 5 rapid "squad --version" commands
    Then all commands complete without crash
    And all exit codes are 0

  Scenario: Alternating valid and invalid commands rapidly
    When I run rapid alternating valid and invalid commands
    Then all commands complete without crash

  Scenario: Concurrent help and version commands
    When I run "squad --version" and "squad --help" concurrently
    Then all commands complete without crash
    And all exit codes are 0
