use anyhow::Result;

use crate::generator::research::memory::MemoryScope;
use crate::generator::research::types::{AgentType, DomainModulesReport};
use crate::generator::{
    context::GeneratorContext,
    step_forward_agent::{
        AgentDataConfig, DataSource, FormatterConfig, LLMCallMode, PromptTemplate, StepForwardAgent,
    },
};

/// Domain Division and Top-Level Abstract Module Researcher - Identifies high-level system domain architecture and abstract modules, as well as their internal relationships.
#[derive(Default)]
pub struct DomainModulesDetector;

impl StepForwardAgent for DomainModulesDetector {
    type Output = DomainModulesReport;

    fn agent_type(&self) -> String {
        AgentType::DomainModulesDetector.to_string()
    }

    fn agent_type_enum(&self) -> Option<AgentType> {
        Some(AgentType::DomainModulesDetector)
    }

    fn memory_scope_key(&self) -> String {
        MemoryScope::STUDIES_RESEARCH.to_string()
    }

    fn data_config(&self) -> AgentDataConfig {
        AgentDataConfig {
            required_sources: vec![
                DataSource::ResearchResult(AgentType::SystemContextResearcher.to_string()),
                DataSource::DEPENDENCY_ANALYSIS,
                DataSource::CODE_INSIGHTS,
            ],
            optional_sources: vec![
                DataSource::PROJECT_STRUCTURE,
                // Use architecture and database docs for domain analysis
                DataSource::knowledge_categories(vec!["architecture", "database"]),
            ],
        }
    }

    fn prompt_template(&self) -> PromptTemplate {
        PromptTemplate {
            system_prompt: r#"You are a professional software architecture analyst, specializing in identifying domain architecture and modules in projects based on the provided information and research materials.

You may have access to existing product description, requirements and architecture documentation from external sources.
If available:
- Use established business domain terminology and glossaries
- Align module identification with documented domain boundaries
- Reference domain-driven design (DDD) concepts from the documentation
- Validate code organization against documented bounded contexts
- Ensure consistency between business language and code structure

You MUST output strict JSON only (no markdown, no code fences, no prose outside JSON).
Return all required fields exactly with this structure:
{
  "domain_modules": [
    {
      "name": "string",
      "description": "string",
      "domain_type": "string",
      "sub_modules": [
        {
          "name": "string",
          "description": "string",
          "code_paths": ["string"],
          "key_functions": ["string"],
          "importance": 1.0
        }
      ],
      "code_paths": ["string"],
      "importance": 1.0,
      "complexity": 1.0
    }
  ],
  "domain_relations": [
    {
      "from_domain": "string",
      "to_domain": "string",
      "relation_type": "string",
      "strength": 1.0,
      "description": "string"
    }
  ],
  "business_flows": [
    {
      "name": "string",
      "description": "string",
      "steps": [
        {
          "step": 1,
          "domain_module": "string",
          "sub_module": "string or null",
          "operation": "string",
          "code_entry_point": "string or null"
        }
      ],
      "entry_point": "string",
      "importance": 1.0,
      "involved_domains_count": 1
    }
  ],
  "architecture_summary": "string",
  "confidence_score": 0.0
}

Rules:
- Always include all top-level keys.
- Every element in business_flows.steps must be an object, never a plain string.
- Fill unknown values with empty string, empty arrays, or null as appropriate.
- confidence_score must be numeric (0.0-10.0)."#
                .to_string(),

            opening_instruction: "Based on the following research materials, conduct a high-level architecture analysis:".to_string(),

            closing_instruction: r#"
## Analysis Requirements:
- Use a top-down analysis approach, domains first then modules
- Domain division should reflect functional value, not technical implementation
- Maintain a reasonable level of abstraction, avoid excessive detail
- Focus on core business logic and key dependency relationships
- If external documentation is provided, use consistent domain terminology
- Identify any misalignment between documented domains and code structure"#
                .to_string(),

            llm_call_mode: LLMCallMode::Extract,
            formatter_config: FormatterConfig {
                only_directories_when_files_more_than: Some(500),
                ..FormatterConfig::default()
            },
        }
    }

    /// Post-processing - Store analysis results to memory
    fn post_process(
        &self,
        result: &DomainModulesReport,
        _context: &GeneratorContext,
    ) -> Result<()> {
        // Simplified storage logic
        println!("✅ Domain architecture analysis completed:");
        println!(
            "   - Identified domain modules: {}",
            result.domain_modules.len()
        );

        let total_sub_modules: usize = result
            .domain_modules
            .iter()
            .map(|d| d.sub_modules.len())
            .sum();
        println!("   - Total sub-modules: {}", total_sub_modules);
        println!("   - Domain relations: {}", result.domain_relations.len());
        println!("   - Business flows: {}", result.business_flows.len());
        println!("   - Confidence score: {:.1}/10", result.confidence_score);

        Ok(())
    }
}
