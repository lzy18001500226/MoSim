Feature: Hostile — Corrupt configuration files

  Scenario: .squad/ directory exists but is empty
    Given a temp directory with an empty ".squad" directory
    When I run "squad status" in the temp directory
    Then the process does not crash
    And the exit code is not null

  Scenario: .squad/team.md is an empty file
    Given a temp directory with an empty ".squad/team.md"
    When I run "squad status" in the temp directory
    Then the process does not crash
    And the exit code is not null

  Scenario: .squad/team.md contains invalid content
    Given a temp directory with ".squad/team.md" containing "{{{{INVALID JSON NOT MARKDOWN}}}}"
    When I run "squad status" in the temp directory
    Then the process does not crash
    And the exit code is not null

  Scenario: .squad/ is a file instead of directory
    Given a temp directory where ".squad" is a regular file
    When I run "squad status" in the temp directory
    Then the process does not crash
    And the exit code is not null

  Scenario: Doctor handles corrupt .squad/ gracefully
    Given a temp directory with an empty ".squad" directory
    When I run "squad doctor" in the temp directory
    Then the process does not crash
    And the exit code is not null
