// /api/v1/users/me equivalent over Connect (proto.user.v1.UserService/GetMe).
// Three (auth) pages (invite acceptance, onboarding, runners/authorize) read
// the viewer's email just to display "Signed in as <email>" / derive a
// default workspace name without booting wasm. Returns null on any failure —
// these pages use it as best-effort UI sugar and must keep working when the
// call fails.

import { lightConnect } from "./api-fetch";

export interface LightUser {
  id: number;
  email: string;
  username: string;
  name?: string;
  avatar_url?: string;
}

// Per proto/user/v1/user.proto convention: GetMe returns the User message
// directly (no envelope wrapper). Connect JSON transport mirrors that shape.
interface ConnectMeUser {
  id?: number | string;
  email?: string;
  username?: string;
  name?: string;
  avatarUrl?: string;
}

export async function lightFetchMe(): Promise<LightUser | null> {
  try {
    const u = await lightConnect<Record<string, never>, ConnectMeUser>(
      "proto.user.v1.UserService",
      "GetMe",
      {},
      { authenticated: true },
    );
    if (!u || u.email === undefined || u.username === undefined) return null;
    return {
      id: Number(u.id ?? 0),
      email: u.email,
      username: u.username,
      name: u.name,
      avatar_url: u.avatarUrl,
    };
  } catch {
    return null;
  }
}
