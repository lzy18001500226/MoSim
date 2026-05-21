# Domain-Specific Agent Design

Special design considerations for domain-specific agents — each vertical has unique requirements, constraints, and best practices.

---

## The Necessity of Domain Specialization

```
Generic Agent PRD ──► Provides framework and general patterns
       +
Domain Guide   ──► Domain-specific requirements, constraints, best practices
       =
Complete Agent PRD
```

---

## 1. Code Agent (Coding Assistant)

### Domain Characteristics

| Characteristic | Description |
|------|------|
| **High precision** | Code must be correct; a single character can break it |
| **Security sensitive** | Code execution can pose security risks |
| **Context intensive** | Must understand the entire codebase |
| **Multi-language** | Syntax and best practices across programming languages |

### Special Capability Requirements

```yaml
coding_agent:
  
  skills:
    - code_generation
    - code_explanation
    - bug_fixing
    - code_review
    - refactoring
    - test_generation
    - documentation
    
  tools:
    - file_read
    - file_write
    - code_execution  # Requires sandbox
    - lsp_integration  # Language server
    - git_operations
    - package_manager
    - debugger
    
  context:
    - current_file
    - related_files
    - project_structure
    - dependencies
    - coding_standards
    - git_history
```

### Special Security Considerations

```yaml
coding_security:
  
  code_execution:
    sandbox: required
    sandbox_type: [docker, firecracker, wasm]
    network: disabled_by_default
    file_access: workspace_only
    timeout: 30s
    resource_limits:
      memory: 512MB
      cpu: 1 core
      
  file_operations:
    allowed_paths: [workspace]
    denied_paths: [/etc, /root, ~/.ssh]
    confirmation_required: [delete, overwrite_system]
    
  dangerous_operations:
    require_confirmation:
      - rm -rf
      - format
      - drop database
      - system modifications
```

### Specialized Evaluation Metrics

| Metric | Definition | Target |
|------|------|------|
| Code correctness | Generated code runs/passes tests | >90% |
| First-pass success | Usable without modification | >70% |
| Security | No security vulnerabilities introduced | 100% |
| Code quality | Adheres to best practices | >85% |

---

## 2. Customer Support Agent

### Domain Characteristics

| Characteristic | Description |
|------|------|
| **Emotion sensitive** | Users may be frustrated or angry |
| **Compliance required** | Must follow company policies |
| **Escalation path** | Knows when to transfer to human |
| **Multi-turn dialog** | Complex issues require multiple turns |

### Special Capability Requirements

```yaml
support_agent:
  
  skills:
    - intent_classification
    - sentiment_detection
    - issue_diagnosis
    - solution_recommendation
    - escalation_decision
    - satisfaction_recovery  # Win back dissatisfied users
    
  tools:
    - knowledge_base_search
    - order_lookup
    - account_info
    - ticket_creation
    - refund_processing
    - human_handoff
    
  context:
    - customer_profile
    - order_history
    - previous_interactions
    - current_sentiment
    - company_policies
```

### Emotion Handling Specification

```yaml
emotional_handling:
  
  sentiment_detection:
    categories: [positive, neutral, frustrated, angry, confused]
    
  response_adaptation:
    frustrated:
      - acknowledge_frustration
      - apologize_first
      - then_solve
      - offer_compensation_if_applicable
      
    angry:
      - stay_calm
      - validate_feelings
      - focus_on_solution
      - consider_early_escalation
      
  de_escalation_phrases:
    - "I completely understand your frustration"
    - "I'm sorry this happened"
    - "Let me make this right for you"
    
  forbidden_phrases:
    - "Calm down"
    - "That's not our fault"
    - "You should have..."
```

### Escalation Strategy

```yaml
escalation:
  
  triggers:
    automatic:
      - sentiment: angry for 3+ turns
      - request: "speak to human/manager"
      - issue_type: legal_threat
      - complexity: beyond_agent_capability
      
    criteria:
      - failed_resolution_attempts: 2
      - customer_tier: vip
      - monetary_value: >$500
      
  handoff:
    preserve_context: true
    notify_customer: true
    message: "I'm connecting you with a specialist who can better help..."
    warmth_transfer: true  # Agent briefs human first
```

### Specialized Evaluation Metrics

| Metric | Definition | Target |
|------|------|------|
| First-contact resolution | Resolved in one interaction | >70% |
| CSAT | Customer satisfaction | >4.2/5 |
| Sentiment conversion | Negative→Positive | >50% |
| Escalation rate | Transferred to human | <15% |
| Response time | First response | <30s |

---

## 3. Data Analysis Agent (Data Analyst)

### Domain Characteristics

| Characteristic | Description |
|------|------|
| **Data sensitive** | May access sensitive business data |
| **Accuracy critical** | Wrong analysis may lead to wrong decisions |
| **Explainability** | Must explain analysis process and conclusions |
| **Visualization** | Results need visual presentation |

### Special Capability Requirements

```yaml
analyst_agent:
  
  skills:
    - data_exploration
    - statistical_analysis
    - trend_identification
    - anomaly_detection
    - insight_generation
    - visualization_creation
    - report_generation
    
  tools:
    - sql_query
    - python_execution  # pandas, numpy, etc.
    - visualization_tools  # matplotlib, plotly
    - data_export
    - dashboard_creation
    
  context:
    - data_schema
    - business_context
    - historical_analyses
    - metric_definitions
```

### Data Security Specification

```yaml
data_security:
  
  access_control:
    role_based: true
    row_level_security: true
    column_masking:
      pii_columns: masked
      salary_columns: role_restricted
      
  query_restrictions:
    max_rows_returned: 10000
    timeout_seconds: 60
    no_data_export_without_approval: true
    
  audit:
    log_all_queries: true
    log_data_access: true
    alert_on_bulk_access: true
```

### Analysis Quality Assurance

```yaml
analysis_quality:
  
  verification:
    - check_sample_size
    - validate_assumptions
    - cross_reference_sources
    - sanity_check_results
    
  uncertainty_communication:
    - confidence_intervals
    - data_limitations
    - assumption_disclosure
    
  reproducibility:
    - save_queries
    - document_methodology
    - version_data_snapshots
```

---

## 4. Writing Agent (Content Writer)

### Domain Characteristics

| Characteristic | Description |
|------|------|
| **Creativity** | Requires originality and creative thinking |
| **Brand consistency** | Must align with brand voice |
| **Multi-format** | Blog, social media, email, and other formats |
| **SEO considerations** | May require SEO optimization |

### Special Capability Requirements

```yaml
writer_agent:
  
  skills:
    - content_ideation
    - outline_creation
    - draft_writing
    - editing_revision
    - tone_adaptation
    - format_conversion
    - seo_optimization
    
  tools:
    - research_tool
    - plagiarism_checker
    - grammar_checker
    - seo_analyzer
    - image_suggestion
    
  context:
    - brand_guidelines
    - target_audience
    - content_calendar
    - previous_content
    - competitor_content
```

### Brand Consistency

```yaml
brand_consistency:
  
  voice_guidelines:
    tone: [professional, friendly, authoritative]
    personality: [innovative, trustworthy, approachable]
    
  dos:
    - use_active_voice
    - be_concise
    - include_examples
    - end_with_cta
    
  donts:
    - avoid_jargon_without_explanation
    - no_negative_competitor_mentions
    - no_unverified_claims
    
  terminology:
    preferred:
      - "customers" not "users"
      - "solution" not "product"
    forbidden:
      - [list of forbidden terms]
```

### Content Compliance

```yaml
content_compliance:
  
  legal:
    - no_unsubstantiated_claims
    - required_disclaimers: [financial, health, legal]
    - copyright_respect
    
  fact_checking:
    - verify_statistics
    - cite_sources
    - date_check_information
    
  originality:
    - plagiarism_threshold: <10%
    - citation_required_for_quotes
```

---

## 5. Sales Agent (Sales Assistant)

### Domain Characteristics

| Characteristic | Description |
|------|------|
| **Goal-oriented** | Drive sales conversion |
| **Compliance required** | Cannot mislead or exaggerate |
| **CRM integration** | Deep integration with sales systems |
| **Relationship building** | Needs to establish trust |

### Special Capability Requirements

```yaml
sales_agent:
  
  skills:
    - lead_qualification
    - needs_discovery
    - product_matching
    - objection_handling
    - pricing_discussion
    - follow_up_scheduling
    
  tools:
    - crm_integration
    - product_catalog
    - pricing_calculator
    - calendar_scheduling
    - proposal_generator
    - competitor_comparison
    
  context:
    - lead_profile
    - interaction_history
    - company_info
    - buying_signals
    - budget_indicators
```

### Compliance and Ethics

```yaml
sales_ethics:
  
  prohibited:
    - false_claims
    - pressure_tactics
    - competitor_disparagement
    - undisclosed_terms
    - bait_and_switch
    
  required_disclosures:
    - pricing_complete
    - contract_terms
    - refund_policy
    
  consent:
    - permission_to_follow_up
    - data_usage_disclosure
```

---

## 6. Healthcare Agent

### Domain Characteristics

| Characteristic | Description |
|------|------|
| **High risk** | Wrong information could endanger lives |
| **Strict compliance** | HIPAA and other regulations |
| **Disclaimer required** | Must include appropriate disclaimers |
| **Human review** | Critical recommendations need human confirmation |

### Special Restrictions

```yaml
healthcare_constraints:
  
  absolute_restrictions:
    - no_diagnosis
    - no_prescription
    - no_treatment_decisions
    - no_emergency_handling  # Should direct to call emergency services
    
  required_disclaimers:
    every_response: "This is not medical advice. Please consult a healthcare provider."
    
  escalation:
    immediate:
      - mentions_of_self_harm
      - emergency_symptoms
      - medication_emergencies
    to_professional:
      - specific_diagnosis_questions
      - treatment_recommendations
```

### Data Compliance

```yaml
hipaa_compliance:
  
  data_handling:
    - no_phi_storage
    - no_phi_in_logs
    - encrypted_transmission
    
  minimum_necessary:
    - only_collect_required_info
    - don't_ask_for_unnecessary_details
    
  audit:
    - log_all_access
    - regular_compliance_review
```

---

## Domain Selection Checklist

When designing a domain-specific agent, confirm the following:

```markdown
## Domain Specialization Checklist

### Risk Assessment
- [ ] Domain risk level assessment (High/Medium/Low)
- [ ] Potential consequences of errors
- [ ] Regulatory requirements

### Special Capabilities
- [ ] Domain-specific skill identification
- [ ] Specialized tool requirements
- [ ] Special context requirements

### Compliance Requirements
- [ ] Industry regulations (HIPAA, GDPR, etc.)
- [ ] Company policies
- [ ] Required disclaimers

### Safety Boundaries
- [ ] Absolutely prohibited behaviors
- [ ] Behaviors requiring confirmation
- [ ] Escalation trigger conditions

### Evaluation Metrics
- [ ] Domain-specific quality metrics
- [ ] Safety/compliance metrics
- [ ] User satisfaction metrics
```

---

## Domain Specification Template

```markdown
## Domain Specialization Spec: [Domain Name]

### Domain Characteristics
| Characteristic | Description | Design Impact |
|------|------|----------|
| [characteristic] | [description] | [how to address] |

### Special Capabilities
**Skills:** [list]
**Tools:** [list]  
**Context:** [list]

### Compliance Requirements
| Regulation/Policy | Requirement | Implementation |
|-----------|------|----------|
| [regulation] | [requirement] | [method] |

### Safety Boundaries
**Prohibited:** [list]
**Requires confirmation:** [list]
**Escalation conditions:** [list]

### Domain Metrics
| Metric | Definition | Target |
|------|------|------|
| [metric] | [definition] | [target] |
```
