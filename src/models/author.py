from dataclasses import dataclass
from models.enums import AuthorRole

@dataclass
class AuthorDTO:
    """저자 정보를 저장하는 데이터 객체"""
    uid: str
    name: str
    role: AuthorRole