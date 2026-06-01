import {
  adminClient,
  emailOTPClient,
  passkeyClient,
  usernameClient,
} from "better-auth/client/plugins";
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  plugins: [passkeyClient(), usernameClient(), adminClient(), emailOTPClient()],
});

export type ErrorTypes = Record<keyof typeof authClient.$ERROR_CODES, string>;
export type Session = typeof authClient.$Infer.Session;
