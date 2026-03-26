import { Router, Request, Response } from "express";
import { NotificationService } from "../services/NotificationService";
import { UserService } from "../services/UserService";
import { requireAuth } from "../middleware/auth";

export function createNotificationRoutes(
  notificationService: NotificationService,
  userService: UserService
): Router {
  const router = Router();

  router.get("/:userId", requireAuth, async (req: Request, res: Response) => {
    const user = await userService.getUser(req.params.userId);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    const notifications =
      await notificationService.getNotificationsForUser(req.params.userId);
    res.json(notifications);
  });

  router.post("/send", requireAuth, async (req: Request, res: Response) => {
    const { userId, message } = req.body;
    const sent = await notificationService.sendNotification(userId, message);
    res.json({ sent });
  });

  return router;
}
