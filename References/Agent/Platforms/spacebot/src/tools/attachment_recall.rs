//! Attachment recall tool for channels. Retrieves saved attachment info
//! and optionally re-loads file content for re-analysis or delegation.

use crate::ChannelId;

use rig::completion::ToolDefinition;
use rig::tool::Tool;
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::path::PathBuf;

/// Maximum file size for `get_content` action (10 MB).
const MAX_CONTENT_SIZE: u64 = 10 * 1024 * 1024;

/// Image MIME types supported for re-loading as base64.
const IMAGE_MIME_PREFIXES: &[&str] = &["image/jpeg", "image/png", "image/gif", "image/webp"];

/// Text-based MIME types supported for inline re-loading.
const TEXT_MIME_PREFIXES: &[&str] = &[
    "text/",
    "application/json",
    "application/xml",
    "application/javascript",
    "application/typescript",
    "application/toml",
    "application/yaml",
];

/// Tool for recalling saved attachments from the channel's history.
///
/// Added per-turn to channels that have `save_attachments` enabled.
/// Provides three actions: list recent attachments, get a file's disk path
/// (for delegation to workers), or re-load file content for analysis.
#[derive(Debug, Clone)]
pub struct AttachmentRecallTool {
    pool: SqlitePool,
    channel_id: ChannelId,
}

impl AttachmentRecallTool {
    pub fn new(pool: SqlitePool, channel_id: ChannelId) -> Self {
        Self { pool, channel_id }
    }
}

/// Error type for attachment recall tool.
#[derive(Debug, thiserror::Error)]
#[error("Attachment recall failed: {0}")]
pub struct AttachmentRecallError(String);

/// Arguments for attachment recall tool.
#[derive(Debug, Deserialize, JsonSchema)]
pub struct AttachmentRecallArgs {
    /// What to do: "list" recent attachments, "get_path" for a specific file's
    /// absolute disk path, or "get_content" to re-load file content for analysis.
    pub action: String,
    /// The attachment ID (from the history annotation). Required for get_path
    /// and get_content.
    #[serde(default)]
    pub attachment_id: Option<String>,
    /// Alternative to attachment_id — look up by original filename. If multiple
    /// matches, returns the most recent.
    #[serde(default)]
    pub filename: Option<String>,
    /// For list action: how many recent attachments to return (default 10).
    #[serde(default = "default_limit")]
    pub limit: i64,
}

fn default_limit() -> i64 {
    10
}

/// Output from attachment recall tool.
///
/// Note: `UserContent` is not serializable, so image content cannot be
/// delivered through the tool's JSON output. Text file content is inlined
/// directly into `summary` so the LLM receives it. For images, the summary
/// confirms the image was loaded; the base64 data would need to be injected
/// into the conversation history through a separate mechanism (future work).
#[derive(Debug, Serialize)]
pub struct AttachmentRecallOutput {
    pub action: String,
    pub attachments: Vec<AttachmentInfo>,
    /// Human-readable summary for the LLM. For text files via `get_content`,
    /// the file content is inlined here.
    pub summary: String,
    /// Whether this was an error result (unknown action, not found, etc.)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

/// Info about a saved attachment.
#[derive(Debug, Clone, Serialize)]
pub struct AttachmentInfo {
    pub id: String,
    pub filename: String,
    pub saved_filename: String,
    pub mime_type: String,
    pub size_bytes: i64,
    /// Absolute disk path. Only populated for `get_path` responses to avoid
    /// leaking filesystem layout in `list` responses.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub disk_path: Option<String>,
    pub created_at: String,
}

impl Tool for AttachmentRecallTool {
    const NAME: &'static str = "attachment_recall";

    type Error = AttachmentRecallError;
    type Args = AttachmentRecallArgs;
    type Output = AttachmentRecallOutput;

    async fn definition(&self, _prompt: String) -> ToolDefinition {
        ToolDefinition {
            name: Self::NAME.to_string(),
            description: crate::prompts::text::get("tools/attachment_recall").to_string(),
            parameters: serde_json::json!({
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "get_path", "get_content"],
                        "description": "What to do: list recent attachments, get the disk path of a specific file, or re-load its content for analysis."
                    },
                    "attachment_id": {
                        "type": "string",
                        "description": "The attachment ID (from history metadata). Required for get_path and get_content."
                    },
                    "filename": {
                        "type": "string",
                        "description": "Alternative to attachment_id — look up by original filename. If multiple matches, returns the most recent."
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "For list action: how many recent attachments to return."
                    }
                },
                "required": ["action"]
            }),
        }
    }

    async fn call(&self, args: Self::Args) -> Result<Self::Output, Self::Error> {
        match args.action.as_str() {
            "list" => self.list_attachments(args.limit.clamp(1, 50)).await,
            "get_path" => {
                self.get_attachment_path(args.attachment_id.as_deref(), args.filename.as_deref())
                    .await
            }
            "get_content" => {
                self.get_attachment_content(args.attachment_id.as_deref(), args.filename.as_deref())
                    .await
            }
            other => Ok(AttachmentRecallOutput {
                action: other.to_string(),
                attachments: vec![],
                summary: format!(
                    "Unknown action: '{other}'. Use 'list', 'get_path', or 'get_content'."
                ),
                error: Some(format!("unknown_action: {other}")),
            }),
        }
    }
}

impl AttachmentRecallTool {
    async fn list_attachments(
        &self,
        limit: i64,
    ) -> Result<AttachmentRecallOutput, AttachmentRecallError> {
        let rows = sqlx::query_as::<_, AttachmentRow>(
            "SELECT id, original_filename, saved_filename, mime_type, size_bytes, disk_path, created_at \
             FROM saved_attachments \
             WHERE channel_id = ? \
             ORDER BY created_at DESC \
             LIMIT ?",
        )
        .bind(self.channel_id.as_ref())
        .bind(limit)
        .fetch_all(&self.pool)
        .await
        .map_err(|error| {
            AttachmentRecallError(format!("Failed to query saved attachments: {error}"))
        })?;

        let attachments: Vec<AttachmentInfo> = rows
            .into_iter()
            .map(|row| AttachmentInfo {
                id: row.id,
                filename: row.original_filename,
                saved_filename: row.saved_filename,
                mime_type: row.mime_type,
                size_bytes: row.size_bytes,
                disk_path: None,
                created_at: row.created_at,
            })
            .collect();

        let summary = if attachments.is_empty() {
            "No saved attachments in this channel.".to_string()
        } else {
            let mut lines = vec![format!(
                "{} saved attachment(s) in this channel:",
                attachments.len()
            )];
            for attachment in &attachments {
                let size_str = format_size(attachment.size_bytes);
                lines.push(format!(
                    "  - {} ({}, {}, id:{})",
                    attachment.filename,
                    attachment.mime_type,
                    size_str,
                    attachment.id.get(..8).unwrap_or(&attachment.id)
                ));
            }
            lines.join("\n")
        };

        Ok(AttachmentRecallOutput {
            action: "list".to_string(),
            attachments,
            summary,
            error: None,
        })
    }

    async fn get_attachment_path(
        &self,
        attachment_id: Option<&str>,
        filename: Option<&str>,
    ) -> Result<AttachmentRecallOutput, AttachmentRecallError> {
        let attachment = self.resolve_attachment(attachment_id, filename).await?;
        let disk_path = attachment.disk_path.clone().unwrap_or_default();

        // Verify the file exists on disk
        let path = PathBuf::from(&disk_path);
        if !path.exists() {
            let summary = format!(
                "File '{}' was saved but is no longer on disk at {}",
                attachment.filename, disk_path
            );
            return Ok(AttachmentRecallOutput {
                action: "get_path".to_string(),
                attachments: vec![attachment],
                summary,
                error: Some("file_missing".to_string()),
            });
        }

        let summary = format!("File '{}' is saved at: {}", attachment.filename, disk_path);

        Ok(AttachmentRecallOutput {
            action: "get_path".to_string(),
            attachments: vec![attachment],
            summary,
            error: None,
        })
    }

    async fn get_attachment_content(
        &self,
        attachment_id: Option<&str>,
        filename: Option<&str>,
    ) -> Result<AttachmentRecallOutput, AttachmentRecallError> {
        let attachment = self.resolve_attachment(attachment_id, filename).await?;
        let disk_path = attachment.disk_path.clone().unwrap_or_default();

        let path = PathBuf::from(&disk_path);
        if !path.exists() {
            let summary = format!(
                "File '{}' was saved but is no longer on disk at {}",
                attachment.filename, disk_path
            );
            return Ok(AttachmentRecallOutput {
                action: "get_content".to_string(),
                attachments: vec![attachment],
                summary,
                error: Some("file_missing".to_string()),
            });
        }

        // Check live file size from disk, not the DB value which may be stale
        let live_size = tokio::fs::metadata(&path)
            .await
            .map(|metadata| metadata.len())
            .unwrap_or(attachment.size_bytes as u64);

        if live_size > MAX_CONTENT_SIZE {
            let size_str = format_size(live_size as i64);
            let summary = format!(
                "File '{}' is too large for inline content ({}, max 10 MB). \
                 Use get_path instead and delegate to a worker.",
                attachment.filename, size_str
            );
            return Ok(AttachmentRecallOutput {
                action: "get_content".to_string(),
                attachments: vec![attachment],
                summary,
                error: Some("file_too_large".to_string()),
            });
        }

        let is_image = IMAGE_MIME_PREFIXES
            .iter()
            .any(|p| attachment.mime_type.starts_with(p));
        let is_text = TEXT_MIME_PREFIXES
            .iter()
            .any(|p| attachment.mime_type.starts_with(p));

        if !is_image && !is_text {
            let summary = format!(
                "File '{}' ({}) cannot be loaded inline — only images and text files \
                 are supported for get_content. Use get_path to get the disk path \
                 and delegate to a worker.\nPath: {}",
                attachment.filename, attachment.mime_type, disk_path
            );
            return Ok(AttachmentRecallOutput {
                action: "get_content".to_string(),
                attachments: vec![attachment],
                summary,
                error: None,
            });
        }

        let bytes: Vec<u8> = tokio::fs::read(&path).await.map_err(|error| {
            AttachmentRecallError(format!(
                "Failed to read file '{}': {error}",
                attachment.filename
            ))
        })?;

        let summary = if is_image {
            // Images can't be delivered through JSON tool output — the LLM
            // would need the image injected into conversation history as
            // UserContent::Image, which requires a separate mechanism.
            // For now, confirm the image exists and suggest using get_path
            // to delegate to a worker for image analysis.
            format!(
                "Image '{}' ({}, {}) exists on disk at: {}\n\
                 Note: Image content cannot be inlined in tool output. \
                 Use get_path and delegate to a worker, or re-send the image in chat.",
                attachment.filename,
                attachment.mime_type,
                format_size(attachment.size_bytes),
                disk_path
            )
        } else {
            // Text file — inline content directly into summary so the LLM
            // receives it through the serialized tool output.
            let text = String::from_utf8_lossy(&bytes);
            let truncated = if text.len() > 50_000 {
                let end = text.floor_char_boundary(50_000);
                format!(
                    "{}...\n[truncated — {} bytes total]",
                    &text[..end],
                    text.len()
                )
            } else {
                text.into_owned()
            };
            format!(
                "<file name=\"{}\" mime=\"{}\">\n{}\n</file>",
                attachment.filename, attachment.mime_type, truncated
            )
        };

        Ok(AttachmentRecallOutput {
            action: "get_content".to_string(),
            attachments: vec![attachment],
            summary,
            error: None,
        })
    }

    /// Resolve an attachment by ID or filename.
    async fn resolve_attachment(
        &self,
        attachment_id: Option<&str>,
        filename: Option<&str>,
    ) -> Result<AttachmentInfo, AttachmentRecallError> {
        let row = if let Some(id) = attachment_id {
            // Look up by exact ID or literal ID prefix (no LIKE wildcards)
            let row = sqlx::query_as::<_, AttachmentRow>(
                "SELECT id, original_filename, saved_filename, mime_type, size_bytes, disk_path, created_at \
                 FROM saved_attachments \
                 WHERE channel_id = ? AND substr(id, 1, length(?)) = ? \
                 ORDER BY created_at DESC \
                 LIMIT 1",
            )
            .bind(self.channel_id.as_ref())
            .bind(id)
            .bind(id)
            .fetch_optional(&self.pool)
            .await
            .map_err(|error| {
                AttachmentRecallError(format!("Failed to look up attachment: {error}"))
            })?;

            match row {
                Some(row) => row,
                None => {
                    return Err(AttachmentRecallError(format!(
                        "not_found: No attachment found with ID '{id}'"
                    )));
                }
            }
        } else if let Some(name) = filename {
            // Look up by original filename, most recent match
            let row = sqlx::query_as::<_, AttachmentRow>(
                "SELECT id, original_filename, saved_filename, mime_type, size_bytes, disk_path, created_at \
                 FROM saved_attachments \
                 WHERE channel_id = ? AND original_filename = ? \
                 ORDER BY created_at DESC \
                 LIMIT 1",
            )
            .bind(self.channel_id.as_ref())
            .bind(name)
            .fetch_optional(&self.pool)
            .await
            .map_err(|error| {
                AttachmentRecallError(format!("Failed to look up attachment: {error}"))
            })?;

            match row {
                Some(row) => row,
                None => {
                    return Err(AttachmentRecallError(format!(
                        "not_found: No attachment found with filename '{name}'"
                    )));
                }
            }
        } else {
            return Err(AttachmentRecallError(
                "missing_args: Either attachment_id or filename is required for get_path and get_content."
                    .to_string(),
            ));
        };

        Ok(AttachmentInfo {
            id: row.id,
            filename: row.original_filename,
            saved_filename: row.saved_filename,
            mime_type: row.mime_type,
            size_bytes: row.size_bytes,
            disk_path: Some(row.disk_path),
            created_at: row.created_at,
        })
    }
}

/// Internal row type for sqlx query mapping.
#[derive(sqlx::FromRow)]
struct AttachmentRow {
    id: String,
    original_filename: String,
    saved_filename: String,
    mime_type: String,
    size_bytes: i64,
    disk_path: String,
    created_at: String,
}

fn format_size(bytes: i64) -> String {
    if bytes >= 1024 * 1024 {
        format!("{:.1} MB", bytes as f64 / (1024.0 * 1024.0))
    } else {
        format!("{:.0} KB", bytes as f64 / 1024.0)
    }
}
