import { UserService } from "../services/UserService";
import { TaskService } from "../services/TaskService";
import { NotificationService } from "../services/NotificationService";

/**
 * Dependency injection container holding all service instances.
 */
export interface ServiceContainer {
  userService: UserService;
  taskService: TaskService;
  notificationService: NotificationService;
}

export function createServiceContainer(): ServiceContainer {
  const userService = new UserService();
  const taskService = new TaskService(userService);
  const notificationService = new NotificationService(userService);

  return { userService, taskService, notificationService };
}
