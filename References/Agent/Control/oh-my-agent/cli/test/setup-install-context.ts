import { afterEach, beforeEach } from "vitest";
import { _resetInstallContext } from "../platform/install-context.js";

beforeEach(() => {
  _resetInstallContext();
});

afterEach(() => {
  _resetInstallContext();
});
