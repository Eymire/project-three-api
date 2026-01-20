from enum import Enum


class UserScope(str, Enum):
    USER = 'user'
    ADMIN = 'admin'


class FileVisibility(str, Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
