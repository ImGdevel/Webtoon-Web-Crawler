from abc import ABC, abstractmethod

class WebtoonRepository(ABC):
    @abstractmethod
    def save(self, webtoon_data: dict):
        pass

    @abstractmethod
    def save_to_file(self, filename: str):
        pass

