//! Prompt hooks for observing and controlling agent behavior.

pub mod cortex;
pub mod loop_guard;
pub mod spacebot;

pub use cortex::CortexHook;
pub use loop_guard::{LoopGuard, LoopGuardConfig, LoopGuardVerdict};
pub use spacebot::{SpacebotHook, ToolNudgePolicy};
