import { Router, Request, Response } from "express";
import {
  createTask,
  getTask,
  getAllTasks,
  deleteTask,
  updateTask,
} from "./database";

export function createRoutes(): Router {
  const router = Router();

  // Create a task
  router.post("/tasks", (req: Request, res: Response) => {
    const { title, description } = req.body;
    if (!title) {
      return res.status(400).json({ error: "Title is required" });
    }
    const task = createTask(title, description || "");
    res.status(201).json(task);
  });

  // Get all tasks
  router.get("/tasks", (_req: Request, res: Response) => {
    const tasks = getAllTasks();
    res.json({ tasks, count: tasks.length });
  });

  // Get single task
  router.get("/tasks/:id", (req: Request, res: Response) => {
    const task = getTask(req.params.id);
    if (!task) {
      return res.status(404).json({ error: "Task not found" });
    }
    res.json(task);
  });

  // Update a task
  router.patch("/tasks/:id", (req: Request, res: Response) => {
    const task = updateTask(req.params.id, req.body);
    if (!task) {
      return res.status(404).json({ error: "Task not found" });
    }
    res.json(task);
  });

  // Delete a task
  router.delete("/tasks/:id", (req: Request, res: Response) => {
    const deleted = deleteTask(req.params.id);
    if (!deleted) {
      return res.status(404).json({ error: "Task not found" });
    }
    res.status(204).send();
  });

  return router;
}
