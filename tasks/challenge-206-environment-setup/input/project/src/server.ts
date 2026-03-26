import express, { Application } from "express";
import { createRoutes } from "./routes";

export function createServer(): Application {
  const app = express();

  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Health check
  app.get("/health", (_req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  // Mount API routes
  app.use("/api", createRoutes());

  // Error handler
  app.use(
    (
      err: Error,
      _req: express.Request,
      res: express.Response,
      _next: express.NextFunction
    ) => {
      console.error("Unhandled error:", err.message);
      res.status(500).json({ error: "Internal Server Error" });
    }
  );

  return app;
}
