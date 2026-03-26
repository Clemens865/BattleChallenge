import { Router, Request, Response } from "express";

export function createHealthRoutes(): Router {
  const router = Router();

  router.get("/", (_req: Request, res: Response) => {
    res.json({
      status: "ok",
      timestamp: new Date().toISOString(),
      version: "1.0.0",
    });
  });

  router.get("/ready", (_req: Request, res: Response) => {
    res.json({ ready: true });
  });

  return router;
}
