// AUTO-GENERATED — regenerate: pnpm --filter desktop e2e:gen
//
// Source of truth: clients/core/crates/node-bridge/index.d.ts (the
// napi-rs-emitted TypeScript declaration of AppState). Desktop main
// reflects over the prototype to register one ipcMain handler per method,
// so this mirror is what the renderer can actually invoke at runtime.
export interface IpcMethodSchema {
  name: string;
  group: string;
  params: Array<{ name: string; type: string }>;
  returnType: string;
}

export const ipcSchema: IpcMethodSchema[] = [
  {
    "name": "apikeyCreateConnect",
    "group": "apikey",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "apikeyDeleteConnect",
    "group": "apikey",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "apikeyGetConnect",
    "group": "apikey",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "apikeyListConnect",
    "group": "apikey",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "apikeyRevokeConnect",
    "group": "apikey",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "apikeyUpdateConnect",
    "group": "apikey",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "authApplySession",
    "group": "auth",
    "params": [
      {
        "name": "sessionJson",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "authBootstrap",
    "group": "auth",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "authClearSession",
    "group": "auth",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "authFetchOrganizations",
    "group": "auth",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "authGetCurrentOrgJson",
    "group": "auth",
    "params": [],
    "returnType": "string | null"
  },
  {
    "name": "authGetCurrentUserJson",
    "group": "auth",
    "params": [],
    "returnType": "string | null"
  },
  {
    "name": "authGetExpiresAt",
    "group": "auth",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "authGetOrganizationsJson",
    "group": "auth",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "authGetToken",
    "group": "auth",
    "params": [],
    "returnType": "string | null"
  },
  {
    "name": "authIsAuthenticated",
    "group": "auth",
    "params": [],
    "returnType": "boolean"
  },
  {
    "name": "authLogin",
    "group": "auth",
    "params": [
      {
        "name": "email",
        "type": "string"
      },
      {
        "name": "password",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "authLogout",
    "group": "auth",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "authRefreshToken",
    "group": "auth",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "authSetCurrentOrg",
    "group": "auth",
    "params": [
      {
        "name": "orgJson",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "authSetOrganizations",
    "group": "auth",
    "params": [
      {
        "name": "orgsJson",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "authSwitchOrg",
    "group": "auth",
    "params": [
      {
        "name": "slug",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "authConnectForgotPasswordConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectLoginConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectLogoutConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectOauthCallbackConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectOauthRedirectConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectRefreshTokenConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectRegisterConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectResendVerificationConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectResetPasswordConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "authConnectVerifyEmailConnect",
    "group": "auth_connect",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "autopilotAddController",
    "group": "autopilot",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "autopilotAddIteration",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "autopilotControllersJson",
    "group": "autopilot",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "autopilotCurrentControllerJson",
    "group": "autopilot",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "autopilotGetControllerByPodKeyJson",
    "group": "autopilot",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "autopilotGetIterationsJson",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "autopilotGetThinkingHistoryJson",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "autopilotGetThinkingJson",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "autopilotRemoveController",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "autopilotSetControllers",
    "group": "autopilot",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "autopilotSetCurrentController",
    "group": "autopilot",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "autopilotSetIterations",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "autopilotUpdateController",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "autopilotUpdateThinking",
    "group": "autopilot",
    "params": [
      {
        "name": "key",
        "type": "string"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "bindingAcceptBindingConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingApproveScopesConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingCheckBindingConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingGetBoundPodsConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingGetPendingBindingsConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingListBindingsConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingRejectBindingConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingRequestBindingConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingRequestScopesConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "bindingUnbindConnect",
    "group": "binding",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "blockstoreApplyOps",
    "group": "blockstore",
    "params": [
      {
        "name": "reqJson",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "blockstoreApplyRemoteOp",
    "group": "blockstore",
    "params": [
      {
        "name": "opJson",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "blockstoreBacklinksJson",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "blockstoreBlocksJson",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "blockstoreCatchup",
    "group": "blockstore",
    "params": [
      {
        "name": "workspaceId",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "blockstoreEnsureDefaultWorkspace",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "blockstoreGetBlockJson",
    "group": "blockstore",
    "params": [
      {
        "name": "id",
        "type": "string"
      }
    ],
    "returnType": "string | null"
  },
  {
    "name": "blockstoreLastOpId",
    "group": "blockstore",
    "params": [
      {
        "name": "workspaceId",
        "type": "string"
      }
    ],
    "returnType": "number"
  },
  {
    "name": "blockstoreLastOpIdsJson",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "blockstoreListBacklinksJson",
    "group": "blockstore",
    "params": [
      {
        "name": "targetId",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "blockstoreListChildrenJson",
    "group": "blockstore",
    "params": [
      {
        "name": "parentId",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "blockstoreListWorkspaces",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "blockstoreLoadSubtree",
    "group": "blockstore",
    "params": [
      {
        "name": "workspaceId",
        "type": "string"
      },
      {
        "name": "rootId",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "blockstoreLoadTypeDefs",
    "group": "blockstore",
    "params": [
      {
        "name": "workspaceId",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "blockstoreNestChildrenJson",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "blockstoreRefsJson",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "blockstoreSemanticSearch",
    "group": "blockstore",
    "params": [
      {
        "name": "workspaceId",
        "type": "string"
      },
      {
        "name": "reqJson",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "blockstoreSetLastOpId",
    "group": "blockstore",
    "params": [
      {
        "name": "workspaceId",
        "type": "string"
      },
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "blockstoreTypeDefsJson",
    "group": "blockstore",
    "params": [
      {
        "name": "workspaceId",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "blockstoreWorkspacesJson",
    "group": "blockstore",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "channelAddChannelLocal",
    "group": "channel",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelAddMessage",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelChannelMembersJson",
    "group": "channel",
    "params": [
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelChannelPodsJson",
    "group": "channel",
    "params": [
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelChannelsJson",
    "group": "channel",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "channelClearChannelMentions",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelClearChannelUnread",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelCurrentChannelJson",
    "group": "channel",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "channelFilterChannelsJson",
    "group": "channel",
    "params": [
      {
        "name": "query",
        "type": "string"
      },
      {
        "name": "includeArchived",
        "type": "boolean"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelGetChannelJson",
    "group": "channel",
    "params": [
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelGetLastMessageJson",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelGetMentionCount",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "number"
  },
  {
    "name": "channelGetMessagesJson",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelGetUnreadCount",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "number"
  },
  {
    "name": "channelIncrementMention",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelIncrementUnread",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelMentionCountsJson",
    "group": "channel",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "channelOnNewMessage",
    "group": "channel",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "boolean"
  },
  {
    "name": "channelPrependMessages",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      },
      {
        "name": "json",
        "type": "string"
      },
      {
        "name": "hasMore",
        "type": "boolean"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelRemoveChannelLocal",
    "group": "channel",
    "params": [
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelRemoveMessageLocal",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      },
      {
        "name": "messageId",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSelectChannel",
    "group": "channel",
    "params": [
      {
        "name": "id",
        "type": "number | undefined | null"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelSetChannelPodsLocal",
    "group": "channel",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "channelSetChannels",
    "group": "channel",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSetCurrentChannel",
    "group": "channel",
    "params": [
      {
        "name": "id",
        "type": "number | undefined | null"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSetCurrentUser",
    "group": "channel",
    "params": [
      {
        "name": "userJson",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSetCurrentUserId",
    "group": "channel",
    "params": [
      {
        "name": "userId",
        "type": "number | undefined | null"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSetLastMessage",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSetMentionCounts",
    "group": "channel",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSetMessages",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      },
      {
        "name": "json",
        "type": "string"
      },
      {
        "name": "hasMore",
        "type": "boolean"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSetUnreadCounts",
    "group": "channel",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelSortedChannelIdsJson",
    "group": "channel",
    "params": [
      {
        "name": "mode",
        "type": "string"
      },
      {
        "name": "includeArchived",
        "type": "boolean"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "channelTotalMentionCount",
    "group": "channel",
    "params": [],
    "returnType": "number"
  },
  {
    "name": "channelTotalUnreadCount",
    "group": "channel",
    "params": [],
    "returnType": "number"
  },
  {
    "name": "channelUnreadCountsJson",
    "group": "channel",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "channelUpdateChannelLocal",
    "group": "channel",
    "params": [
      {
        "name": "id",
        "type": "number"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "channelUpdateMessageLocal",
    "group": "channel",
    "params": [
      {
        "name": "channelId",
        "type": "number"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "envBundleCreateEnvBundleConnect",
    "group": "env_bundle",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "envBundleDeleteEnvBundleConnect",
    "group": "env_bundle",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "envBundleGetEnvBundleConnect",
    "group": "env_bundle",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "envBundleListEnvBundlesConnect",
    "group": "env_bundle",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "envBundleSetPrimaryEnvBundleConnect",
    "group": "env_bundle",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "envBundleUpdateEnvBundleConnect",
    "group": "env_bundle",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionCreateSkillRegistryConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionDeleteSkillRegistryConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionInstallCustomMcpServerConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionInstallMcpFromMarketConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionInstallSkillFromGithubConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionInstallSkillFromMarketConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionInstallSkillFromUploadedFileConnect",
    "group": "extension",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "extensionListMarketMcpServersConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionListMarketSkillsConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionListRepoMcpServersConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionListRepoSkillsConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionListSkillRegistriesConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionListSkillRegistryOverridesConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionPresignSkillUploadConnect",
    "group": "extension",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "extensionSyncSkillRegistryConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionTogglePlatformRegistryConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionUninstallMcpServerConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionUninstallSkillConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionUpdateMcpServerConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "extensionUpdateSkillConnect",
    "group": "extension",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "fileUploadFile",
    "group": "file",
    "params": [
      {
        "name": "fileData",
        "type": "Array<number>"
      },
      {
        "name": "filename",
        "type": "string"
      },
      {
        "name": "contentType",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "invitationAcceptInvitationConnect",
    "group": "invitation",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "invitationCreateInvitationConnect",
    "group": "invitation",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "invitationGetInvitationByTokenConnect",
    "group": "invitation",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "invitationListInvitationsConnect",
    "group": "invitation",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "invitationListPendingInvitationsConnect",
    "group": "invitation",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "invitationResendInvitationConnect",
    "group": "invitation",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "invitationRevokeInvitationConnect",
    "group": "invitation",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "localRunnerBinaryPath",
    "group": "local_runner",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "localRunnerFallbackVersion",
    "group": "local_runner",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "localRunnerHostTarget",
    "group": "local_runner",
    "params": [],
    "returnType": "string | null"
  },
  {
    "name": "localRunnerInstallBinary",
    "group": "local_runner",
    "params": [
      {
        "name": "releaseUrl",
        "type": "string"
      },
      {
        "name": "expectedSha256",
        "type": "string | undefined | null"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "localRunnerInstalledVersion",
    "group": "local_runner",
    "params": [],
    "returnType": "string | null"
  },
  {
    "name": "localRunnerIsInstalled",
    "group": "local_runner",
    "params": [],
    "returnType": "boolean"
  },
  {
    "name": "localRunnerIsRegistered",
    "group": "local_runner",
    "params": [],
    "returnType": "boolean"
  },
  {
    "name": "localRunnerLocalNodeId",
    "group": "local_runner",
    "params": [],
    "returnType": "string | null"
  },
  {
    "name": "localRunnerRegister",
    "group": "local_runner",
    "params": [
      {
        "name": "token",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "localRunnerServiceInstall",
    "group": "local_runner",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "localRunnerServiceStart",
    "group": "local_runner",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "localRunnerServiceStatus",
    "group": "local_runner",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "localRunnerServiceStop",
    "group": "local_runner",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "localRunnerServiceUninstall",
    "group": "local_runner",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "loopSvcAddRun",
    "group": "loop_svc",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "loopSvcAppendRuns",
    "group": "loop_svc",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "loopSvcClearRuns",
    "group": "loop_svc",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "loopSvcCurrentLoopJson",
    "group": "loop_svc",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "loopSvcGetLoopBySlugJson",
    "group": "loop_svc",
    "params": [
      {
        "name": "slug",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "loopSvcLoopsJson",
    "group": "loop_svc",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "loopSvcRunsJson",
    "group": "loop_svc",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "loopSvcSetCurrentLoop",
    "group": "loop_svc",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "loopSvcSetLoops",
    "group": "loop_svc",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "loopSvcSetRuns",
    "group": "loop_svc",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "loopSvcUpdateLoopLocal",
    "group": "loop_svc",
    "params": [
      {
        "name": "slug",
        "type": "string"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "loopSvcUpdateRunStatus",
    "group": "loop_svc",
    "params": [
      {
        "name": "runId",
        "type": "number"
      },
      {
        "name": "status",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "meshBatchGetTicketPodsConnect",
    "group": "mesh",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "meshClearTopology",
    "group": "mesh",
    "params": [],
    "returnType": "void"
  },
  {
    "name": "meshCreatePodForTicketConnect",
    "group": "mesh",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "meshFetchTopology",
    "group": "mesh",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "meshGetActiveNodesJson",
    "group": "mesh",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "meshGetChannelsForNodeJson",
    "group": "mesh",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "meshGetEdgesForNodeJson",
    "group": "mesh",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "meshGetMeshTopologyConnect",
    "group": "mesh",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "meshGetNodeJson",
    "group": "mesh",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "meshGetNodesByRunnerJson",
    "group": "mesh",
    "params": [
      {
        "name": "runnerId",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "meshGetRunnerInfoJson",
    "group": "mesh",
    "params": [
      {
        "name": "runnerId",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "meshGetTicketPodsConnect",
    "group": "mesh",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "meshSelectedNode",
    "group": "mesh",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "meshSelectNode",
    "group": "mesh",
    "params": [
      {
        "name": "podKey",
        "type": "string | undefined | null"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "meshTopologyJson",
    "group": "mesh",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "podCurrentPodJson",
    "group": "pod",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "podGetPodJson",
    "group": "pod",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "podPodsJson",
    "group": "pod",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "podRemovePod",
    "group": "pod",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "podUpdateAgentStatus",
    "group": "pod",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      },
      {
        "name": "agentStatus",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "podUpdatePodAlias",
    "group": "pod",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      },
      {
        "name": "alias",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "podUpdatePodStatus",
    "group": "pod",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      },
      {
        "name": "status",
        "type": "string"
      },
      {
        "name": "agentStatus",
        "type": "string | undefined | null"
      },
      {
        "name": "errorCode",
        "type": "string | undefined | null"
      },
      {
        "name": "errorMessage",
        "type": "string | undefined | null"
      },
      {
        "name": "timestamp",
        "type": "number | undefined | null"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "podUpdatePodTitle",
    "group": "pod",
    "params": [
      {
        "name": "podKey",
        "type": "string"
      },
      {
        "name": "title",
        "type": "string"
      },
      {
        "name": "timestamp",
        "type": "number | undefined | null"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "promocodeGetRedemptionHistoryConnect",
    "group": "promocode",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "promocodeRedeemPromoCodeConnect",
    "group": "promocode",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "promocodeValidatePromoCodeConnect",
    "group": "promocode",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "runnerAuthorizeRunner",
    "group": "runner",
    "params": [
      {
        "name": "requestJson",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "runnerAvailableRunnersJson",
    "group": "runner",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "runnerCurrentRunnerJson",
    "group": "runner",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "runnerGetAuthStatus",
    "group": "runner",
    "params": [
      {
        "name": "authKey",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "runnerGetRunnerJson",
    "group": "runner",
    "params": [
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "runnerListRunnerPods",
    "group": "runner",
    "params": [
      {
        "name": "id",
        "type": "number"
      },
      {
        "name": "status",
        "type": "string | undefined | null"
      },
      {
        "name": "limit",
        "type": "number | undefined | null"
      },
      {
        "name": "offset",
        "type": "number | undefined | null"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "runnerRemoveRunnerLocal",
    "group": "runner",
    "params": [
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "runnerRunnersJson",
    "group": "runner",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "runnerSetAvailableRunners",
    "group": "runner",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "runnerSetCurrentRunner",
    "group": "runner",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "runnerSetRunners",
    "group": "runner",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "runnerUpdateRunner",
    "group": "runner",
    "params": [
      {
        "name": "id",
        "type": "number"
      },
      {
        "name": "requestJson",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "runnerUpdateRunnerLocal",
    "group": "runner",
    "params": [
      {
        "name": "id",
        "type": "number"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "runnerUpdateRunnerStatus",
    "group": "runner",
    "params": [
      {
        "name": "id",
        "type": "number"
      },
      {
        "name": "status",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ssoDiscoverConnect",
    "group": "sso",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ssoLdapAuthConnect",
    "group": "sso",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "supportTicketAddSupportTicketMessageConnect",
    "group": "support_ticket",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "supportTicketAssociateAttachmentsConnect",
    "group": "support_ticket",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "supportTicketCreateSupportTicketConnect",
    "group": "support_ticket",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "supportTicketGetAttachmentUrlConnect",
    "group": "support_ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "supportTicketGetSupportTicketConnect",
    "group": "support_ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "supportTicketListSupportTicketsConnect",
    "group": "support_ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "supportTicketPresignAttachmentUploadConnect",
    "group": "support_ticket",
    "params": [],
    "returnType": "any"
  },
  {
    "name": "ticketAddAssigneeConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketAddLabel",
    "group": "ticket",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketAddLabelConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketAddTicket",
    "group": "ticket",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketAppendColumnTickets",
    "group": "ticket",
    "params": [
      {
        "name": "status",
        "type": "string"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketBoardColumnsJson",
    "group": "ticket",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "ticketCreateLabelConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketCreateTicketConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketCurrentTicketJson",
    "group": "ticket",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "ticketDeleteLabelConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketDeleteTicketConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketFilterTicketsJson",
    "group": "ticket",
    "params": [
      {
        "name": "search",
        "type": "string"
      },
      {
        "name": "statusesJson",
        "type": "string"
      },
      {
        "name": "prioritiesJson",
        "type": "string"
      },
      {
        "name": "repositoryIdsJson",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "ticketGetActiveTicketsConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketGetBoardConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketGetSubTicketsConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketGetTicketBySlugJson",
    "group": "ticket",
    "params": [
      {
        "name": "slug",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "ticketGetTicketConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketGetTicketPods",
    "group": "ticket",
    "params": [
      {
        "name": "slug",
        "type": "string"
      },
      {
        "name": "activeOnly",
        "type": "boolean | undefined | null"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "ticketLabelsJson",
    "group": "ticket",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "ticketListLabelsConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketListTicketsConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRemoveAssigneeConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRemoveLabel",
    "group": "ticket",
    "params": [
      {
        "name": "id",
        "type": "number"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketRemoveLabelConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRemoveTicket",
    "group": "ticket",
    "params": [
      {
        "name": "slug",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketSetBoardColumns",
    "group": "ticket",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketSetCurrentTicket",
    "group": "ticket",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketSetLabels",
    "group": "ticket",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketSetTickets",
    "group": "ticket",
    "params": [
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketTicketPodsJson",
    "group": "ticket",
    "params": [
      {
        "name": "slug",
        "type": "string"
      }
    ],
    "returnType": "string"
  },
  {
    "name": "ticketTicketsJson",
    "group": "ticket",
    "params": [],
    "returnType": "string"
  },
  {
    "name": "ticketUpdateLabelConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketUpdateTicketConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketUpdateTicketLocal",
    "group": "ticket",
    "params": [
      {
        "name": "slug",
        "type": "string"
      },
      {
        "name": "json",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketUpdateTicketStatusConnect",
    "group": "ticket",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketUpdateTicketStatusLocal",
    "group": "ticket",
    "params": [
      {
        "name": "slug",
        "type": "string"
      },
      {
        "name": "status",
        "type": "string"
      }
    ],
    "returnType": "void"
  },
  {
    "name": "ticketRelationsCreateCommentConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsCreateRelationConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsDeleteCommentConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsDeleteRelationConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsLinkCommitConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsListCommentsConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsListCommitsConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsListMergeRequestsConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsListRelationsConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsUnlinkCommitConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "ticketRelationsUpdateCommentConnect",
    "group": "ticket_relations",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "userChangePasswordConnect",
    "group": "user",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "userDeleteIdentityConnect",
    "group": "user",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "userGetMeConnect",
    "group": "user",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "userListIdentitiesConnect",
    "group": "user",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "userSearchUsersConnect",
    "group": "user",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  },
  {
    "name": "userUpdateMeConnect",
    "group": "user",
    "params": [
      {
        "name": "request",
        "type": "Array<number>"
      }
    ],
    "returnType": "Array<number>"
  }
];
