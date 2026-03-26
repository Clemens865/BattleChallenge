"""Data models for the blog application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_active: bool = True

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }


@dataclass
class Post:
    id: str
    title: str
    body: str
    author_id: str
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = None
    is_published: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "author_id": self.author_id,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_published": self.is_published,
        }
