import { v4 as uuidv4 } from "uuid";

export interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  createdAt: Date;
}

// In-memory store (simulating a database)
const tasks: Map<string, Task> = new Map();
let connected = false;

export async function connectDatabase(url: string): Promise<void> {
  // Simulate async database connection
  console.log(`Connecting to: ${url}`);
  await new Promise((resolve) => setTimeout(resolve, 100));
  connected = true;
  console.log("Database connected successfully");
}

export function isConnected(): boolean {
  return connected;
}

export function createTask(title: string, description: string): Task {
  const task: Task = {
    id: uuidv4(),
    title,
    description,
    completed: false,
    createdAt: new Date(),
  };
  tasks.set(task.id, task);
  return task;
}

export function getTask(id: string): Task | undefined {
  return tasks.get(id);
}

export function getAllTasks(): Task[] {
  return Array.from(tasks.values());
}

export function deleteTask(id: string): boolean {
  return tasks.delete(id);
}

export function updateTask(
  id: string,
  updates: Partial<Pick<Task, "title" | "description" | "completed">>
): Task | undefined {
  const task = tasks.get(id);
  if (!task) return undefined;
  const updated = { ...task, ...updates };
  tasks.set(id, updated);
  return updated;
}
