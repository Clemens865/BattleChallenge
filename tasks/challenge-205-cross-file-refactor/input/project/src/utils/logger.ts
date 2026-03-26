export interface Logger {
  debug(msg: string): void;
  info(msg: string): void;
  warn(msg: string): void;
  error(msg: string): void;
}

class ConsoleLogger implements Logger {
  debug(msg: string): void {
    console.debug(`[DEBUG] ${msg}`);
  }
  info(msg: string): void {
    console.info(`[INFO] ${msg}`);
  }
  warn(msg: string): void {
    console.warn(`[WARN] ${msg}`);
  }
  error(msg: string): void {
    console.error(`[ERROR] ${msg}`);
  }
}

export const logger: Logger = new ConsoleLogger();
