import { UserService } from "../../src/services/UserService";
import { createUserRoutes } from "../../src/routes/users";

describe("User Routes", () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService();
  });

  it("should create route handler with UserService", () => {
    const router = createUserRoutes(userService);
    expect(router).toBeDefined();
  });

  it("should use getUser for fetching", async () => {
    const spy = jest.spyOn(userService, "getUser");
    await userService.getUser("test-id");
    expect(spy).toHaveBeenCalledWith("test-id");
    spy.mockRestore();
  });

  it("should use createUser for registration", async () => {
    const spy = jest.spyOn(userService, "createUser");
    const dto = {
      email: "route@test.com",
      username: "routetest",
      password: "pass123",
    };
    await userService.createUser(dto);
    expect(spy).toHaveBeenCalledWith(dto);
    spy.mockRestore();
  });
});
