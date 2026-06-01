import {
  emitEventWithMemory,
  getActiveSid,
  readEvents,
  readIndex,
} from "./events.js";

export interface RequiredDecision {
  subject: string;
  description: string;
}

export type RequiredDecisionTable = Record<
  string,
  Record<string, RequiredDecision[]>
>;

export const REQUIRED_DECISIONS: RequiredDecisionTable = {
  ultrawork: {
    "plan-approved": [
      {
        subject: "ultrawork.plan-approved",
        description:
          "Architecture and plan decision captured after PLAN_GATE approval.",
      },
    ],
    "impl-plan-locked": [
      {
        subject: "ultrawork.impl-plan-locked",
        description:
          "Task decomposition and implementation scope locked before IMPL work.",
      },
    ],
    "refine-outcome": [
      {
        subject: "ultrawork.refine-outcome",
        description:
          "REFINE experiment outcome captured before shipping or skipping refinement.",
      },
    ],
  },
  orchestrate: {
    "fanout-strategy": [
      {
        subject: "orchestrate.fanout-strategy",
        description:
          "Parallel agent fan-out strategy captured after the plan is loaded.",
      },
    ],
    "qa-verdict": [
      {
        subject: "orchestrate.qa-verdict",
        description:
          "Verification gate verdict captured after completed agents are checked.",
      },
    ],
  },
  work: {
    "remediation-choice": [
      {
        subject: "work.remediation-choice",
        description:
          "QA remediation decision captured before ignored or fixed findings are accepted.",
      },
    ],
  },
};

export interface DecisionVerificationResult {
  sid: string;
  workflow: string;
  checkpoint: string;
  ok: boolean;
  required: RequiredDecision[];
  presentSubjects: string[];
  missing: RequiredDecision[];
}

export function listRequiredDecisionCheckpoints(
  workflow?: string,
): RequiredDecisionTable {
  if (!workflow) return REQUIRED_DECISIONS;
  return { [workflow]: REQUIRED_DECISIONS[workflow] ?? {} };
}

export function resolveDecisionVerifierSid(args: {
  projectDir: string;
  sid?: string;
  category?: string;
}): string {
  if (args.sid) return args.sid;
  const sid = getActiveSid(readIndex(args.projectDir), args.category ?? "main");
  if (!sid) {
    throw new Error(
      "No active L1 session found. Pass --sid or run a workflow first.",
    );
  }
  return sid;
}

export async function verifyRequiredDecisions(args: {
  projectDir: string;
  sid: string;
  workflow: string;
  checkpoint: string;
  emitMissing?: boolean;
}): Promise<DecisionVerificationResult> {
  const required = REQUIRED_DECISIONS[args.workflow]?.[args.checkpoint];
  if (!required) {
    throw new Error(
      `Unknown required decision checkpoint: ${args.workflow}/${args.checkpoint}`,
    );
  }

  const events = readEvents(args.projectDir, args.sid);
  const presentSubjects = events
    .filter((event) => event.kind === "decision.made")
    .map((event) => event.payload?.subject)
    .filter((subject): subject is string => typeof subject === "string");
  const present = new Set(presentSubjects);
  const missing = required.filter((decision) => !present.has(decision.subject));
  const result: DecisionVerificationResult = {
    sid: args.sid,
    workflow: args.workflow,
    checkpoint: args.checkpoint,
    ok: missing.length === 0,
    required,
    presentSubjects,
    missing,
  };

  if (!result.ok && args.emitMissing !== false) {
    await emitEventWithMemory(args.projectDir, args.sid, {
      kind: "decision.missing",
      payload: {
        workflow: args.workflow,
        checkpoint: args.checkpoint,
        missing,
        remediation:
          "Emit the required decision.made event with oma_emit, then rerun this verifier.",
      },
    });
  }

  return result;
}
