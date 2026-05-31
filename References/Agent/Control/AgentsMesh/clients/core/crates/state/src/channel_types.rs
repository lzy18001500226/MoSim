// Client-side channel cache types. The canonical schema is
// `proto.channel_state.v1.*` — this module re-exports the prost-generated
// structs so existing import sites (`crate::channel_types::Channel`,
// `crate::channel_types::ChannelMessage`, etc.) keep working without a
// wholesale rename.
//
// All proto state types derive `serde::{Serialize, Deserialize}` via the
// `rust_prost_transform` in proto/channel_state/v1/BUILD.bazel, so the
// JSON-bridge surface (channels_json, last_messages_json, etc.) keeps
// working out of the box.

pub use agentsmesh_types::proto_channel_state_v1::{
    Channel, ChannelMember, ChannelMessage, MessagePreview, SenderAgentInfo,
    SenderPodInfo, SenderUser,
};

// Compatibility alias — `crate::channel_types::User` historically pointed
// at `auth_types::User`. After R6, channel-side User references use
// the trimmed `SenderUser` shape from the state schema.
pub use SenderUser as User;
