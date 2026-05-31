// Password reset over Connect-RPC JSON. ForgotPassword always returns 200
// to avoid email enumeration — backend returns a generic message regardless
// of whether the email exists. ResetPassword consumes a token + new
// password.

import { lightConnect } from "./api-fetch";

export async function lightForgotPassword(email: string): Promise<void> {
  await lightConnect<{ email: string }, unknown>(
    "proto.auth.v1.AuthService",
    "ForgotPassword",
    { email },
  );
}

export interface LightResetPasswordInput {
  token: string;
  newPassword: string;
}

export async function lightResetPassword(input: LightResetPasswordInput): Promise<void> {
  await lightConnect<{ token: string; newPassword: string }, unknown>(
    "proto.auth.v1.AuthService",
    "ResetPassword",
    { token: input.token, newPassword: input.newPassword },
  );
}
