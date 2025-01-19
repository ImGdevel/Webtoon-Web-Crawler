import json
from .WebtoonRepository import WebtoonRepository
from src.Model.WebtoonCreateRequestDTO import WebtoonCreateRequestDTO

class JsonWebtoonRepository(WebtoonRepository):
    def __init__(self):
        self.webtoons = []
        self.webtoon_id = 0

    def save(self, webtoon_data: WebtoonCreateRequestDTO):
        # WebtoonCreateRequestDTO 객체의 title 속성으로 확인
        if self._exists(webtoon_data.title):
            self._update_day(webtoon_data)
        else:
            # WebtoonCreateRequestDTO 객체의 id 속성을 설정하고 리스트에 추가
            webtoon_data.id = self.webtoon_id
            self.webtoons.append(webtoon_data)
            self.webtoon_id += 1

    def _exists(self, title: str) -> bool:
        # WebtoonCreateRequestDTO 객체의 title 속성으로 비교
        return any(webtoon.title == title for webtoon in self.webtoons)

    def _update_day(self, webtoon_data: WebtoonCreateRequestDTO):
        # day 속성을 업데이트
        for webtoon in self.webtoons:
            if webtoon.title == webtoon_data.title:
                webtoon.day_of_week += ', ' + webtoon_data.day_of_week
                break

    def save_to_file(self, filename: str):
        # WebtoonCreateRequestDTO 객체를 딕셔너리로 변환해서 JSON 파일로 저장
        with open(f"{filename}.json", "w", encoding="utf-8") as output_file:
            # 객체를 JSON으로 직렬화하기 전에 to_dict() 메서드를 사용하여 딕셔너리로 변환
            json.dump([webtoon.to_dict() for webtoon in self.webtoons], output_file, ensure_ascii=False, indent=4)
