import { Router, Request, Response } from "express";
import { UserService } from "../services/UserService";
import { CreateUserDto, UpdateUserDto } from "../models";
import { validateRequest } from "../middleware/validation";
import { logger } from "../utils/logger";

export function createUserRoutes(userService: UserService): Router {
  const router = Router();

  router.get("/:id", async (req: Request, res: Response) => {
    const user = await userService.getUser(req.params.id);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    const { passwordHash, ...safeUser } = user;
    res.json(safeUser);
  });

  router.post("/", validateRequest, async (req: Request, res: Response) => {
    try {
      const dto: CreateUserDto = req.body;
      const user = await userService.createUser(dto);
      logger.info(`Route: created user ${user.id}`);
      res.status(201).json(user);
    } catch (err: any) {
      res.status(400).json({ error: err.message });
    }
  });

  router.put("/:id", validateRequest, async (req: Request, res: Response) => {
    const dto: UpdateUserDto = req.body;
    const user = await userService.updateUser(req.params.id, dto);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    res.json(user);
  });

  router.delete("/:id", async (req: Request, res: Response) => {
    const deleted = await userService.deleteUser(req.params.id);
    res.json({ deleted });
  });

  router.get("/", async (_req: Request, res: Response) => {
    const users = await userService.listUsers();
    res.json(users);
  });

  return router;
}
