import { createServer } from "../src/server";
import { Application } from "express";

describe("Server", () => {
  let app: Application;

  beforeAll(() => {
    app = createServer();
  });

  it("should create an express application", () => {
    expect(app).toBeDefined();
    expect(typeof app.listen).toBe("function");
  });

  it("should have a health endpoint", (done) => {
    const request = require("supertest");
    request(app)
      .get("/health")
      .expect(200)
      .expect("Content-Type", /json/)
      .end((err: Error | null, res: any) => {
        if (err) return done(err);
        expect(res.body.status).toBe("ok");
        done();
      });
  });

  it("should mount API routes under /api", (done) => {
    const request = require("supertest");
    request(app)
      .get("/api/tasks")
      .expect(200)
      .expect("Content-Type", /json/)
      .end((err: Error | null, res: any) => {
        if (err) return done(err);
        expect(res.body).toHaveProperty("tasks");
        expect(res.body).toHaveProperty("count");
        done();
      });
  });
});
