import { Request, Response, NextFunction } from "express";
import { UserService } from "../services/UserService";
import { logger } from "../utils/logger";

// Singleton reference set by the app bootstrap
let userService: UserService;

export function initAuth(service: UserService): void {
  userService = service;
}

export async function requireAuth(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  const token = req.headers["x-user-id"] as string | undefined;
  if (!token) {
    res.status(401).json({ error: "Missing x-user-id header" });
    return;
  }

  const user = await userService.getUser(token);
  if (!user || !user.isActive) {
    logger.warn(`Auth failed for token ${token}`);
    res.status(403).json({ error: "Forbidden" });
    return;
  }

  next();
}
