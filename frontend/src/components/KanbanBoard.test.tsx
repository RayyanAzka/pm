import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";

const mockFetch = vi.fn();

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    mockFetch.mockImplementation(async (url: RequestInfo | URL, options?: RequestInit) => {
      if (url === "/api/users/user/board" && (!options || options.method !== "PUT")) {
        return {
          ok: true,
          json: async () => initialData,
        } as Response;
      }

      if (url === "/api/users/user/board" && options?.method === "PUT") {
        return {
          ok: true,
          json: async () => JSON.parse(String(options.body)),
        } as Response;
      }

      return {
        ok: true,
        json: async () => initialData,
      } as Response;
    });
    global.fetch = mockFetch as typeof fetch;
  });

  afterEach(() => {
    mockFetch.mockReset();
  });

  it("loads the board from the backend API", async () => {
    render(<KanbanBoard />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith("/api/users/user/board");
    });
    expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    await waitFor(() => expect(screen.getAllByTestId(/column-/i)).toHaveLength(5));

    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    await waitFor(() => expect(screen.getAllByTestId(/column-/i)).toHaveLength(5));

    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});
