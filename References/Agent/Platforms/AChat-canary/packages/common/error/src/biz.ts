export const BizCodeEnum = {
  // General
  InvalidRequest: "INVALID_REQUEST",
  Unauthorized: "UNAUTHORIZED",
  Forbidden: "FORBIDDEN",
  Conflict: "CONFLICT",

  // Authentication
  AuthFailed: "AUTH_FAILED",
  InvalidPassword: "INVALID_PASSWORD",
  InvalidVerificationCode: "INVALID_VERIFICATION_CODE",
  InvalidVerificationToken: "INVALID_VERIFICATION_TOKEN",
  VerifyCodeTooFrequently: "VERIFY_CODE_TOO_FREQUENTLY",
  VerifyCodeSendFailed: "VERIFY_CODE_SEND_FAILED",
  EmailAlreadyUsed: "EMAIL_ALREADY_USED",
  RegisterFailed: "REGISTER_FAILED",
  // User
  UserNotFound: "USER_NOT_FOUND",
  OrganizationNotFound: "ORGANIZATION_NOT_FOUND",
  // Messages
  ConversationNotFound: "CONVERSATION_NOT_FOUND",
  MessageNotFound: "MESSAGE_NOT_FOUND",
} as const;

export type BizCode = (typeof BizCodeEnum)[keyof typeof BizCodeEnum];

export default class BizError extends Error {
  name = "BizError";

  public readonly code: BizCode;
  public readonly statusCode: number;
  public readonly message: string;

  constructor(code: BizCode) {
    const [statusCode, message] = BizErrorEnum[code];
    super(message);
    this.code = code;
    this.statusCode = statusCode;
    this.message = message;
  }
}

export const BizErrorEnum: Record<
  BizCode,
  [statusCode: number, message: string]
> = {
  [BizCodeEnum.InvalidRequest]: [400, "Invalid request"],
  [BizCodeEnum.Unauthorized]: [401, "Unauthorized"],
  [BizCodeEnum.Forbidden]: [403, "Forbidden"],
  [BizCodeEnum.Conflict]: [409, "Conflict"],
  [BizCodeEnum.AuthFailed]: [401, "Authentication failed"],
  [BizCodeEnum.InvalidPassword]: [401, "Invalid password"],
  [BizCodeEnum.InvalidVerificationCode]: [401, "Invalid verification code"],
  [BizCodeEnum.InvalidVerificationToken]: [401, "Invalid verification token"],
  [BizCodeEnum.VerifyCodeTooFrequently]: [429, "Verify code too frequently"],
  [BizCodeEnum.VerifyCodeSendFailed]: [500, "Verify code send failed"],
  [BizCodeEnum.EmailAlreadyUsed]: [400, "Email already used"],
  [BizCodeEnum.RegisterFailed]: [400, "Register failed"],
  [BizCodeEnum.UserNotFound]: [404, "User not found"],
  [BizCodeEnum.OrganizationNotFound]: [404, "Organization not found"],
  [BizCodeEnum.ConversationNotFound]: [404, "Conversation not found"],
  [BizCodeEnum.MessageNotFound]: [404, "Message not found"],
} as const;
