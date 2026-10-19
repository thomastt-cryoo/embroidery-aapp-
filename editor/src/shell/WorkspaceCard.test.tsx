// @vitest-environment jsdom
import { afterEach, expect, it } from "vitest";
import { act, cleanup, fireEvent, screen, waitFor, within } from "@testing-library/react";
import { lastEditor, renderEditor, testDesign } from "../test/helpers";
import { EditorShell } from "./EditorShell";
import { hoopViewStore } from "../state/hoopViewStore";

afterEach(cleanup);

it("keeps the hoop picker accessible while editing a selected shape or lettering", async () => {
  renderEditor(<EditorShell />, { design: testDesign() });
  await waitFor(() => expect(lastEditor?.state.planResult).not.toBeNull(), { timeout: 20_000 });
  act(() => lastEditor!.actions.setSelection(["f1"]));
  const workspace = screen.getByRole("region", { name: "Hoop and workspace" });
  fireEvent.click(within(workspace).getAllByRole("button", { name: /^Hoop:/ })[0]);
  expect(hoopViewStore.getState().pickerOpen).toBe(true);
  act(() => hoopViewStore.setState({ pickerOpen: false }));
  act(() => lastEditor!.actions.setTool("text"));
  expect(within(workspace).getAllByRole("button", { name: /^Hoop:/ })[0]).toBeTruthy();
});

it("puts generation before advanced controls while retaining every option", () => {
  renderEditor(<EditorShell />);
  const advanced = screen.getByText("Advanced generation settings").closest("details")!;
  expect(advanced.open).toBe(false);
  expect((screen.getByRole("button", { name: "Generate stitches" }) as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByText("Advanced generation settings"));
  advanced.open = true; // jsdom does not implement summary's native toggle.
  expect(screen.getByLabelText("Thread brand")).toBeTruthy();
  expect(screen.getByLabelText("Minimum region size")).toBeTruthy();
  expect(screen.getByLabelText("Use my threads")).toBeTruthy();
});

it("opens saved or drawn designs in editing controls and selects their shapes for resizing", async () => {
  renderEditor(<EditorShell />, { design: testDesign() });
  await waitFor(() => expect(lastEditor?.state.planResult).not.toBeNull(), { timeout: 20_000 });
  const panel = screen.getByRole("region", { name: "Edit the current design" });
  fireEvent.click(within(panel).getByRole("button", { name: "Select all to resize" }));
  expect(lastEditor!.state.selectedIds).toEqual(["f1", "r1", "s1"]);
  expect(screen.getByRole("region", { name: "Hoop and workspace" })).toBeTruthy();
});
