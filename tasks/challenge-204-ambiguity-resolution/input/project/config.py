"""Application configuration."""


class Config:
    """Base configuration."""
    APP_NAME = "BlogApp"
    DEBUG = False
    SECRET_KEY = "dev-secret-key-change-in-prod"
    DATABASE_URI = "sqlite:///blog.db"
    MAX_POSTS_PER_PAGE = 20
    TOKEN_EXPIRY_HOURS = 24
    ALLOWED_POST_TAGS = ["tech", "science", "art", "news", "opinion"]


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    SECRET_KEY = None  # Must be set via environment variable


def get_config(env="development"):
    configs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    return configs.get(env, DevelopmentConfig)
