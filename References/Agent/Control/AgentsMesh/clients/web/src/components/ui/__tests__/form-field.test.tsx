import { describe, it, expect } from "vitest";
import { render, screen } from "@/test/test-utils";
import { FormField, FormFieldGroup, FormRow } from "../form-field";
import { Input } from "../input";

describe("FormField", () => {
  it("renders label and children", () => {
    render(
      <FormField label="Email" htmlFor="email">
        <Input id="email" data-testid="email-input" />
      </FormField>
    );

    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByTestId("email-input")).toBeInTheDocument();
  });

  it("renders required indicator when required is true", () => {
    render(
      <FormField label="Name" required>
        <Input />
      </FormField>
    );

    expect(screen.getByText("*")).toBeInTheDocument();
    expect(screen.getByText("*")).toHaveClass("text-destructive");
  });

  it("renders error message", () => {
    render(
      <FormField label="Password" error="Password is required">
        <Input />
      </FormField>
    );

    const errorMessage = screen.getByRole("alert");
    expect(errorMessage).toHaveTextContent("Password is required");
    expect(errorMessage).toHaveClass("text-destructive");
  });

  it("renders hint text when no error", () => {
    render(
      <FormField label="Bio" hint="Max 200 characters">
        <Input />
      </FormField>
    );

    expect(screen.getByText("Max 200 characters")).toBeInTheDocument();
    expect(screen.getByText("Max 200 characters")).toHaveClass(
      "text-muted-foreground"
    );
  });

  it("does not render hint when error is present", () => {
    render(
      <FormField label="Bio" error="Too long" hint="Max 200 characters">
        <Input />
      </FormField>
    );

    expect(screen.queryByText("Max 200 characters")).not.toBeInTheDocument();
    expect(screen.getByText("Too long")).toBeInTheDocument();
  });

  it("applies disabled styling to label when disabled", () => {
    render(
      <FormField label="Disabled Field" disabled>
        <Input disabled />
      </FormField>
    );

    const label = screen.getByText("Disabled Field");
    expect(label).toHaveClass("opacity-50");
  });

  it("applies custom className", () => {
    const { container } = render(
      <FormField label="Custom" className="my-custom-class">
        <Input />
      </FormField>
    );

    expect(container.firstChild).toHaveClass("my-custom-class");
  });

  it("associates label with input via htmlFor", () => {
    render(
      <FormField label="Username" htmlFor="username">
        <Input id="username" />
      </FormField>
    );

    const label = screen.getByText("Username");
    expect(label).toHaveAttribute("for", "username");
  });
});

describe("FormFieldGroup", () => {
  it("renders children", () => {
    render(
      <FormFieldGroup>
        <FormField label="Field 1">
          <Input data-testid="input-1" />
        </FormField>
        <FormField label="Field 2">
          <Input data-testid="input-2" />
        </FormField>
      </FormFieldGroup>
    );

    expect(screen.getByTestId("input-1")).toBeInTheDocument();
    expect(screen.getByTestId("input-2")).toBeInTheDocument();
  });

  it("renders title and description", () => {
    render(
      <FormFieldGroup title="Personal Info" description="Enter your details">
        <FormField label="Name">
          <Input />
        </FormField>
      </FormFieldGroup>
    );

    expect(screen.getByText("Personal Info")).toBeInTheDocument();
    expect(screen.getByText("Enter your details")).toBeInTheDocument();
  });

  it("renders without title and description", () => {
    const { container } = render(
      <FormFieldGroup>
        <FormField label="Name">
          <Input />
        </FormField>
      </FormFieldGroup>
    );

    expect(container.querySelector("h3")).not.toBeInTheDocument();
  });
});

describe("FormRow", () => {
  it("renders children in a flex row", () => {
    const { container } = render(
      <FormRow>
        <FormField label="First" className="flex-1">
          <Input data-testid="first" />
        </FormField>
        <FormField label="Last" className="flex-1">
          <Input data-testid="last" />
        </FormField>
      </FormRow>
    );

    const row = container.firstChild;
    expect(row).toHaveClass("flex");
    expect(screen.getByTestId("first")).toBeInTheDocument();
    expect(screen.getByTestId("last")).toBeInTheDocument();
  });

  it("applies custom gap", () => {
    const { container } = render(
      <FormRow gap={6}>
        <Input />
        <Input />
      </FormRow>
    );

    expect(container.firstChild).toHaveClass("gap-6");
  });

  it("applies custom className", () => {
    const { container } = render(
      <FormRow className="my-row-class">
        <Input />
      </FormRow>
    );

    expect(container.firstChild).toHaveClass("my-row-class");
  });
});
