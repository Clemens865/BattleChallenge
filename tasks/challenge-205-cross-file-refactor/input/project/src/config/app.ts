export interface AppConfig {
  port: number;
  env: string;
  corsOrigins: string[];
}

export function getAppConfig(): AppConfig {
  return {
    port: parseInt(process.env.PORT || "3000", 10),
    env: process.env.NODE_ENV || "development",
    corsOrigins: (process.env.CORS_ORIGINS || "http://localhost:3000").split(","),
  };
}
