// Unit tests for clients/web/src/lib/api/userConnect.ts proto → snake_case
// converters. Pins the User / Identity / UserSummary field set so the
// binary wire faithfully round-trips into the call-site shape that
// UserPicker and the auth callback pages consume.
//
// Note: this test file imports @proto/user/v1/user_pb which resolves via
// vitest.config.ts. Under `bazel test //clients/web:unit` the
// `proto/gen` tree is in .bazelignore so the import fails — runs under
// `pnpm test:run` (or once ts_proto_library lands; see runbook
// "TS proto codegen toolchain").

import { describe, it, expect } from "vitest";
import { create } from "@bufbuild/protobuf";
import {
  IdentitySchema,
  UserSchema,
  UserSummarySchema,
} from "@proto/user/v1/user_pb";
import {
  fromProtoIdentity,
  fromProtoUser,
  fromProtoUserSummary,
} from "../connect/userConnect";

describe("fromProtoUser", () => {
  it("converts a full User proto to snake_case shape", () => {
    const proto = create(UserSchema, {
      id: BigInt(42),
      email: "alice@example.com",
      username: "alice",
      name: "Alice",
      avatarUrl: "https://cdn.example.com/a.png",
      isActive: true,
      isSystemAdmin: true,
      isEmailVerified: true,
      lastLoginAt: "2026-05-12T13:16:10Z",
      defaultGitCredentialId: BigInt(7),
      createdAt: "2026-01-01T00:00:00Z",
      updatedAt: "2026-05-12T13:16:10Z",
    });
    const data = fromProtoUser(proto);
    expect(data.id).toBe(42);
    expect(data.email).toBe("alice@example.com");
    expect(data.username).toBe("alice");
    expect(data.name).toBe("Alice");
    expect(data.avatar_url).toBe("https://cdn.example.com/a.png");
    expect(data.is_active).toBe(true);
    expect(data.is_system_admin).toBe(true);
    expect(data.is_email_verified).toBe(true);
    expect(data.last_login_at).toBe("2026-05-12T13:16:10Z");
    expect(data.default_git_credential_id).toBe(7);
    expect(data.created_at).toBe("2026-01-01T00:00:00Z");
    expect(data.updated_at).toBe("2026-05-12T13:16:10Z");
  });

  it("handles missing optionals correctly", () => {
    const proto = create(UserSchema, {
      id: BigInt(1),
      email: "bob@example.com",
      username: "bob",
      isActive: true,
      isSystemAdmin: false,
      isEmailVerified: false,
      createdAt: "2026-01-01T00:00:00Z",
      updatedAt: "2026-01-01T00:00:00Z",
    });
    const data = fromProtoUser(proto);
    expect(data.id).toBe(1);
    expect(data.name).toBeUndefined();
    expect(data.avatar_url).toBeUndefined();
    expect(data.last_login_at).toBeUndefined();
    expect(data.default_git_credential_id).toBeUndefined();
  });
});

describe("fromProtoIdentity", () => {
  it("converts a full Identity proto to snake_case shape", () => {
    const proto = create(IdentitySchema, {
      id: BigInt(101),
      userId: BigInt(42),
      provider: "github",
      providerUserId: "1234567",
      providerUsername: "alice-gh",
      tokenExpiresAt: "2026-06-01T00:00:00Z",
      createdAt: "2026-01-01T00:00:00Z",
      updatedAt: "2026-05-01T00:00:00Z",
    });
    const data = fromProtoIdentity(proto);
    expect(data.id).toBe(101);
    expect(data.user_id).toBe(42);
    expect(data.provider).toBe("github");
    expect(data.provider_user_id).toBe("1234567");
    expect(data.provider_username).toBe("alice-gh");
    expect(data.token_expires_at).toBe("2026-06-01T00:00:00Z");
    expect(data.created_at).toBe("2026-01-01T00:00:00Z");
    expect(data.updated_at).toBe("2026-05-01T00:00:00Z");
  });

  it("handles missing optionals correctly", () => {
    const proto = create(IdentitySchema, {
      id: BigInt(2),
      userId: BigInt(1),
      provider: "google",
      providerUserId: "g-99",
      createdAt: "2026-01-01T00:00:00Z",
      updatedAt: "2026-01-01T00:00:00Z",
    });
    const data = fromProtoIdentity(proto);
    expect(data.provider_username).toBeUndefined();
    expect(data.token_expires_at).toBeUndefined();
  });
});

describe("fromProtoUserSummary", () => {
  it("converts a full UserSummary proto to snake_case shape", () => {
    const proto = create(UserSummarySchema, {
      id: BigInt(42),
      email: "alice@example.com",
      username: "alice",
      name: "Alice",
      avatarUrl: "https://cdn.example.com/a.png",
    });
    const data = fromProtoUserSummary(proto);
    expect(data.id).toBe(42);
    expect(data.email).toBe("alice@example.com");
    expect(data.username).toBe("alice");
    expect(data.name).toBe("Alice");
    expect(data.avatar_url).toBe("https://cdn.example.com/a.png");
  });

  it("handles missing optionals correctly", () => {
    const proto = create(UserSummarySchema, {
      id: BigInt(7),
      email: "bot@example.com",
      username: "bot",
    });
    const data = fromProtoUserSummary(proto);
    expect(data.name).toBeUndefined();
    expect(data.avatar_url).toBeUndefined();
  });
});
