//! Context assembly: prompt + identity + memories + status.

use crate::agent::status::StatusBlock;
use crate::error::Result;
use crate::memory::MemoryStore;

/// Assembled context ready for injection into LLM.
#[derive(Debug, Clone)]
pub struct AssembledContext {
    /// Full system prompt with identity, memories, and status.
    pub system_prompt: String,
    /// Recent conversation history as formatted text.
    pub conversation_history: String,
}

/// Build context for a channel.
pub async fn build_channel_context(
    base_prompt: &str,
    memory_store: &MemoryStore,
    status_block: &StatusBlock,
    _conversation_id: &str,
) -> Result<String> {
    let mut context = String::new();

    // Base channel prompt
    context.push_str(base_prompt);
    context.push_str("\n\n");

    // Add status block
    let status = status_block.render();
    if !status.is_empty() {
        context.push_str("## Current Status\n\n");
        context.push_str(&status);
        context.push('\n');
    }

    // Add identity memories (always included)
    let identity_memories = memory_store
        .get_by_type(crate::memory::types::MemoryType::Identity, 10)
        .await?;

    if !identity_memories.is_empty() {
        context.push_str("## Identity\n\n");
        for memory in identity_memories {
            context.push_str(&format!("- {}\n", memory.content));
        }
        context.push('\n');
    }

    // Add high-importance memories
    let important_memories = memory_store.get_high_importance(0.8, 5).await?;
    let non_identity: Vec<_> = important_memories
        .into_iter()
        .filter(|m| m.memory_type != crate::memory::types::MemoryType::Identity)
        .collect();

    if !non_identity.is_empty() {
        context.push_str("## Key Context\n\n");
        for memory in non_identity {
            context.push_str(&format!(
                "- [{}] {}\n",
                memory.memory_type,
                memory.content.lines().next().unwrap_or(&memory.content)
            ));
        }
        context.push('\n');
    }

    Ok(context)
}

/// Build minimal context for a branch.
pub async fn build_branch_context(base_prompt: &str) -> Result<String> {
    // Branches get a simpler context - just their base prompt
    // They can recall memories as needed
    Ok(base_prompt.to_string())
}

/// Build context for a worker.
pub fn build_worker_context(base_prompt: &str, task: &str) -> String {
    format!("{}\n\n## Your Task\n\n{}", base_prompt, task)
}
