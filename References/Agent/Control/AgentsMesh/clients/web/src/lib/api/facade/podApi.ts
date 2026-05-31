import { readCurrentOrg } from "@/stores/auth";
import { createPod, terminatePod, type CreatePodInput } from "../connect/podConnect";

function orgSlug(): string {
  return readCurrentOrg()?.slug ?? "";
}

export const podApi = {
  create: async (data: CreatePodInput) => {
    return createPod(orgSlug(), data);
  },
  terminate: async (podKey: string) => {
    await terminatePod(orgSlug(), podKey);
  },
};
