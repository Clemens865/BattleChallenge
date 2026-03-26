export interface Task {
  id: string;
  title: string;
  description: string;
  assigneeId: string;
  creatorId: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueDate: Date | null;
  createdAt: Date;
  updatedAt: Date;
}

export enum TaskStatus {
  Open = "open",
  InProgress = "in_progress",
  Review = "review",
  Done = "done",
  Cancelled = "cancelled",
}

export enum TaskPriority {
  Low = "low",
  Medium = "medium",
  High = "high",
  Critical = "critical",
}

export interface CreateTaskDto {
  title: string;
  description: string;
  assigneeId: string;
  priority?: TaskPriority;
  dueDate?: string;
}
