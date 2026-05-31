// ── Enums ─────────────────────────────────────────────────

#[derive(Clone, Copy, Debug, uniffi::Enum)]
pub enum TicketStatusDto {
    Backlog,
    Todo,
    InProgress,
    InReview,
    Done,
    Unknown,
}

impl TicketStatusDto {
    pub fn from_wire(s: &str) -> Self {
        match s {
            "backlog" => Self::Backlog,
            "todo" => Self::Todo,
            "in_progress" => Self::InProgress,
            "in_review" => Self::InReview,
            "done" => Self::Done,
            _ => Self::Unknown,
        }
    }

    pub fn to_wire(self) -> &'static str {
        match self {
            Self::Backlog => "backlog",
            Self::Todo => "todo",
            Self::InProgress => "in_progress",
            Self::InReview => "in_review",
            Self::Done => "done",
            Self::Unknown => "unknown",
        }
    }
}

#[derive(Clone, Copy, Debug, uniffi::Enum)]
pub enum TicketPriorityDto {
    None,
    Low,
    Medium,
    High,
    Urgent,
    Unknown,
}

impl TicketPriorityDto {
    pub fn from_wire(s: &str) -> Self {
        match s {
            "none" => Self::None,
            "low" => Self::Low,
            "medium" => Self::Medium,
            "high" => Self::High,
            "urgent" => Self::Urgent,
            _ => Self::Unknown,
        }
    }

    pub fn to_wire(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::Low => "low",
            Self::Medium => "medium",
            Self::High => "high",
            Self::Urgent => "urgent",
            Self::Unknown => "unknown",
        }
    }
}

// ── Ticket ────────────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct TicketDto {
    pub slug: String,
    pub title: String,
    pub content: Option<String>,
    pub status: TicketStatusDto,
    pub priority: TicketPriorityDto,
    pub repository_id: Option<i64>,
    pub parent_slug: Option<String>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct TicketListResponseDto {
    pub tickets: Vec<TicketDto>,
    pub total: Option<i64>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct BoardColumnDto {
    pub status: TicketStatusDto,
    pub tickets: Vec<TicketDto>,
    pub total_count: i64,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct BoardResponseDto {
    pub columns: Vec<BoardColumnDto>,
    /// Opaque JSON of per-priority counts (server-side aggregated).
    pub priority_counts_json: Option<String>,
}

// ── Label ─────────────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct LabelDto {
    pub id: i64,
    pub name: String,
    pub color: String,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct LabelListResponseDto {
    pub labels: Vec<LabelDto>,
}

// ── Request DTOs ──────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct CreateTicketRequestDto {
    pub title: String,
    pub content: Option<String>,
    pub priority: Option<TicketPriorityDto>,
    pub severity: Option<String>,
    pub estimate: Option<f64>,
    pub repository_id: Option<i64>,
    pub assignee_ids: Option<Vec<i64>>,
    pub labels: Option<Vec<i64>>,
    pub parent_slug: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct UpdateTicketRequestDto {
    pub title: Option<String>,
    pub content: Option<String>,
    pub priority: Option<TicketPriorityDto>,
    pub severity: Option<String>,
    pub estimate: Option<f64>,
    pub repository_id: Option<i64>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct CreateLabelRequestDto {
    pub name: String,
    pub color: String,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct UpdateLabelRequestDto {
    pub name: Option<String>,
    pub color: Option<String>,
}
