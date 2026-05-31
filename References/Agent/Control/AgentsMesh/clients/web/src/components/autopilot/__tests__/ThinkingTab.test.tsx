import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ThinkingTab } from "../panel/ThinkingTab";
import type { AutopilotThinking } from "@/stores/autopilot";

// Helper to create mock thinking data
const createMockThinking = (overrides: Partial<AutopilotThinking> = {}): AutopilotThinking => ({
  autopilot_controller_key: "test-autopilot-key",
  iteration: 1,
  decision_type: "CONTINUE",
  reasoning: "Test reasoning text",
  confidence: 0.85,
  action: undefined,
  progress: undefined,
  help_request: undefined,
  ...overrides,
});

describe("ThinkingTab", () => {
  describe("empty state", () => {
    it("should show waiting message when thinking is null", () => {
      render(<ThinkingTab thinking={null} />);
      expect(screen.getByText("Waiting for Control Agent...")).toBeInTheDocument();
    });
  });

  describe("decision type display", () => {
    it("should display Continue badge for CONTINUE decision", () => {
      render(<ThinkingTab thinking={createMockThinking({ decision_type: "CONTINUE" })} />);
      expect(screen.getByText("Continue")).toBeInTheDocument();
    });

    it("should display Completed badge for TASK_COMPLETED decision", () => {
      render(<ThinkingTab thinking={createMockThinking({ decision_type: "TASK_COMPLETED" })} />);
      expect(screen.getByText("Completed")).toBeInTheDocument();
    });

    it("should display Need Help badge for NEED_HUMAN_HELP decision", () => {
      render(<ThinkingTab thinking={createMockThinking({ decision_type: "NEED_HUMAN_HELP" })} />);
      expect(screen.getByText("Need Help")).toBeInTheDocument();
    });

    it("should display Give Up badge for GIVE_UP decision", () => {
      render(<ThinkingTab thinking={createMockThinking({ decision_type: "GIVE_UP" })} />);
      expect(screen.getByText("Give Up")).toBeInTheDocument();
    });

    it("should display Continue badge for lowercase continue", () => {
      render(<ThinkingTab thinking={createMockThinking({ decision_type: "continue" })} />);
      expect(screen.getByText("Continue")).toBeInTheDocument();
    });
  });

  describe("iteration and confidence display", () => {
    it("should display iteration number", () => {
      render(<ThinkingTab thinking={createMockThinking({ iteration: 5 })} />);
      expect(screen.getByText("Iteration #5")).toBeInTheDocument();
    });

    it("should display confidence percentage when > 0", () => {
      render(<ThinkingTab thinking={createMockThinking({ confidence: 0.75 })} />);
      expect(screen.getByText("Confidence: 75%")).toBeInTheDocument();
    });

    it("should not display confidence when 0", () => {
      render(<ThinkingTab thinking={createMockThinking({ confidence: 0 })} />);
      expect(screen.queryByText(/Confidence:/)).not.toBeInTheDocument();
    });

    it("should round confidence percentage correctly", () => {
      render(<ThinkingTab thinking={createMockThinking({ confidence: 0.876 })} />);
      expect(screen.getByText("Confidence: 88%")).toBeInTheDocument();
    });
  });

  describe("reasoning display", () => {
    it("should display reasoning text", () => {
      const reasoning = "This is the control agent reasoning text";
      render(<ThinkingTab thinking={createMockThinking({ reasoning })} />);
      expect(screen.getByText(reasoning)).toBeInTheDocument();
    });

    it("should display Reasoning label", () => {
      render(<ThinkingTab thinking={createMockThinking()} />);
      expect(screen.getByText("Reasoning")).toBeInTheDocument();
    });
  });

  describe("action display", () => {
    it("should display action when present", () => {
      const thinking = createMockThinking({
        action: {
          type: "send_input",
          content: "echo hello",
          reason: "Testing command",
        },
      });
      render(<ThinkingTab thinking={thinking} />);
      expect(screen.getByText("Sending Input")).toBeInTheDocument();
      expect(screen.getByText("echo hello")).toBeInTheDocument();
      expect(screen.getByText("Testing command")).toBeInTheDocument();
    });

    it("should display observe action", () => {
      const thinking = createMockThinking({
        action: {
          type: "observe",
          content: "",
          reason: "Checking terminal state",
        },
      });
      render(<ThinkingTab thinking={thinking} />);
      expect(screen.getByText("Observing")).toBeInTheDocument();
    });

    it("should display wait action", () => {
      const thinking = createMockThinking({
        action: {
          type: "wait",
          content: "",
          reason: "Waiting for process",
        },
      });
      render(<ThinkingTab thinking={thinking} />);
      expect(screen.getByText("Waiting")).toBeInTheDocument();
    });

    it("should not display action section when action is undefined", () => {
      render(<ThinkingTab thinking={createMockThinking({ action: undefined })} />);
      expect(screen.queryByText("Sending Input")).not.toBeInTheDocument();
      expect(screen.queryByText("Observing")).not.toBeInTheDocument();
    });
  });

  describe("help request display", () => {
    it("should display help request when present", () => {
      const thinking = createMockThinking({
        decision_type: "NEED_HUMAN_HELP",
        help_request: {
          reason: "Permission denied error",
          context: "Installing npm packages",
          terminal_excerpt: "npm ERR! EACCES",
          suggestions: [],
        },
      });
      render(<ThinkingTab thinking={thinking} />);
      expect(screen.getByText("Help Needed")).toBeInTheDocument();
      expect(screen.getByText("Permission denied error")).toBeInTheDocument();
      expect(screen.getByText("Context: Installing npm packages")).toBeInTheDocument();
      expect(screen.getByText("npm ERR! EACCES")).toBeInTheDocument();
    });

    it("should display help request without context", () => {
      const thinking = createMockThinking({
        help_request: {
          reason: "Need user input",
          context: "",
          terminal_excerpt: "",
          suggestions: [],
        },
      });
      render(<ThinkingTab thinking={thinking} />);
      expect(screen.getByText("Help Needed")).toBeInTheDocument();
      expect(screen.getByText("Need user input")).toBeInTheDocument();
      expect(screen.queryByText(/Context:/)).not.toBeInTheDocument();
    });

    it("should display help request without terminal excerpt", () => {
      const thinking = createMockThinking({
        help_request: {
          reason: "Needs approval",
          context: "Deleting files",
          terminal_excerpt: "",
          suggestions: [],
        },
      });
      render(<ThinkingTab thinking={thinking} />);
      expect(screen.getByText("Help Needed")).toBeInTheDocument();
      expect(screen.queryByRole("code")).not.toBeInTheDocument();
    });

    it("should not display help request when undefined", () => {
      render(<ThinkingTab thinking={createMockThinking({ help_request: undefined })} />);
      expect(screen.queryByText("Help Needed")).not.toBeInTheDocument();
    });
  });
});
