# 웹툰 크롤러 사용 가이드

## 기본 사용법

### 1. 초기화 크롤러
```python
from crawler import WebtoonCrawlerFactory

# 초기화 크롤러 생성
crawler = WebtoonCrawlerFactory.create_crawler("init_webtoon")
crawler.crawl()  # 크롤링 실행
```

### 2. 에피소드 수집 크롤러
```python
# 에피소드 수집 크롤러 생성
crawler = WebtoonCrawlerFactory.create_crawler("collect_episodes")
crawler.crawl()  # 크롤링 실행
```

### 3. 상태 확인 크롤러
```python
# 상태 확인 크롤러 생성
crawler = WebtoonCrawlerFactory.create_crawler("check_status")
crawler.crawl()  # 크롤링 실행
```

## 크롤러 종류

1. **InitWebtoonCrawler**
   - 웹툰의 기본 정보를 초기화하는 크롤러
   - 제목, 작가, 장르 등 기본 메타데이터 수집

2. **EpisodeCollectorCrawler**
   - 웹툰의 에피소드 정보를 수집하는 크롤러
   - 에피소드 제목, 업로드 날짜, 조회수 등 수집

3. **StatusCheckCrawler**
   - 웹툰의 연재 상태를 확인하는 크롤러
   - 연재 중, 휴재, 완결 등의 상태 확인

## 주의사항

1. 크롤러 사용 전 반드시 WebDriver 인스턴스가 필요합니다.
2. 각 크롤러는 독립적으로 동작하며, 순서에 따라 실행해야 합니다.
3. 크롤링 실패 시 적절한 예외 처리가 필요합니다.

## 예외 처리

```python
try:
    crawler = WebtoonCrawlerFactory.create_crawler("init_webtoon")
    crawler.crawl()
except Exception as e:
    print(f"크롤링 오류 발생: {e}")
``` 