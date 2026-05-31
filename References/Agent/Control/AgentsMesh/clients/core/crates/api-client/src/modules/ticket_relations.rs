use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_ticket_relations_v1 as tr_proto;

// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
//
// These methods call the Connect handlers in
// backend/internal/api/connect/ticket_relations/. Procedure paths derive from
// `proto.ticket_relations.v1.TicketRelationsService.<Method>` (conventions §12).
impl ApiClient {
    pub async fn list_relations_connect(
        &self,
        req: &tr_proto::ListRelationsRequest,
    ) -> Result<tr_proto::ListRelationsResponse, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/ListRelations",
            req,
        )
        .await
    }

    pub async fn create_relation_connect(
        &self,
        req: &tr_proto::CreateRelationRequest,
    ) -> Result<tr_proto::Relation, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/CreateRelation",
            req,
        )
        .await
    }

    pub async fn delete_relation_connect(
        &self,
        req: &tr_proto::DeleteRelationRequest,
    ) -> Result<tr_proto::DeleteRelationResponse, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/DeleteRelation",
            req,
        )
        .await
    }

    pub async fn list_ticket_merge_requests_connect(
        &self,
        req: &tr_proto::ListMergeRequestsRequest,
    ) -> Result<tr_proto::ListMergeRequestsResponse, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/ListMergeRequests",
            req,
        )
        .await
    }

    pub async fn list_ticket_commits_connect(
        &self,
        req: &tr_proto::ListCommitsRequest,
    ) -> Result<tr_proto::ListCommitsResponse, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/ListCommits",
            req,
        )
        .await
    }

    pub async fn link_commit_connect(
        &self,
        req: &tr_proto::LinkCommitRequest,
    ) -> Result<tr_proto::Commit, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/LinkCommit",
            req,
        )
        .await
    }

    pub async fn unlink_commit_connect(
        &self,
        req: &tr_proto::UnlinkCommitRequest,
    ) -> Result<tr_proto::UnlinkCommitResponse, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/UnlinkCommit",
            req,
        )
        .await
    }

    pub async fn list_comments_connect(
        &self,
        req: &tr_proto::ListCommentsRequest,
    ) -> Result<tr_proto::ListCommentsResponse, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/ListComments",
            req,
        )
        .await
    }

    pub async fn create_comment_connect(
        &self,
        req: &tr_proto::CreateCommentRequest,
    ) -> Result<tr_proto::Comment, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/CreateComment",
            req,
        )
        .await
    }

    pub async fn update_comment_connect(
        &self,
        req: &tr_proto::UpdateCommentRequest,
    ) -> Result<tr_proto::Comment, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/UpdateComment",
            req,
        )
        .await
    }

    pub async fn delete_comment_connect(
        &self,
        req: &tr_proto::DeleteCommentRequest,
    ) -> Result<tr_proto::DeleteCommentResponse, ApiError> {
        connect_call(
            self,
            "/proto.ticket_relations.v1.TicketRelationsService/DeleteComment",
            req,
        )
        .await
    }
}
