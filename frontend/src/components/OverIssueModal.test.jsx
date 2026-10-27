import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import OverIssueModal from "./OverIssueModal";

describe("OverIssueModal", () => {
  const warning = { available: 20, requested: 50 };

  // Without vitest globals, Testing Library does not clean up between tests,
  // so each modal would stay in the page and duplicate buttons.
  afterEach(() => {
    cleanup();
  });

  it("shows the available and requested amounts", () => {
    render(<OverIssueModal warning={warning} onConfirm={() => {}} onCancel={() => {}} />);
    expect(screen.getByText("20")).toBeTruthy();
    expect(screen.getByText("50")).toBeTruthy();
  });

  it("calls onConfirm when the user continues", () => {
    const onConfirm = vi.fn();
    render(<OverIssueModal warning={warning} onConfirm={onConfirm} onCancel={() => {}} />);
    fireEvent.click(screen.getByTestId("over-issue-confirm"));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel and does not confirm when the user cancels", () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(<OverIssueModal warning={warning} onConfirm={onConfirm} onCancel={onCancel} />);
    fireEvent.click(screen.getByTestId("over-issue-cancel"));
    expect(onCancel).toHaveBeenCalledTimes(1);
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("renders nothing without a warning", () => {
    const { container } = render(
      <OverIssueModal warning={null} onConfirm={() => {}} onCancel={() => {}} />,
    );
    expect(container.textContent).toBe("");
  });
});
