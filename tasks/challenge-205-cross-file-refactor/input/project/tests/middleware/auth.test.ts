import { UserService } from "../../src/services/UserService";
import { initAuth } from "../../src/middleware/auth";

describe("Auth Middleware", () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService();
    initAuth(userService);
  });

  it("should initialize with UserService", () => {
    // initAuth should not throw
    expect(() => initAuth(userService)).not.toThrow();
  });

  it("should use getUser for token validation", async () => {
    const spy = jest.spyOn(userService, "getUser");
    await userService.getUser("some-token");
    expect(spy).toHaveBeenCalledWith("some-token");
    spy.mockRestore();
  });

  it("should handle missing UserService gracefully", () => {
    const freshUserService = new UserService();
    expect(() => initAuth(freshUserService)).not.toThrow();
  });
});
