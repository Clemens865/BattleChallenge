import {
  createTask,
  getTask,
  getAllTasks,
  deleteTask,
  updateTask,
  connectDatabase,
  isConnected,
} from "../src/database";

describe("Database", () => {
  beforeAll(async () => {
    await connectDatabase("test://localhost:5432/test");
  });

  it("should connect successfully", () => {
    expect(isConnected()).toBe(true);
  });

  it("should create a task", () => {
    const task = createTask("Test Task", "Test description");
    expect(task).toBeDefined();
    expect(task.id).toBeDefined();
    expect(task.title).toBe("Test Task");
    expect(task.completed).toBe(false);
  });

  it("should get a task by id", () => {
    const created = createTask("Find Me", "Searchable");
    const found = getTask(created.id);
    expect(found).toBeDefined();
    expect(found!.title).toBe("Find Me");
  });

  it("should return undefined for missing task", () => {
    const result = getTask("nonexistent-id");
    expect(result).toBeUndefined();
  });

  it("should list all tasks", () => {
    const before = getAllTasks().length;
    createTask("Another", "Task");
    const after = getAllTasks().length;
    expect(after).toBe(before + 1);
  });

  it("should update a task", () => {
    const task = createTask("Update Me", "Original");
    const updated = updateTask(task.id, { completed: true });
    expect(updated).toBeDefined();
    expect(updated!.completed).toBe(true);
  });

  it("should delete a task", () => {
    const task = createTask("Delete Me", "Temporary");
    expect(deleteTask(task.id)).toBe(true);
    expect(getTask(task.id)).toBeUndefined();
  });
});
