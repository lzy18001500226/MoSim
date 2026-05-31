// Web userApi facade — delegates to the Connect-RPC adapter
// (clients/web/src/lib/api/userConnect.ts) which carries the binary wire
// to the wasm bridge. Keeping this thin shim lets existing call sites
// (UserPicker, auth callback pages) import { userApi } unchanged while
// the underlying transport flips from REST JSON to Connect binary.

import {
  changePassword as connectChangePassword,
  deleteIdentity as connectDeleteIdentity,
  getMe as connectGetMe,
  listIdentities as connectListIdentities,
  searchUsers as connectSearchUsers,
  updateMe as connectUpdateMe,
  type Identity,
  type User,
  type UserSummary,
} from "@/lib/api/connect/userConnect";

export type { Identity, User, UserSummary };

export const userApi = {
  // /me returns the wrapped REST-style shape { user } so legacy callers
  // that destructure `.user` keep working through the Connect lane.
  getMe: async (): Promise<{ user: User }> => {
    const user = await connectGetMe();
    return { user };
  },
  updateMe: async (input: {
    name?: string;
    avatar_url?: string;
  }): Promise<{ user: User }> => {
    const user = await connectUpdateMe(input);
    return { user };
  },
  changePassword: connectChangePassword,
  listIdentities: connectListIdentities,
  deleteIdentity: connectDeleteIdentity,
  search: async (
    q: string,
    limit = 10,
  ): Promise<{ users: UserSummary[] }> => {
    const { items } = await connectSearchUsers(q, limit);
    return { users: items };
  },
};
