import json
from dataclasses import dataclass, asdict
from typing import List
import requests
from bs4 import BeautifulSoup

response = requests.get("https://comic.naver.com/webtoon/list?titleId=747269")
print(response.text)  # HTML 내용을 출력
