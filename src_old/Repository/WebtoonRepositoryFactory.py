from src.Repository.WebtoonRepository import WebtoonRepository
from src.Repository.JsonWebtoonRepository import JsonWebtoonRepository

class WebtoonRepositoryFactory:
    @staticmethod
    def create_repository(repository_type: str) -> WebtoonRepository:
        if repository_type == 'json':
            return JsonWebtoonRepository()
        else:
            raise ValueError(f"Unsupported repository type: {repository_type}")
