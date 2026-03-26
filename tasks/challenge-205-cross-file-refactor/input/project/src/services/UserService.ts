import { User, CreateUserDto, UpdateUserDto, UserRole } from "../models";
import { hashPassword, generateId } from "../utils/crypto";
import { logger } from "../utils/logger";

export class UserService {
  private users: Map<string, User> = new Map();

  async getUser(id: string): Promise<User | null> {
    logger.debug(`UserService.getUser called with id=${id}`);
    return this.users.get(id) || null;
  }

  async getUserByEmail(email: string): Promise<User | null> {
    for (const user of this.users.values()) {
      if (user.email === email) return user;
    }
    return null;
  }

  async createUser(dto: CreateUserDto): Promise<User> {
    const existing = await this.getUserByEmail(dto.email);
    if (existing) {
      throw new Error(`User with email ${dto.email} already exists`);
    }

    const user: User = {
      id: generateId(),
      email: dto.email,
      username: dto.username,
      passwordHash: await hashPassword(dto.password),
      role: dto.role || UserRole.Member,
      createdAt: new Date(),
      updatedAt: new Date(),
      isActive: true,
    };

    this.users.set(user.id, user);
    logger.info(`UserService: created user ${user.id}`);
    return user;
  }

  async deleteUser(id: string): Promise<boolean> {
    const existed = this.users.has(id);
    this.users.delete(id);
    if (existed) {
      logger.info(`UserService: deleted user ${id}`);
    }
    return existed;
  }

  async updateUser(id: string, dto: UpdateUserDto): Promise<User | null> {
    const user = this.users.get(id);
    if (!user) return null;

    const updated: User = {
      ...user,
      ...dto,
      updatedAt: new Date(),
    };
    this.users.set(id, updated);
    logger.info(`UserService: updated user ${id}`);
    return updated;
  }

  async listUsers(): Promise<User[]> {
    return Array.from(this.users.values());
  }
}
