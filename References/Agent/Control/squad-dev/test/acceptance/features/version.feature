Feature: Version display

  Scenario: Show version with --version flag
    When I run "squad --version"
    Then the output matches pattern "\d+\.\d+\.\d+"
    And the exit code is 0
