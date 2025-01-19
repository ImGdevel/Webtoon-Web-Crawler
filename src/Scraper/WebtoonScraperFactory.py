from src.Scraper.KaKaoWebtoonScraper import KaKaoWebtoonScraper
from src.Scraper.NaverWebtoonScraper import NaverWebtoonScraper


# Scraper Factory 구현
class WebtoonScraperFactory:
    @staticmethod
    def create_scraper(scraper_type: str, driver):
        if scraper_type == 'naver':
            return NaverWebtoonScraper(driver)
        elif scraper_type == 'kakao':
            return KaKaoWebtoonScraper(driver)
        else:
            raise ValueError(f"Unsupported scraper type: {scraper_type}")