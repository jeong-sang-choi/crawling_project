import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import json
import os
from datetime import datetime
import logging

class WebCrawler:
    """
    구글 봇과 같은 웹 크롤러 클래스
    """
    
    def __init__(self, delay_range=(1, 3), max_pages=100, output_file="crawled_data.json"):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.delay_range = delay_range
        self.max_pages = max_pages
        self.output_file = output_file
        self.crawled_urls = set()
        self.crawled_data = []
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # User-Agent 설정
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_page(self, url):
        """웹페이지를 가져오는 메서드"""
        try:
            # 랜덤 지연 (봇 감지 방지)
            time.sleep(random.uniform(*self.delay_range))
            
            # User-Agent 변경
            self.session.headers['User-Agent'] = self.ua.random
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"성공적으로 페이지 가져옴: {url}")
            return response
            
        except requests.RequestException as e:
            self.logger.error(f"페이지 가져오기 실패 {url}: {e}")
            return None
    
    def parse_page(self, url, html_content):
        """페이지 내용을 파싱하는 메서드"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 페이지 정보 추출
        page_data = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'timestamp': datetime.now().isoformat(),
            'links': [],
            'text_content': '',
            'meta_description': '',
            'meta_keywords': []
        }
        
        # 메타 태그 추출
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            page_data['meta_description'] = meta_desc.get('content', '')
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            page_data['meta_keywords'] = [kw.strip() for kw in meta_keywords.get('content', '').split(',')]
        
        # 텍스트 내용 추출 (스크립트, 스타일 제외)
        for script in soup(["script", "style"]):
            script.decompose()
        
        page_data['text_content'] = soup.get_text(separator=' ', strip=True)
        
        # 링크 추출
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            
            # 같은 도메인의 링크만 수집
            if self._is_same_domain(url, absolute_url):
                page_data['links'].append({
                    'url': absolute_url,
                    'text': link.get_text(strip=True)
                })
        
        return page_data
    
    def _is_same_domain(self, base_url, target_url):
        """같은 도메인인지 확인하는 메서드"""
        base_domain = urlparse(base_url).netloc
        target_domain = urlparse(target_url).netloc
        return base_domain == target_domain
    
    def crawl(self, start_url, max_depth=3):
        """웹사이트를 크롤링하는 메인 메서드"""
        self.logger.info(f"크롤링 시작: {start_url}")
        
        urls_to_crawl = [(start_url, 0)]  # (url, depth)
        
        while urls_to_crawl and len(self.crawled_urls) < self.max_pages:
            current_url, depth = urls_to_crawl.pop(0)
            
            if current_url in self.crawled_urls or depth > max_depth:
                continue
            
            self.logger.info(f"크롤링 중: {current_url} (깊이: {depth})")
            
            # 페이지 가져오기
            response = self.get_page(current_url)
            if not response:
                continue
            
            # 페이지 파싱
            page_data = self.parse_page(current_url, response.text)
            self.crawled_data.append(page_data)
            self.crawled_urls.add(current_url)
            
            # 새로운 링크들을 큐에 추가
            if depth < max_depth:
                for link_info in page_data['links']:
                    link_url = link_info['url']
                    if link_url not in self.crawled_urls:
                        urls_to_crawl.append((link_url, depth + 1))
        
        self.logger.info(f"크롤링 완료. 총 {len(self.crawled_urls)}개 페이지 크롤링됨")
        self.save_data()
    
    def save_data(self):
        """크롤링된 데이터를 파일로 저장"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"데이터가 {self.output_file}에 저장되었습니다.")
    
    def get_statistics(self):
        """크롤링 통계 반환"""
        total_links = sum(len(page['links']) for page in self.crawled_data)
        total_text_length = sum(len(page['text_content']) for page in self.crawled_data)
        
        return {
            'total_pages': len(self.crawled_data),
            'total_links': total_links,
            'total_text_length': total_text_length,
            'average_text_length': total_text_length / len(self.crawled_data) if self.crawled_data else 0
        }

# 사용 예시
if __name__ == "__main__":
    # 크롤러 인스턴스 생성
    crawler = WebCrawler(delay_range=(1, 2), max_pages=50)
    
    # 웹사이트 크롤링 시작
    start_url = "https://example.com"  # 크롤링할 웹사이트 URL
    crawler.crawl(start_url, max_depth=2)
    
    # 통계 출력
    stats = crawler.get_statistics()
    print(f"크롤링 통계: {stats}")
