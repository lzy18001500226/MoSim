# frozen_string_literal: true

# Test swarm for composable swarms feature
SwarmSDK.build do
  id "code_review_team"
  name "Code Review Team"
  lead :lead_reviewer

  agent :lead_reviewer do
    model "gpt-4o-mini"
    description "Lead code reviewer"
    system "You are a lead code reviewer. When asked to review code, respond with: 'Code review complete. Found 0 issues.'"
    tools :Think
  end
end
