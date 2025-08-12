import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import json
import os
from datetime import datetime
import logging
import threading
from queue import Queue
import hashlib
from fake_useragent import UserAgent
import re

class AdvancedWebCrawler:
    """
    고급 웹 크롤러 - 구글 봇과 유사한 기능
    """
    
    def __init__(self, config=None):
        self.config = config or {
            'delay_range': (1, 3),
            'max_pages': 100,
            'max_depth': 3,
            'max_workers': 3,
            'timeout': 10,
            'respect_robots': True,
            'output_file': 'advanced_crawled_data.json',
            'cache_file': 'crawler_cache.json'
        }
        
        self.session = requests.Session()
        self.ua = UserAgent()
        self.crawled_urls = set()
        self.crawled_data = []
        self.robots_cache = {}
        self.url_queue = Queue()
        self.lock = threading.Lock()
        
        # 로깅 설정
        self._setup_logging()
        
        # 세션 설정
        self._setup_session()
        
        # 캐시 로드
        self._load_cache()
    
    def _setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('advanced_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_session(self):
        """세션 설정"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _load_cache(self):
        """캐시 파일 로드"""
        try:
            if os.path.exists(self.config['cache_file']):
                with open(self.config['cache_file'], 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.crawled_urls = set(cache_data.get('crawled_urls', []))
                    self.logger.info(f"캐시에서 {len(self.crawled_urls)}개 URL 로드됨")
        except Exception as e:
            self.logger.warning(f"캐시 로드 실패: {e}")
    
    def _save_cache(self):
        """캐시 파일 저장"""
        try:
            cache_data = {
                'crawled_urls': list(self.crawled_urls),
                'timestamp': datetime.now().isoformat()
            }
            with open(self.config['cache_file'], 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"캐시 저장 실패: {e}")
    
    def check_robots_txt(self, url):
        """robots.txt 확인"""
        if not self.config['respect_robots']:
            return True
        
        domain = urlparse(url).netloc
        if domain in self.robots_cache:
            return self.robots_cache[domain]
        
        try:
            robots_url = f"https://{domain}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            can_fetch = rp.can_fetch(self.session.headers['User-Agent'], url)
            self.robots_cache[domain] = can_fetch
            
            if not can_fetch:
                self.logger.warning(f"robots.txt에 의해 차단됨: {url}")
            
            return can_fetch
            
        except Exception as e:
            self.logger.warning(f"robots.txt 확인 실패 {domain}: {e}")
            return True
    
    def get_page(self, url):
        """웹페이지 가져오기"""
        try:
            # robots.txt 확인
            if not self.check_robots_txt(url):
                return None
            
            # 랜덤 지연
            time.sleep(random.uniform(*self.config['delay_range']))
            
            # User-Agent 변경
            self.session.headers['User-Agent'] = self.ua.random
            
            response = self.session.get(url, timeout=self.config['timeout'])
            response.raise_for_status()
            
            self.logger.info(f"페이지 가져옴: {url}")
            return response
            
        except requests.RequestException as e:
            self.logger.error(f"페이지 가져오기 실패 {url}: {e}")
            return None
    
    def parse_page(self, url, html_content):
        """페이지 파싱"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 페이지 해시 생성 (중복 확인용)
        content_hash = hashlib.md5(html_content.encode()).hexdigest()
        
        page_data = {
            'url': url,
            'content_hash': content_hash,
            'title': soup.title.string if soup.title else '',
            'timestamp': datetime.now().isoformat(),
            'links': [],
            'text_content': '',
            'meta_description': '',
            'meta_keywords': [],
            'images': [],
            'headers': {},
            'word_count': 0
        }
        
        # 메타 태그 추출
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                page_data['meta_description'] = content
            elif name == 'keywords':
                page_data['meta_keywords'] = [kw.strip() for kw in content.split(',')]
            elif name == 'robots':
                page_data['meta_robots'] = content
        
        # 헤더 태그 추출
        for i in range(1, 7):
            headers = soup.find_all(f'h{i}')
            page_data['headers'][f'h{i}'] = [h.get_text(strip=True) for h in headers]
        
        # 이미지 추출
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            page_data['images'].append({
                'src': urljoin(url, src),
                'alt': alt
            })
        
        # 텍스트 내용 추출
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text_content = soup.get_text(separator=' ', strip=True)
        page_data['text_content'] = text_content
        page_data['word_count'] = len(text_content.split())
        
        # 링크 추출
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            
            # 같은 도메인의 링크만 수집
            if self._is_same_domain(url, absolute_url):
                page_data['links'].append({
                    'url': absolute_url,
                    'text': link.get_text(strip=True),
                    'title': link.get('title', '')
                })
        
        return page_data
    
    def _is_same_domain(self, base_url, target_url):
        """같은 도메인 확인"""
        base_domain = urlparse(base_url).netloc
        target_domain = urlparse(target_url).netloc
        return base_domain == target_domain
    
    def worker(self):
        """워커 스레드"""
        while True:
            try:
                item = self.url_queue.get(timeout=1)
                if item is None:
                    break
                
                url, depth = item
                
                with self.lock:
                    if url in self.crawled_urls or len(self.crawled_urls) >= self.config['max_pages']:
                        self.url_queue.task_done()
                        continue
                
                response = self.get_page(url)
                if response:
                    page_data = self.parse_page(url, response.text)
                    
                    with self.lock:
                        if url not in self.crawled_urls:
                            self.crawled_data.append(page_data)
                            self.crawled_urls.add(url)
                            
                            # 새로운 링크들을 큐에 추가
                            if depth < self.config['max_depth']:
                                for link_info in page_data['links']:
                                    link_url = link_info['url']
                                    if link_url not in self.crawled_urls:
                                        self.url_queue.put((link_url, depth + 1))
                
                self.url_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"워커 에러: {e}")
                self.url_queue.task_done()
    
    def crawl(self, start_url):
        """멀티스레드 크롤링"""
        self.logger.info(f"고급 크롤링 시작: {start_url}")
        
        # 시작 URL을 큐에 추가
        self.url_queue.put((start_url, 0))
        
        # 워커 스레드 시작
        threads = []
        for _ in range(self.config['max_workers']):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 모든 작업 완료 대기
        self.url_queue.join()
        
        # 워커 스레드 종료
        for _ in range(self.config['max_workers']):
            self.url_queue.put(None)
        
        for t in threads:
            t.join()
        
        self.logger.info(f"크롤링 완료. 총 {len(self.crawled_urls)}개 페이지 크롤링됨")
        self.save_data()
        self._save_cache()
    
    def save_data(self):
        """데이터 저장"""
        output_data = {
            'crawl_info': {
                'start_time': datetime.now().isoformat(),
                'total_pages': len(self.crawled_data),
                'config': self.config
            },
            'pages': self.crawled_data
        }
        
        with open(self.config['output_file'], 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"데이터가 {self.config['output_file']}에 저장되었습니다.")
    
    def get_statistics(self):
        """통계 반환"""
        if not self.crawled_data:
            return {}
        
        total_links = sum(len(page['links']) for page in self.crawled_data)
        total_images = sum(len(page['images']) for page in self.crawled_data)
        total_words = sum(page['word_count'] for page in self.crawled_data)
        
        return {
            'total_pages': len(self.crawled_data),
            'total_links': total_links,
            'total_images': total_images,
            'total_words': total_words,
            'average_words_per_page': total_words / len(self.crawled_data),
            'average_links_per_page': total_links / len(self.crawled_data),
            'average_images_per_page': total_images / len(self.crawled_data)
        }

# 사용 예시
if __name__ == "__main__":
    config = {
        'delay_range': (1, 2),
        'max_pages': 30,
        'max_depth': 2,
        'max_workers': 2,
        'respect_robots': True,
        'output_file': 'advanced_crawled_data.json'
    }
    
    crawler = AdvancedWebCrawler(config)
    start_url = "https://example.com"
    crawler.crawl(start_url)
    
    stats = crawler.get_statistics()
    print(f"크롤링 통계: {stats}")
