import json
from .WebtoonRepository import WebtoonRepository

class JsonWebtoonRepository(WebtoonRepository):
    def __init__(self):
        self.webtoons = []
        self.webtoon_id = 0

    def save(self, webtoon_data: dict):
        if self._exists(webtoon_data["title"]):
            self._update_day(webtoon_data)
        else:
            webtoon_data["id"] = self.webtoon_id
            self.webtoons.append(webtoon_data)
            self.webtoon_id += 1

    def _exists(self, title: str) -> bool:
        return any(webtoon['title'] == title for webtoon in self.webtoons)

    def _update_day(self, webtoon_data: dict):
        for webtoon in self.webtoons:
            if webtoon['title'] == webtoon_data['title']:
                webtoon['day'] += ', ' + webtoon_data['day']
                break

    def save_to_file(self, filename: str):
        with open(f"{filename}.json", "w", encoding="utf-8") as output_file:
            json.dump(self.webtoons, output_file, ensure_ascii=False, indent=4)
