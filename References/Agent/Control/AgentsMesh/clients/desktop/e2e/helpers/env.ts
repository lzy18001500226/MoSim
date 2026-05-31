import { resolve } from "node:path";
import {
  getApiBaseUrl,
  getComposeProject,
  getPostgresContainer,
  TEST_USER,
  ADMIN_USER,
  TEST_ORG_SLUG,
} from "../../../web/e2e-playwright/helpers/env";

export {
  getApiBaseUrl,
  getComposeProject,
  getPostgresContainer,
  TEST_USER,
  ADMIN_USER,
  TEST_ORG_SLUG,
};

export function getElectronMainPath(): string {
  return resolve(__dirname, "../../out/main/index.js");
}

export function getAuthFile(): string {
  return resolve(__dirname, "../.auth/user.json");
}

export function getAdminAuthFile(): string {
  return resolve(__dirname, "../.auth/admin.json");
}

/** Isolated Electron userData dir — keeps test session separate from dev profile. */
export function getUserDataDir(): string {
  return resolve(__dirname, "../.auth/electron-userdata");
}

export function isCi(): boolean {
  return process.env.CI === "true" || process.env.CI === "1";
}
