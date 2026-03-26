import { Task, CreateTaskDto, TaskStatus, TaskPriority } from "../models";
import { UserService } from "./UserService";
import { generateId } from "../utils/crypto";
import { logger } from "../utils/logger";

export class TaskService {
  private tasks: Map<string, Task> = new Map();
  private userService: UserService;

  constructor(userService: UserService) {
    this.userService = userService;
  }

  async createTask(creatorId: string, dto: CreateTaskDto): Promise<Task> {
    // Verify creator exists
    const creator = await this.userService.getUser(creatorId);
    if (!creator) {
      throw new Error(`Creator ${creatorId} not found`);
    }

    // Verify assignee exists
    const assignee = await this.userService.getUser(dto.assigneeId);
    if (!assignee) {
      throw new Error(`Assignee ${dto.assigneeId} not found`);
    }

    const task: Task = {
      id: generateId(),
      title: dto.title,
      description: dto.description,
      assigneeId: dto.assigneeId,
      creatorId,
      status: TaskStatus.Open,
      priority: dto.priority || TaskPriority.Medium,
      dueDate: dto.dueDate ? new Date(dto.dueDate) : null,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.tasks.set(task.id, task);
    logger.info(`TaskService: created task ${task.id}`);
    return task;
  }

  async getTask(id: string): Promise<Task | null> {
    return this.tasks.get(id) || null;
  }

  async getTasksByAssignee(userId: string): Promise<Task[]> {
    return Array.from(this.tasks.values()).filter(
      (t) => t.assigneeId === userId
    );
  }

  async deleteTask(id: string): Promise<boolean> {
    return this.tasks.delete(id);
  }
}
