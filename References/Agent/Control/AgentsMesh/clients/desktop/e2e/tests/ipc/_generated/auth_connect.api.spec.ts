// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · auth_connect", () => {
  test("authConnectForgotPasswordConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectForgotPasswordConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectLoginConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectLoginConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectLogoutConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectLogoutConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectOauthCallbackConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectOauthCallbackConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectOauthRedirectConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectOauthRedirectConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectRefreshTokenConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectRefreshTokenConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectRegisterConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectRegisterConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectResendVerificationConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectResendVerificationConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectResetPasswordConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectResetPasswordConnect", returnType: "Array<number>" }, []);
  });

  test("authConnectVerifyEmailConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authConnectVerifyEmailConnect", returnType: "Array<number>" }, []);
  });
});
