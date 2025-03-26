from dataclasses import dataclass

@dataclass
class AuthorDTO:
    """저자 정보를 저장하는 데이터 객체"""
    id: str
    name: str
    role: str
    link: str 