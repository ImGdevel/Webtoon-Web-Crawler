from enum import Enum

class AuthorRole(Enum):
    WRITER = "글"
    ARTIST = "그림"
    BOTH = "글/그림"
    ORIGINAL = "원작"
