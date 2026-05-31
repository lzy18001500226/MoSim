export type {
  AgentAttachmentCapability,
  AgentAttachmentCapabilityTarget,
  AgentAttachmentErrorJson,
  AgentAttachmentPayload,
  AttachmentDeliveryFailureCode,
  AttachmentValidationResult,
  AttachmentWarning,
  AttachmentWarningCode,
  ImageOptimizationBudget,
} from '../core/domain';
export { AGENT_ATTACHMENT_SCHEMA_VERSION } from '../core/domain';
export {
  estimateAgentAttachmentSerializedPayloadBytes,
  MAX_AGENT_ATTACHMENT_SERIALIZED_PAYLOAD_BYTES,
} from '../core/domain';
