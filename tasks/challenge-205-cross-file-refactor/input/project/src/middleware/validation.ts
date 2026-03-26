import { Request, Response, NextFunction } from "express";
import { logger } from "../utils/logger";

export function validateRequest(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  if (!req.body || typeof req.body !== "object") {
    logger.warn("Validation failed: empty or non-object body");
    res.status(400).json({ error: "Request body must be a JSON object" });
    return;
  }

  next();
}

export function validateId(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const { id } = req.params;
  if (!id || id.length < 1) {
    res.status(400).json({ error: "Invalid ID parameter" });
    return;
  }

  next();
}
