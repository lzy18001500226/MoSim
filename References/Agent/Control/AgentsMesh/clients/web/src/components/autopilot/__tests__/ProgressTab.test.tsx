import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProgressTab } from "../panel/ProgressTab";
import type { AutopilotThinking } from "@/stores/autopilot";

// Helper to create mock thinking data with progress
const createMockThinking = (
  progress: AutopilotThinking["progress"] = undefined
): AutopilotThinking => ({
  autopilot_controller_key: "test-autopilot-key",
  iteration: 1,
  decision_type: "CONTINUE",
  reasoning: "Test reasoning",
  confidence: 0.85,
  action: undefined,
  progress,
  help_request: undefined,
});

describe("ProgressTab", () => {
  describe("empty state", () => {
    it("should show no progress message when thinking is null", () => {
      render(<ProgressTab thinking={null} />);
      expect(screen.getByText("No progress data available")).toBeInTheDocument();
    });

    it("should show no progress message when progress is undefined", () => {
      render(<ProgressTab thinking={createMockThinking(undefined)} />);
      expect(screen.getByText("No progress data available")).toBeInTheDocument();
    });
  });

  describe("progress summary", () => {
    it("should display progress summary", () => {
      const thinking = createMockThinking({
        summary: "Working on file creation",
        percent: 50,
        completed_steps: [],
        remaining_steps: [],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("Working on file creation")).toBeInTheDocument();
    });

    it("should display default summary when not provided", () => {
      const thinking = createMockThinking({
        summary: "",
        percent: 30,
        completed_steps: [],
        remaining_steps: [],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("Task Progress")).toBeInTheDocument();
    });
  });

  describe("progress percentage", () => {
    it("should display progress percentage when > 0", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 75,
        completed_steps: [],
        remaining_steps: [],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("75%")).toBeInTheDocument();
    });

    it("should not display percentage when 0", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 0,
        completed_steps: [],
        remaining_steps: [],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.queryByText("0%")).not.toBeInTheDocument();
    });

    it("should render progress bar when percent > 0", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 60,
        completed_steps: [],
        remaining_steps: [],
      });
      const { container } = render(<ProgressTab thinking={thinking} />);
      // Progress component renders with role="progressbar"
      expect(container.querySelector('[role="progressbar"]')).toBeInTheDocument();
    });
  });

  describe("completed steps", () => {
    it("should display completed steps", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 50,
        completed_steps: ["Step 1 done", "Step 2 done"],
        remaining_steps: [],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("Step 1 done")).toBeInTheDocument();
      expect(screen.getByText("Step 2 done")).toBeInTheDocument();
    });

    it("should display completed steps count", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 50,
        completed_steps: ["Step 1", "Step 2", "Step 3"],
        remaining_steps: [],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("Completed (3)")).toBeInTheDocument();
    });

    it("should not display completed section when empty", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 0,
        completed_steps: [],
        remaining_steps: ["Step 1"],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.queryByText(/Completed/)).not.toBeInTheDocument();
    });
  });

  describe("remaining steps", () => {
    it("should display remaining steps", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 30,
        completed_steps: [],
        remaining_steps: ["Remaining 1", "Remaining 2"],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("Remaining 1")).toBeInTheDocument();
      expect(screen.getByText("Remaining 2")).toBeInTheDocument();
    });

    it("should display remaining steps count", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 30,
        completed_steps: [],
        remaining_steps: ["Step 1", "Step 2"],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("Remaining (2)")).toBeInTheDocument();
    });

    it("should not display remaining section when empty", () => {
      const thinking = createMockThinking({
        summary: "Test",
        percent: 100,
        completed_steps: ["Done"],
        remaining_steps: [],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.queryByText(/Remaining/)).not.toBeInTheDocument();
    });
  });

  describe("both completed and remaining steps", () => {
    it("should display both sections in two columns", () => {
      const thinking = createMockThinking({
        summary: "In progress",
        percent: 60,
        completed_steps: ["Done 1", "Done 2"],
        remaining_steps: ["Todo 1", "Todo 2"],
      });
      render(<ProgressTab thinking={thinking} />);
      expect(screen.getByText("Completed (2)")).toBeInTheDocument();
      expect(screen.getByText("Remaining (2)")).toBeInTheDocument();
      expect(screen.getByText("Done 1")).toBeInTheDocument();
      expect(screen.getByText("Todo 1")).toBeInTheDocument();
    });
  });
});
