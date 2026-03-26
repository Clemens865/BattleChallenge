import express from "express";
import { getAppConfig } from "./config";
import { createServiceContainer } from "./types/ServiceContainer";
import {
  createUserRoutes,
  createTaskRoutes,
  createNotificationRoutes,
  createHealthRoutes,
} from "./routes";
import { initAuth, errorHandler } from "./middleware";
import { logger } from "./utils/logger";

export function createApp() {
  const app = express();
  const config = getAppConfig();
  const services = createServiceContainer();

  // Initialize auth middleware with UserService
  initAuth(services.userService);

  app.use(express.json());

  // Mount routes
  app.use("/api/health", createHealthRoutes());
  app.use("/api/users", createUserRoutes(services.userService));
  app.use(
    "/api/tasks",
    createTaskRoutes(services.taskService, services.userService)
  );
  app.use(
    "/api/notifications",
    createNotificationRoutes(services.notificationService, services.userService)
  );

  app.use(errorHandler);

  return { app, config, services };
}

if (require.main === module) {
  const { app, config } = createApp();
  app.listen(config.port, () => {
    logger.info(`Server running on port ${config.port}`);
  });
}
