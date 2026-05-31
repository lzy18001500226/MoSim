// Connect-RPC adapter for proto.notification.v1.NotificationService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out — conventions §2.5), decodes
// responses via .fromBinary(). Returns proto types directly — no DTO adapter.

import {
  ListPreferencesRequestSchema,
  ListPreferencesResponseSchema,
  SetPreferenceRequestSchema,
  NotificationPreferenceSchema,
  type NotificationPreference,
} from "@proto/notification/v1/notification_pb";
import { create, toBinary, fromBinary, type MessageInitShape } from "@bufbuild/protobuf";
import { getNotificationService } from "@/lib/wasm-core";

export type { NotificationPreference } from "@proto/notification/v1/notification_pb";

export async function listPreferencesConnect(
  orgSlug: string,
): Promise<NotificationPreference[]> {
  const req = create(ListPreferencesRequestSchema, { orgSlug });
  const bytes = toBinary(ListPreferencesRequestSchema, req);
  const respBytes = await getNotificationService().listPreferencesConnect(bytes);
  const resp = fromBinary(ListPreferencesResponseSchema, new Uint8Array(respBytes));
  return resp.items;
}

export async function setPreferenceConnect(
  input: MessageInitShape<typeof SetPreferenceRequestSchema>,
): Promise<NotificationPreference> {
  const req = create(SetPreferenceRequestSchema, input);
  const bytes = toBinary(SetPreferenceRequestSchema, req);
  const respBytes = await getNotificationService().setPreferenceConnect(bytes);
  return fromBinary(NotificationPreferenceSchema, new Uint8Array(respBytes));
}
