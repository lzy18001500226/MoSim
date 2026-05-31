import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@/test/test-utils";
import userEvent from "@testing-library/user-event";
import { ImportRepositoryModal } from "../ImportRepositoryModal";
import { setupProviderMocks } from "./ImportRepositoryModal.utils";

describe("ImportRepositoryModal - Manual Entry", () => {
  const mockOnClose = vi.fn();
  const mockOnImported = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    setupProviderMocks();
  });

  it("should navigate to manual entry step", async () => {
    const user = userEvent.setup();
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Enter Manually"));

    await waitFor(() => {
      expect(screen.getByText(/Clone URL/)).toBeInTheDocument();
    });
  });

  it("should show provider type dropdown in manual entry", async () => {
    const user = userEvent.setup();
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Enter Manually"));

    await waitFor(() => {
      expect(screen.getByText("Provider Type")).toBeInTheDocument();
    });
  });

  it("should update base URL when provider type changes", async () => {
    const user = userEvent.setup();
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Enter Manually"));

    await waitFor(() => {
      const baseUrlInput = screen.getByPlaceholderText("https://github.com") as HTMLInputElement;
      expect(baseUrlInput.value).toBe("https://github.com");
    });
  });

  it("should allow filling manual entry fields", async () => {
    const user = userEvent.setup();
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Enter Manually"));

    await waitFor(() => {
      expect(screen.getByPlaceholderText("https://github.com/org/repo.git")).toBeInTheDocument();
    });

    const cloneUrlInput = screen.getByPlaceholderText("https://github.com/org/repo.git");
    const nameInput = screen.getByPlaceholderText("my-project");
    const slugInput = screen.getByPlaceholderText("org/my-project");

    await user.clear(cloneUrlInput);
    await user.type(cloneUrlInput, "https://github.com/test/repo.git");
    await user.clear(nameInput);
    await user.type(nameInput, "test-repo");
    await user.clear(slugInput);
    await user.type(slugInput, "test/repo");
  });

  it("should show error when continue is clicked without required fields", async () => {
    const user = userEvent.setup();
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Enter Manually"));

    await waitFor(() => {
      expect(screen.getByText("Continue")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Continue"));

    await waitFor(() => {
      expect(screen.getByText(/Please fill in all required fields/)).toBeInTheDocument();
    });
  });

  it("should navigate to confirm step after filling manual entry", async () => {
    const user = userEvent.setup();
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Enter Manually"));

    await waitFor(() => {
      expect(screen.getByPlaceholderText("https://github.com/org/repo.git")).toBeInTheDocument();
    });

    const cloneUrlInput = screen.getByPlaceholderText("https://github.com/org/repo.git");
    const nameInput = screen.getByPlaceholderText("my-project");
    const slugInput = screen.getByPlaceholderText("org/my-project");

    await user.clear(cloneUrlInput);
    await user.type(cloneUrlInput, "https://github.com/test/repo.git");
    await user.clear(nameInput);
    await user.type(nameInput, "test-repo");
    await user.clear(slugInput);
    await user.type(slugInput, "test/repo");

    await user.click(screen.getByText("Continue"));

    await waitFor(() => {
      expect(screen.getByText("Confirm Import")).toBeInTheDocument();
    });
  });
});
