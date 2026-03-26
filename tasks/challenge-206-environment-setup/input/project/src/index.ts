import { createServer } from "./server";
import { connectDatabase } from "./database";
import dotenv from "dotenv";

dotenv.config();

const PORT = parseInt(process.env.PORT || "3000", 10);
const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
  console.error("DATABASE_URL environment variable is required");
  process.exit(1);
}

async function main(): Promise<void> {
  console.log("Connecting to database...");
  await connectDatabase(DATABASE_URL!);

  const app = createServer();
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
