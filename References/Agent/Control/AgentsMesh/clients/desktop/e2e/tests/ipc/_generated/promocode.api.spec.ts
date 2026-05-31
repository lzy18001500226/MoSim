// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · promocode", () => {
  test("promocodeGetRedemptionHistoryConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "promocodeGetRedemptionHistoryConnect", returnType: "Array<number>" }, []);
  });

  test("promocodeRedeemPromoCodeConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "promocodeRedeemPromoCodeConnect", returnType: "Array<number>" }, []);
  });

  test("promocodeValidatePromoCodeConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "promocodeValidatePromoCodeConnect", returnType: "Array<number>" }, []);
  });
});
