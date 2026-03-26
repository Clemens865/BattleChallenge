export interface User {
  id: string;
  email: string;
  username: string;
  passwordHash: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
}

export enum UserRole {
  Admin = "admin",
  Member = "member",
  Guest = "guest",
}

export interface CreateUserDto {
  email: string;
  username: string;
  password: string;
  role?: UserRole;
}

export interface UpdateUserDto {
  email?: string;
  username?: string;
  role?: UserRole;
  isActive?: boolean;
}
