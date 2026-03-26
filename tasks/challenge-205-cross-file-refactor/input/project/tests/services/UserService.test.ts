import { UserService } from "../../src/services/UserService";
import { CreateUserDto, UserRole } from "../../src/models";

describe("UserService", () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService();
  });

  it("should create a user", async () => {
    const dto: CreateUserDto = {
      email: "test@example.com",
      username: "testuser",
      password: "password123",
    };
    const user = await userService.createUser(dto);
    expect(user.email).toBe(dto.email);
    expect(user.role).toBe(UserRole.Member);
  });

  it("should get a user by id", async () => {
    const dto: CreateUserDto = {
      email: "find@example.com",
      username: "findme",
      password: "password123",
    };
    const created = await userService.createUser(dto);
    const found = await userService.getUser(created.id);
    expect(found).not.toBeNull();
    expect(found!.email).toBe("find@example.com");
  });

  it("should return null for non-existent user", async () => {
    const result = await userService.getUser("non-existent-id");
    expect(result).toBeNull();
  });

  it("should delete a user", async () => {
    const dto: CreateUserDto = {
      email: "delete@example.com",
      username: "deleteme",
      password: "password123",
    };
    const user = await userService.createUser(dto);
    const deleted = await userService.deleteUser(user.id);
    expect(deleted).toBe(true);
    const found = await userService.getUser(user.id);
    expect(found).toBeNull();
  });

  it("should not create duplicate email", async () => {
    const dto: CreateUserDto = {
      email: "dup@example.com",
      username: "user1",
      password: "password123",
    };
    await userService.createUser(dto);
    await expect(
      userService.createUser({ ...dto, username: "user2" })
    ).rejects.toThrow();
  });
});
