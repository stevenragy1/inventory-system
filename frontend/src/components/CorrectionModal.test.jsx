import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import CorrectionModal from "./CorrectionModal";
import { api } from "../api/client";

const alert = {
  item_id: 5, location_id: 2, sku: "BTL-GLS-002",
  location: "Showroom", quantity: -30,
};

describe("CorrectionModal", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("pre-fills the change needed to reach zero", () => {
    render(<CorrectionModal alert={alert} onSaved={() => {}} onCancel={() => {}} />);
    expect(screen.getByLabelText("Change (+ or −)").value).toBe("30");
  });

  it("sends an ADJUST for the item and location, then reports saved", async () => {
    const adjust = vi.spyOn(api, "adjust").mockResolvedValue({ quantity: 0 });
    const onSaved = vi.fn();
    render(<CorrectionModal alert={alert} onSaved={onSaved} onCancel={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: "Record correction" }));
    await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1));
    expect(adjust).toHaveBeenCalledWith({
      item_id: 5, location_id: 2, delta: 30, reason: "Stock count correction",
    });
  });

  it("refuses a zero change without calling the API", async () => {
    const adjust = vi.spyOn(api, "adjust");
    render(<CorrectionModal alert={alert} onSaved={() => {}} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText("Change (+ or −)"), { target: { value: "0" } });
    fireEvent.click(screen.getByRole("button", { name: "Record correction" }));
    expect(await screen.findByText("Enter a whole number that is not zero.")).toBeTruthy();
    expect(adjust).not.toHaveBeenCalled();
  });
});
