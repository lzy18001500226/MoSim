import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@/test/test-utils";
import { ImportRepositoryModal } from "../ImportRepositoryModal";
import { setupProviderMocks } from "./ImportRepositoryModal.utils";

describe("ImportRepositoryModal - Provider Type Switching", () => {
  const mockOnClose = vi.fn();
  const mockOnImported = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    setupProviderMocks();
  });

  it("should change base URL when provider type is changed to gitlab", async () => {
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Enter Manually"));

    await waitFor(() => {
      const baseUrlInput = screen.getByPlaceholderText("https://github.com") as HTMLInputElement;
      expect(baseUrlInput.value).toBe("https://github.com");
    });

    const providerSelect = document.querySelector("select") as HTMLSelectElement;
    fireEvent.change(providerSelect, { target: { value: "gitlab" } });

    await waitFor(() => {
      const baseUrlInput = screen.getByPlaceholderText("https://github.com") as HTMLInputElement;
      expect(baseUrlInput.value).toBe("https://gitlab.com");
    });
  });

  it("should change base URL when provider type is changed to gitee", async () => {
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Enter Manually"));

    const providerSelect = document.querySelector("select") as HTMLSelectElement;
    fireEvent.change(providerSelect, { target: { value: "gitee" } });

    await waitFor(() => {
      const baseUrlInput = screen.getByPlaceholderText("https://github.com") as HTMLInputElement;
      expect(baseUrlInput.value).toBe("https://gitee.com");
    });
  });

  it("should clear base URL when provider type is changed to generic", async () => {
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("Enter Manually")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Enter Manually"));

    const providerSelect = document.querySelector("select") as HTMLSelectElement;
    fireEvent.change(providerSelect, { target: { value: "generic" } });

    await waitFor(() => {
      const baseUrlInput = screen.getByPlaceholderText("https://github.com") as HTMLInputElement;
      expect(baseUrlInput.value).toBe("");
    });
  });
});
