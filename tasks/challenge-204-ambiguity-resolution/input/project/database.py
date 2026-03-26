"""In-memory database layer for users and posts."""

from typing import Dict, List, Optional
from models import User, Post


class Database:
    """Simple in-memory store for the blog application."""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._posts: Dict[str, Post] = {}

    # ---- User operations ----

    def add_user(self, user: User) -> bool:
        if user.id in self._users:
            return False
        self._users[user.id] = user
        return True

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        for u in self._users.values():
            if u.email == email:
                return u
        return None

    def list_users(self) -> List[User]:
        return list(self._users.values())

    # ---- Post operations ----

    def add_post(self, post: Post) -> bool:
        if post.id in self._posts:
            return False
        self._posts[post.id] = post
        return True

    def get_post(self, post_id: str) -> Optional[Post]:
        return self._posts.get(post_id)

    def get_posts_by_author(self, author_id: str) -> List[Post]:
        return [p for p in self._posts.values() if p.author_id == author_id]

    def list_posts(self, published_only: bool = True) -> List[Post]:
        if published_only:
            return [p for p in self._posts.values() if p.is_published]
        return list(self._posts.values())

    def delete_post(self, post_id: str) -> bool:
        if post_id in self._posts:
            del self._posts[post_id]
            return True
        return False
