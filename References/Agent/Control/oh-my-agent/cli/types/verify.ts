export interface VerifyCheck {
  name: string;
  status: "pass" | "fail" | "warn" | "skip";
  message?: string;
}

export interface VerifyResult {
  ok: boolean;
  agent: string;
  workspace: string;
  checks: VerifyCheck[];
  summary: {
    passed: number;
    failed: number;
    warned: number;
  };
}
