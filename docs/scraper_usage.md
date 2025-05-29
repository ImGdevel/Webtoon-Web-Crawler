# 웹툰 스크래퍼 사용 가이드

## 기본 사용법

### 1. 기본 정보 수집
```python
from scrapers.webtoon_scraper_factory import WebtoonScraperFactory

# 기본 정보(제목, 썸네일, 줄거리, 장르, 작가) 수집
scraper = WebtoonScraperFactory.create_basic_info_scraper(driver)
success, webtoon = scraper.fetch_webtoon(url)
```

### 2. 제목과 장르만 수집
```python
# 제목과 장르만 수집
scraper = WebtoonScraperFactory.create_title_genre_scraper(driver)
success, webtoon = scraper.fetch_webtoon(url)
```

### 3. 모든 정보 수집
```python
# 모든 가능한 정보 수집
scraper = WebtoonScraperFactory.create_full_info_scraper(driver)
success, webtoon = scraper.fetch_webtoon(url)
```

## 고급 사용법

### 1. 특정 플랫폼 지정
```python
# 네이버 웹툰 스크래퍼 생성
scraper = WebtoonScraperFactory.create_basic_info_scraper(driver, platform="naver")
```

### 2. 커스텀 스크래퍼 구성
```python
# 원하는 정보만 선택적으로 수집
builder = WebtoonScraperFactory.create_builder(driver, platform="naver")
scraper = (builder
    .scrape_title()
    .scrape_genres()
    .scrape_authors()
    .build())
```

### 3. 새로운 플랫폼 추가
```python
from scrapers.i_webtoon_scraper import IWebtoonScraper

class KakaoWebtoonScraper(IWebtoonScraper):
    # 구현...

# 새로운 플랫폼 등록
WebtoonScraperFactory.register_scraper("kakao", KakaoWebtoonScraper)

# 카카오 웹툰 스크래퍼 사용
scraper = WebtoonScraperFactory.create_basic_info_scraper(driver, platform="kakao")
```

## 주의사항

1. 스크래퍼 사용 전 반드시 WebDriver 인스턴스가 필요합니다.
2. 성인 인증이 필요한 웹툰의 경우 `success`가 `False`로 반환됩니다.
3. 스크래핑 실패 시 `webtoon`은 `None`이 반환됩니다.

## 예외 처리

```python
try:
    success, webtoon = scraper.fetch_webtoon(url)
    if success and webtoon:
        # 성공적으로 데이터 수집
        print(f"제목: {webtoon.title}")
        print(f"장르: {webtoon.genres}")
    else:
        # 수집 실패
        print("웹툰 정보 수집 실패")
except Exception as e:
    print(f"오류 발생: {e}")
``` 