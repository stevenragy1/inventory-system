import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import ItemFormModal from "./ItemFormModal";
import { api } from "../api/client";

const categories = [{ id: 1, name: "Cups" }];

function renderForm(overrides = {}) {
  const props = {
    show: true,
    categories,
    onSaved: vi.fn(),
    onCancel: vi.fn(),
    ...overrides,
  };
  render(<ItemFormModal {...props} />);
  return props;
}

describe("ItemFormModal", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("shows field errors and does not call the API when the form is empty", async () => {
    const create = vi.spyOn(api, "createItem");
    renderForm();
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));
    expect(await screen.findByText("SKU is required.")).toBeTruthy();
    expect(screen.getByText("Choose a category.")).toBeTruthy();
    expect(create).not.toHaveBeenCalled();
  });

  it("sends the item with the price converted to cents", async () => {
    const created = { id: 9, sku: "CUP-CER-004" };
    const create = vi.spyOn(api, "createItem").mockResolvedValue(created);
    const props = renderForm();

    fireEvent.change(screen.getByLabelText("SKU"), { target: { value: "CUP-CER-004" } });
    fireEvent.change(screen.getByLabelText("Name"), { target: { value: "Espresso cup" } });
    fireEvent.change(screen.getByLabelText("Category"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Unit cost"), { target: { value: "2.50" } });
    fireEvent.change(screen.getByLabelText("Reorder level"), { target: { value: "100" } });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() => expect(props.onSaved).toHaveBeenCalledWith(created));
    expect(create).toHaveBeenCalledWith({
      sku: "CUP-CER-004",
      name: "Espresso cup",
      category_id: 1,
      unit_cost_cents: 250,
      reorder_level: 100,
    });
  });

  it("shows the server message when the SKU already exists", async () => {
    const { ApiError } = await import("../api/client");
    vi.spyOn(api, "createItem").mockRejectedValue(
      new ApiError(409, { message: "SKU 'CUP-CER-001' already exists." }),
    );
    renderForm();

    fireEvent.change(screen.getByLabelText("SKU"), { target: { value: "CUP-CER-001" } });
    fireEvent.change(screen.getByLabelText("Name"), { target: { value: "Dup" } });
    fireEvent.change(screen.getByLabelText("Category"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Unit cost"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Reorder level"), { target: { value: "1" } });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(await screen.findByText("SKU 'CUP-CER-001' already exists.")).toBeTruthy();
  });
});
