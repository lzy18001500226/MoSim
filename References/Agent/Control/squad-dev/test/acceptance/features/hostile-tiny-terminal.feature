Feature: Hostile — Tiny terminal (40x10)

  Scenario: Version command works at 40x10
    Given a terminal size of 40 columns by 10 rows
    When I run "squad --version" with that terminal size
    Then the output matches pattern "\d+\.\d+\.\d+"
    And the exit code is 0

  Scenario: Help command works at 40x10
    Given a terminal size of 40 columns by 10 rows
    When I run "squad --help" with that terminal size
    Then the output contains "Usage"
    And the exit code is 0

  Scenario: Status command works at 40x10
    Given a terminal size of 40 columns by 10 rows
    When I run "squad status" with that terminal size
    Then the output contains "Squad Status"
    And the exit code is 0

  Scenario: Doctor command works at 40x10
    Given a terminal size of 40 columns by 10 rows
    When I run "squad doctor" with that terminal size
    Then the exit code is 0

  Scenario: Unknown command at 40x10 still shows error
    Given a terminal size of 40 columns by 10 rows
    When I run "squad nonexistent" with that terminal size
    Then the output contains "Unknown command"
    And the exit code is 1
