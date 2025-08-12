#!/usr/bin/env python3
"""
웹 크롤러 사용 예시
"""

from web_crawler import WebCrawler
from advanced_crawler import AdvancedWebCrawler
import json

def basic_crawler_example():
    """기본 크롤러 사용 예시"""
    print("=== 기본 크롤러 예시 ===")
    
    # 크롤러 설정
    crawler = WebCrawler(
        delay_range=(1, 2),  # 1-2초 지연
        max_pages=10,        # 최대 10페이지
        output_file="basic_crawled_data.json"
    )
    
    # 크롤링 시작
    start_url = "https://httpbin.org/html"  # 테스트용 URL
    crawler.crawl(start_url, max_depth=1)
    
    # 통계 출력
    stats = crawler.get_statistics()
    print(f"기본 크롤러 통계: {stats}")

def advanced_crawler_example():
    """고급 크롤러 사용 예시"""
    print("\n=== 고급 크롤러 예시 ===")
    
    # 고급 설정
    config = {
        'delay_range': (1, 2),
        'max_pages': 5,
        'max_depth': 1,
        'max_workers': 2,
        'timeout': 10,
        'respect_robots': True,
        'output_file': 'advanced_crawled_data.json',
        'cache_file': 'crawler_cache.json'
    }
    
    crawler = AdvancedWebCrawler(config)
    
    # 크롤링 시작
    start_url = "https://httpbin.org/html"
    crawler.crawl(start_url)
    
    # 통계 출력
    stats = crawler.get_statistics()
    print(f"고급 크롤러 통계: {stats}")

def custom_crawler_example():
    """커스텀 크롤러 예시"""
    print("\n=== 커스텀 크롤러 예시 ===")
    
    class CustomCrawler(WebCrawler):
        def parse_page(self, url, html_content):
            """커스텀 파싱 로직"""
            page_data = super().parse_page(url, html_content)
            
            # 추가 정보 추출
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 특정 클래스나 ID를 가진 요소들 추출
            page_data['custom_data'] = {
                'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p')],
                'divs_with_class': [div.get_text(strip=True) for div in soup.find_all('div', class_=True)],
                'forms': [form.get('action', '') for form in soup.find_all('form')]
            }
            
            return page_data
    
    # 커스텀 크롤러 사용
    custom_crawler = CustomCrawler(
        delay_range=(1, 1),
        max_pages=3,
        output_file="custom_crawled_data.json"
    )
    
    start_url = "https://httpbin.org/html"
    custom_crawler.crawl(start_url, max_depth=1)
    
    # 결과 확인
    try:
        with open("custom_crawled_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"커스텀 크롤러로 {len(data)}개 페이지 크롤링 완료")
    except FileNotFoundError:
        print("크롤링 결과 파일을 찾을 수 없습니다.")

def main():
    """메인 함수"""
    print("웹 크롤러 사용 예시를 시작합니다...")
    
    try:
        # 기본 크롤러 예시
        basic_crawler_example()
        
        # 고급 크롤러 예시
        advanced_crawler_example()
        
        # 커스텀 크롤러 예시
        custom_crawler_example()
        
        print("\n모든 예시가 완료되었습니다!")
        print("\n생성된 파일들:")
        print("- basic_crawled_data.json: 기본 크롤러 결과")
        print("- advanced_crawled_data.json: 고급 크롤러 결과")
        print("- custom_crawled_data.json: 커스텀 크롤러 결과")
        print("- crawler.log: 크롤러 로그")
        print("- advanced_crawler.log: 고급 크롤러 로그")
        
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    main()
