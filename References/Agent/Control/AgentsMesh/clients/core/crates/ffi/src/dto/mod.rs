// DTO layer: UniFFI `Record` / `Enum` definitions that map from internal
// `agentsmesh-types` structs to FFI-friendly shapes (no HashMap, no
// chrono, no lifetimes). Populated per service migration in Phase 1.
//
// Re-exports are kept broad so the generated Swift surface contains every
// named record; unused warnings are suppressed because uniffi consumes the
// types via `#[uniffi::export]` in service files, not via direct imports.
#![allow(unused_imports)]

mod automation;
mod billing_dto;
mod blocks_mesh;
mod channel;
mod misc;
mod pod;
mod repository_dto;
mod runner_dto;
mod ticket;
mod user;

pub use automation::{
    AutopilotControllerDto, AutopilotIterationDto, AutopilotIterationListResponseDto,
    AutopilotListResponseDto, AutopilotStatusDto, CreateAutopilotRequestDto, CreateLoopRequestDto,
    LoopDataDto, LoopListResponseDto, LoopRunDataDto, LoopRunListResponseDto, LoopRunStatusDto,
    UpdateLoopRequestDto,
};
pub use billing_dto::{
    BillingOverviewDto, ChangeBillingCycleRequestDto, CheckoutStatusDto,
    CreateCheckoutRequestDto, CreateCheckoutResponseDto, CreateSubscriptionRequestDto,
    DeploymentInfoDto, InvoiceDto, InvoiceListResponseDto, PlanListResponseDto,
    PublicPlanPricingDto, PublicPricingResponseDto, SeatUsageDto, SubscriptionDto,
    SubscriptionPlanDto, UpdateSubscriptionRequestDto, UpgradeSubscriptionRequestDto,
    UsageOverviewDto,
};
pub(crate) use billing_dto::{invoice_list_from_proto, plan_list_from_proto};
pub use blocks_mesh::{
    ActorTypeDto, ApplyOpsRequestDto, ApplyOpsResultDto, BlockDto, BlockOpDto, BlockRefDto,
    ChildrenResultDto, MeshChannelInfoDto, MeshEdgeDto, MeshNodeDto, MeshRunnerInfoDto,
    MeshTopologyDto, NotificationPreferenceDto, NotificationPreferenceListResponseDto, OpEnvelopeDto,
    OpKindDto, SearchHitDto, SemanticSearchRequestDto, SetNotificationPreferenceRequestDto,
    WorkspaceDto,
};
pub(crate) use blocks_mesh::notification_list_from_proto;
pub use misc::{
    InvitationDto, InvitationListResponseDto, PresignRequestDto, PresignResponseDto,
    ResourceGrantDto, ResourceGrantListResponseDto, ResourceGrantResponseDto,
    ResourceGrantUserBriefDto,
};
pub(crate) use misc::{
    invitation_list_from_proto, pending_invitation_list_from_proto, resource_grant_list_from_proto,
};

pub use channel::{
    ChannelDto, ChannelListResponseDto, ChannelMemberDto, ChannelMemberListResponseDto,
    ChannelMessageDto, ChannelMessageListResponseDto, ChannelUnreadResponseDto,
    CreateChannelRequestDto, MessagePreviewDto, SenderAgentInfoDto, SenderPodInfoDto,
    UpdateChannelRequestDto,
};
pub use ticket::{
    BoardColumnDto, BoardResponseDto, CreateLabelRequestDto, CreateTicketRequestDto, LabelDto,
    LabelListResponseDto, TicketDto, TicketListResponseDto, TicketPriorityDto, TicketStatusDto,
    UpdateLabelRequestDto, UpdateTicketRequestDto,
};

pub use pod::{
    CreatePodRequestDto, CreatePodResponseDto, PodAgentInfoDto, PodConnectionInfoDto,
    PodCreatedByInfoDto, PodDto, PodListResponseDto, PodLoopInfoDto, PodRepositoryInfoDto,
    PodRunnerInfoDto, PodStatusDto, PodTicketInfoDto,
};
pub(crate) use pod::{build_create_pod_proto_request, parse_pod_status};
pub use user::{
    AuthSessionDto, AuthTokensDto, BootstrapCleanupReasonDto, BootstrapResultDto,
    OrganizationDto, SSOConfigDto, UserDto, UserIdentityDto,
};
pub use repository_dto::{
    BranchDto, CreateRepositoryRequestDto, MergeRequestListResponseDto, RepositoryDto,
    RepositoryListResponseDto, RepositoryMergeRequestDto, UpdateRepositoryRequestDto,
    WebhookSecretDto, WebhookStatusDto,
};
pub(crate) use repository_dto::{
    build_create_repository_proto_request, build_update_repository_proto_request,
    list_branches_from_proto, merge_request_list_from_proto, repository_list_from_proto,
};
pub use runner_dto::{
    AuthorizeRunnerRequestDto, CreateRunnerTokenRequestDto, GrpcRegistrationTokenDto,
    RunnerAuthStatusDto, RunnerDto, RunnerListResponseDto, RunnerLogDto, RunnerLogListResponseDto,
    RunnerStatusDto, RunnerTokenListResponseDto, UpdateRunnerRequestDto, UpgradeRunnerRequestDto,
};
pub(crate) use runner_dto::{
    runner_list_from_proto, runner_log_list_from_proto, runner_token_list_from_proto,
};
