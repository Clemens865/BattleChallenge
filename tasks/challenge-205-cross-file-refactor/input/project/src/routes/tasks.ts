import { Router, Request, Response } from "express";
import { TaskService } from "../services/TaskService";
import { UserService } from "../services/UserService";
import { CreateTaskDto } from "../models";
import { requireAuth } from "../middleware/auth";
import { logger } from "../utils/logger";

export function createTaskRoutes(
  taskService: TaskService,
  userService: UserService
): Router {
  const router = Router();

  router.post("/", requireAuth, async (req: Request, res: Response) => {
    try {
      const creatorId = req.headers["x-user-id"] as string;
      const dto: CreateTaskDto = req.body;
      const task = await taskService.createTask(creatorId, dto);
      logger.info(`Route: created task ${task.id}`);
      res.status(201).json(task);
    } catch (err: any) {
      res.status(400).json({ error: err.message });
    }
  });

  router.get("/:id", async (req: Request, res: Response) => {
    const task = await taskService.getTask(req.params.id);
    if (!task) {
      return res.status(404).json({ error: "Task not found" });
    }
    res.json(task);
  });

  router.get("/user/:userId", async (req: Request, res: Response) => {
    // Verify the user exists before listing tasks
    const user = await userService.getUser(req.params.userId);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    const tasks = await taskService.getTasksByAssignee(req.params.userId);
    res.json(tasks);
  });

  router.delete("/:id", requireAuth, async (req: Request, res: Response) => {
    const deleted = await taskService.deleteTask(req.params.id);
    res.json({ deleted });
  });

  return router;
}
