import { UserService } from "./UserService";
import { logger } from "../utils/logger";

export interface Notification {
  id: string;
  userId: string;
  message: string;
  read: boolean;
  createdAt: Date;
}

export class NotificationService {
  private notifications: Notification[] = [];
  private userService: UserService;

  constructor(userService: UserService) {
    this.userService = userService;
  }

  async sendNotification(userId: string, message: string): Promise<boolean> {
    const user = await this.userService.getUser(userId);
    if (!user) {
      logger.warn(`Cannot notify non-existent user ${userId}`);
      return false;
    }

    this.notifications.push({
      id: `notif-${Date.now()}`,
      userId,
      message,
      read: false,
      createdAt: new Date(),
    });
    logger.info(`Notification sent to user ${userId}`);
    return true;
  }

  async getNotificationsForUser(userId: string): Promise<Notification[]> {
    return this.notifications.filter((n) => n.userId === userId);
  }
}
