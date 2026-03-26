import { UserService } from "../../src/services/UserService";
import { TaskService } from "../../src/services/TaskService";
import { NotificationService } from "../../src/services/NotificationService";
import { CreateUserDto, UserRole } from "../../src/models";

describe("User Flow Integration", () => {
  let userService: UserService;
  let taskService: TaskService;
  let notificationService: NotificationService;

  beforeEach(() => {
    userService = new UserService();
    taskService = new TaskService(userService);
    notificationService = new NotificationService(userService);
  });

  it("should create user and assign task", async () => {
    const userDto: CreateUserDto = {
      email: "flow@test.com",
      username: "flowuser",
      password: "password123",
    };
    const user = await userService.createUser(userDto);

    const assignee = await userService.createUser({
      email: "assignee@test.com",
      username: "assignee",
      password: "password123",
    });

    const task = await taskService.createTask(user.id, {
      title: "Test task",
      description: "Integration test",
      assigneeId: assignee.id,
    });

    expect(task.creatorId).toBe(user.id);
    expect(task.assigneeId).toBe(assignee.id);
  });

  it("should get user via UserService in task flow", async () => {
    const dto: CreateUserDto = {
      email: "verify@test.com",
      username: "verifyuser",
      password: "password123",
    };
    const user = await userService.createUser(dto);
    const fetched = await userService.getUser(user.id);
    expect(fetched).not.toBeNull();
    expect(fetched!.username).toBe("verifyuser");
  });

  it("should send notification to existing user", async () => {
    const dto: CreateUserDto = {
      email: "notif@test.com",
      username: "notifuser",
      password: "password123",
    };
    const user = await userService.createUser(dto);
    const sent = await notificationService.sendNotification(
      user.id,
      "Welcome!"
    );
    expect(sent).toBe(true);
  });

  it("should fail to notify non-existent user", async () => {
    const sent = await notificationService.sendNotification(
      "ghost-id",
      "Hello?"
    );
    expect(sent).toBe(false);
  });
});
