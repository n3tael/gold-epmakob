import os

class Config(object):
    """Application configuration."""
    def __init__(self, instance_path):
        self.SITE_NAME = "Золотая галерея Ермакова"
        self.POSTS_PER_PAGE = 24

        self.DATABASE = os.path.join(instance_path, 'main.db'),
        self.SECRET_KEY = b"change-me" # !! CHANGE THIS !!
        self.SQUEEZE_COMPRESS = False