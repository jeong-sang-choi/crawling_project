#!/usr/bin/env python3
"""
상용화 웹 크롤러 - Phase 1: 기술적 완성도 향상
"""

import sys
import json
import re
import time
import random
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QProgressBar, QComboBox, QGroupBox,
                            QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QCheckBox, QListWidget, QListWidgetItem, QSpinBox,
                            QFileDialog, QSlider, QSplitter)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import queue
import hashlib
import os

class CommercialCrawler:
    """상용화 크롤러 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.proxy_list = []
        self.current_proxy = None
        self.retry_count = 3
        self.delay_range = (1, 3)
        self.max_concurrent = 5
        self.crawled_urls = set()
        self.error_log = []
        
    def load_proxies(self, proxy_file=None):
        """프록시 목록 로드"""
        if proxy_file and os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                self.proxy_list = [line.strip() for line in f if line.strip()]
        else:
            # 기본 프록시 목록 (실제 사용시 유료 프록시 서비스 권장)
            self.proxy_list = [
                # 여기에 실제 프록시 서버 정보 입력
            ]
    
    def get_random_proxy(self):
        """랜덤 프록시 선택"""
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    def get_headers(self):
        """랜덤 헤더 생성"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def make_request(self, url, use_proxy=True, timeout=30):
        """요청 보내기 (재시도 로직 포함)"""
        for attempt in range(self.retry_count):
            try:
                headers = self.get_headers()
                proxies = None
                
                if use_proxy and self.proxy_list:
                    proxy = self.get_random_proxy()
                    if proxy:
                        proxies = {'http': proxy, 'https': proxy}
                
                # 랜덤 딜레이
                time.sleep(random.uniform(*self.delay_range))
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    proxies=proxies, 
                    timeout=timeout
                )
                response.raise_for_status()
                return response
                
            except Exception as e:
                self.error_log.append({
                    'url': url,
                    'attempt': attempt + 1,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                if attempt == self.retry_count - 1:
                    raise e
                
                time.sleep(2 ** attempt)  # 지수 백오프
        
        return None

class AdvancedCrawlerThread(QThread):
    """고급 크롤링 작업을 별도 스레드에서 실행"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    data_signal = pyqtSignal(dict)  # 실시간 데이터 전송
    
    def __init__(self, url, options=None):
        super().__init__()
        self.url = url
        self.options = options or {}
        self.is_running = True
        self.crawler = CommercialCrawler()
        
    def run(self):
        try:
            self.progress_signal.emit("크롤링 시작...")
            result = self.advanced_crawl()
            
            if self.is_running:
                self.finished_signal.emit(result)
                
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def advanced_crawl(self):
        """고급 크롤링"""
        self.progress_signal.emit("페이지 가져오는 중...")
        
        # 프록시 사용 여부
        use_proxy = self.options.get('use_proxy', False)
        if use_proxy:
            self.crawler.load_proxies(self.options.get('proxy_file'))
        
        # 요청 보내기
        response = self.crawler.make_request(self.url, use_proxy=use_proxy)
        
        self.progress_signal.emit("페이지 파싱 중...")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 기본 정보
        data = {
            'url': self.url,
            'timestamp': datetime.now().isoformat(),
            'crawler_info': {
                'user_agent': response.request.headers.get('User-Agent', ''),
                'proxy_used': self.crawler.current_proxy,
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            },
            'extracted_data': {},
            'basic_info': {},
            'performance_metrics': {}
        }
        
        # 기본 정보 추출
        self.progress_signal.emit("기본 정보 추출 중...")
        basic_info = self.extract_basic_info(soup)
        data['basic_info'] = basic_info
        
        # 고급 정보 추출
        self.progress_signal.emit("고급 정보 추출 중...")
        advanced_info = self.extract_advanced_info(soup)
        data['extracted_data'] = advanced_info
        
        # 성능 메트릭 계산
        self.progress_signal.emit("성능 분석 중...")
        performance = self.calculate_performance_metrics(soup, response)
        data['performance_metrics'] = performance
        
        # 실시간 데이터 전송
        self.data_signal.emit(data)
        
        self.progress_signal.emit("크롤링 완료!")
        return data
    
    def extract_basic_info(self, soup):
        """기본 정보 추출"""
        info = {
            'title': '',
            'description': '',
            'keywords': [],
            'images': [],
            'links': [],
            'text_content': '',
            'headers': {},
            'meta_tags': {},
            'forms': [],
            'scripts': [],
            'styles': []
        }
        
        # 제목
        title_tag = soup.find('title')
        if title_tag:
            info['title'] = title_tag.get_text(strip=True)
        
        # 메타 태그
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                info['description'] = content
            elif name == 'keywords':
                info['keywords'] = [kw.strip() for kw in content.split(',')]
            else:
                info['meta_tags'][name] = content
        
        # 헤더
        for i in range(1, 7):
            headers = soup.find_all(f'h{i}')
            info['headers'][f'h{i}'] = [h.get_text(strip=True) for h in headers]
        
        # 이미지
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            info['images'].append({
                'src': urljoin(self.url, src),
                'alt': alt,
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        
        # 링크
        base_domain = urlparse(self.url).netloc
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(self.url, href)
            link_domain = urlparse(absolute_url).netloc
            
            info['links'].append({
                'url': absolute_url,
                'text': link.get_text(strip=True),
                'title': link.get('title', ''),
                'is_internal': link_domain == base_domain
            })
        
        # 폼
        for form in soup.find_all('form'):
            info['forms'].append({
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': [{'name': inp.get('name', ''), 'type': inp.get('type', '')} 
                          for inp in form.find_all('input')]
            })
        
        # 스크립트
        for script in soup.find_all('script'):
            info['scripts'].append({
                'src': script.get('src', ''),
                'type': script.get('type', ''),
                'content_length': len(script.get_text())
            })
        
        # 스타일
        for style in soup.find_all('style'):
            info['styles'].append({
                'content_length': len(style.get_text())
            })
        
        # 텍스트
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text_content = soup.get_text(separator=' ', strip=True)
        info['text_content'] = text_content[:2000] + "..." if len(text_content) > 2000 else text_content
        
        return info
    
    def extract_advanced_info(self, soup):
        """고급 정보 추출"""
        advanced = {
            'content_analysis': {},
            'seo_metrics': {},
            'accessibility': {},
            'security': {}
        }
        
        # 콘텐츠 분석
        text_content = soup.get_text()
        advanced['content_analysis'] = {
            'word_count': len(text_content.split()),
            'character_count': len(text_content),
            'paragraph_count': len(soup.find_all('p')),
            'sentence_count': len(re.split(r'[.!?]+', text_content)),
            'average_sentence_length': len(text_content.split()) / max(len(re.split(r'[.!?]+', text_content)), 1)
        }
        
        # SEO 메트릭
        advanced['seo_metrics'] = {
            'title_length': len(soup.find('title').get_text() if soup.find('title') else ''),
            'meta_description_length': len(soup.find('meta', attrs={'name': 'description'}).get('content', '') if soup.find('meta', attrs={'name': 'description'}) else ''),
            'h1_count': len(soup.find_all('h1')),
            'h2_count': len(soup.find_all('h2')),
            'image_count': len(soup.find_all('img')),
            'image_with_alt': len([img for img in soup.find_all('img') if img.get('alt')]),
            'internal_links': len([link for link in soup.find_all('a', href=True) if urlparse(link['href']).netloc == urlparse(self.url).netloc]),
            'external_links': len([link for link in soup.find_all('a', href=True) if urlparse(link['href']).netloc != urlparse(self.url).netloc])
        }
        
        # 접근성
        advanced['accessibility'] = {
            'images_without_alt': len([img for img in soup.find_all('img') if not img.get('alt')]),
            'forms_without_labels': len([form for form in soup.find_all('form') if not form.find_all('label')]),
            'tables_without_headers': len([table for table in soup.find_all('table') if not table.find_all('th')])
        }
        
        # 보안
        advanced['security'] = {
            'has_https': self.url.startswith('https'),
            'has_csp': bool(soup.find('meta', attrs={'http-equiv': 'Content-Security-Policy'})),
            'has_hsts': bool(soup.find('meta', attrs={'http-equiv': 'Strict-Transport-Security'}))
        }
        
        return advanced
    
    def calculate_performance_metrics(self, soup, response):
        """성능 메트릭 계산"""
        return {
            'page_size': len(response.content),
            'html_size': len(response.text),
            'css_size': sum(len(style.get_text()) for style in soup.find_all('style')),
            'js_size': sum(len(script.get_text()) for script in soup.find_all('script')),
            'image_count': len(soup.find_all('img')),
            'script_count': len(soup.find_all('script')),
            'style_count': len(soup.find_all('style')),
            'link_count': len(soup.find_all('a')),
            'form_count': len(soup.find_all('form'))
        }
    
    def stop(self):
        """크롤링 중지"""
        self.is_running = False

class CommercialWebCrawlerGUI(QMainWindow):
    """상용화 웹 크롤러 GUI"""
    
    def __init__(self):
        super().__init__()
        self.crawler_thread = None
        self.crawler = CommercialCrawler()
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("🚀 상용화 웹 크롤러 Pro")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # 제목
        title_label = QLabel("상용화 웹 크롤러 Pro")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # URL 입력 그룹
        url_group = QGroupBox("URL 입력")
        url_layout = QHBoxLayout(url_group)
        
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        
        self.crawl_button = QPushButton("크롤링 시작")
        self.crawl_button.clicked.connect(self.start_crawling)
        
        self.stop_button = QPushButton("중지")
        self.stop_button.clicked.connect(self.stop_crawling)
        self.stop_button.setEnabled(False)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.crawl_button)
        url_layout.addWidget(self.stop_button)
        
        layout.addWidget(url_group)
        
        # 고급 옵션 그룹
        options_group = QGroupBox("고급 옵션")
        options_layout = QHBoxLayout(options_group)
        
        # 프록시 옵션
        self.use_proxy_checkbox = QCheckBox("프록시 사용")
        self.proxy_file_button = QPushButton("프록시 파일 선택")
        self.proxy_file_button.clicked.connect(self.select_proxy_file)
        
        # 딜레이 설정
        delay_label = QLabel("딜레이 (초):")
        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setRange(1, 10)
        self.delay_slider.setValue(3)
        self.delay_value_label = QLabel("3")
        self.delay_slider.valueChanged.connect(lambda v: self.delay_value_label.setText(str(v)))
        
        # 재시도 횟수
        retry_label = QLabel("재시도:")
        self.retry_spinbox = QSpinBox()
        self.retry_spinbox.setRange(1, 10)
        self.retry_spinbox.setValue(3)
        
        options_layout.addWidget(self.use_proxy_checkbox)
        options_layout.addWidget(self.proxy_file_button)
        options_layout.addWidget(delay_label)
        options_layout.addWidget(self.delay_slider)
        options_layout.addWidget(self.delay_value_label)
        options_layout.addWidget(retry_label)
        options_layout.addWidget(self.retry_spinbox)
        options_layout.addStretch()
        
        layout.addWidget(options_group)
        
        # 진행률 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 상태 표시
        self.status_label = QLabel("대기 중...")
        layout.addWidget(self.status_label)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 결과 탭
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.tab_widget.addTab(self.result_text, "전체 결과")
        
        # 성능 분석 탭
        self.performance_text = QTextEdit()
        self.performance_text.setReadOnly(True)
        self.tab_widget.addTab(self.performance_text, "성능 분석")
        
        # SEO 분석 탭
        self.seo_text = QTextEdit()
        self.seo_text.setReadOnly(True)
        self.tab_widget.addTab(self.seo_text, "SEO 분석")
        
        # 에러 로그 탭
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.tab_widget.addTab(self.error_text, "에러 로그")
        
        # 요약 탭
        self.summary_table = QTableWidget()
        self.tab_widget.addTab(self.summary_table, "요약 정보")
        
        # 버튼 그룹
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("결과 저장")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        
        self.export_excel_button = QPushButton("Excel 내보내기")
        self.export_excel_button.clicked.connect(self.export_to_excel)
        self.export_excel_button.setEnabled(False)
        
        self.clear_button = QPushButton("초기화")
        self.clear_button.clicked.connect(self.clear_results)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.export_excel_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 결과 데이터 저장
        self.crawl_result = None
        self.proxy_file = None
        
    def select_proxy_file(self):
        """프록시 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "프록시 파일 선택", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.proxy_file = file_path
            QMessageBox.information(self, "성공", f"프록시 파일이 선택되었습니다: {file_path}")
        
    def start_crawling(self):
        """크롤링 시작"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력해주세요.")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        
        # UI 상태 변경
        self.crawl_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("크롤링 준비 중...")
        
        # 옵션 설정
        options = {
            'use_proxy': self.use_proxy_checkbox.isChecked(),
            'proxy_file': self.proxy_file,
            'delay_range': (self.delay_slider.value(), self.delay_slider.value() + 1),
            'retry_count': self.retry_spinbox.value()
        }
        
        # 크롤링 스레드 시작
        self.crawler_thread = AdvancedCrawlerThread(url, options)
        self.crawler_thread.progress_signal.connect(self.update_progress)
        self.crawler_thread.finished_signal.connect(self.crawling_finished)
        self.crawler_thread.error_signal.connect(self.crawling_error)
        self.crawler_thread.data_signal.connect(self.update_data)
        self.crawler_thread.start()
        
    def stop_crawling(self):
        """크롤링 중지"""
        if self.crawler_thread:
            self.crawler_thread.stop()
            self.crawler_thread.wait()
        
        self.crawl_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("크롤링이 중지되었습니다.")
        
    def update_progress(self, message):
        """진행률 업데이트"""
        self.status_label.setText(message)
        
    def update_data(self, data):
        """실시간 데이터 업데이트"""
        self.crawl_result = data
        self.display_results(data)
        
    def crawling_finished(self, result):
        """크롤링 완료"""
        self.crawl_result = result
        
        # UI 상태 복원
        self.crawl_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("크롤링 완료!")
        
        # 결과 표시
        self.display_results(result)
        
        # 저장 버튼 활성화
        self.save_button.setEnabled(True)
        self.export_excel_button.setEnabled(True)
        
    def crawling_error(self, error_message):
        """크롤링 에러"""
        self.crawl_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("크롤링 실패!")
        
        QMessageBox.critical(self, "에러", f"크롤링 중 오류가 발생했습니다:\n{error_message}")
        
    def display_results(self, result):
        """결과 표시"""
        # 전체 결과 표시
        self.result_text.setText(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 성능 분석 표시
        performance = result.get('performance_metrics', {})
        self.performance_text.setText(json.dumps(performance, ensure_ascii=False, indent=2))
        
        # SEO 분석 표시
        seo_metrics = result.get('extracted_data', {}).get('seo_metrics', {})
        self.seo_text.setText(json.dumps(seo_metrics, ensure_ascii=False, indent=2))
        
        # 에러 로그 표시
        if hasattr(self.crawler_thread.crawler, 'error_log'):
            self.error_text.setText(json.dumps(self.crawler_thread.crawler.error_log, ensure_ascii=False, indent=2))
        
        # 요약 정보 표시
        self.display_summary(result)
        
    def display_summary(self, result):
        """요약 정보 표시"""
        self.summary_table.setRowCount(15)
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["항목", "값"])
        
        basic_info = result.get('basic_info', {})
        extracted_data = result.get('extracted_data', {})
        performance = result.get('performance_metrics', {})
        crawler_info = result.get('crawler_info', {})
        
        summary_data = [
            ("URL", result.get('url', '')),
            ("크롤링 시간", result.get('timestamp', '')),
            ("제목", basic_info.get('title', '')),
            ("페이지 크기", f"{performance.get('page_size', 0):,} bytes"),
            ("이미지 수", str(len(basic_info.get('images', [])))),
            ("링크 수", str(len(basic_info.get('links', [])))),
            ("단어 수", str(extracted_data.get('content_analysis', {}).get('word_count', 0))),
            ("H1 태그 수", str(extracted_data.get('seo_metrics', {}).get('h1_count', 0))),
            ("내부 링크", str(extracted_data.get('seo_metrics', {}).get('internal_links', 0))),
            ("외부 링크", str(extracted_data.get('seo_metrics', {}).get('external_links', 0))),
            ("User-Agent", crawler_info.get('user_agent', '')[:50] + "..."),
            ("프록시 사용", "예" if crawler_info.get('proxy_used') else "아니오"),
            ("응답 시간", f"{crawler_info.get('response_time', 0):.2f}초"),
            ("상태 코드", str(crawler_info.get('status_code', ''))),
            ("HTTPS 사용", "예" if extracted_data.get('security', {}).get('has_https') else "아니오")
        ]
        
        for i, (key, value) in enumerate(summary_data):
            self.summary_table.setItem(i, 0, QTableWidgetItem(key))
            self.summary_table.setItem(i, 1, QTableWidgetItem(value))
        
        self.summary_table.resizeColumnsToContents()
        
    def save_results(self):
        """결과 저장"""
        if not self.crawl_result:
            return
            
        filename = f"commercial_crawl_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.crawl_result, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "성공", f"결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def export_to_excel(self):
        """Excel로 내보내기"""
        if not self.crawl_result:
            return
            
        try:
            import pandas as pd
            
            # 데이터 준비
            data = []
            basic_info = self.crawl_result.get('basic_info', {})
            extracted_data = self.crawl_result.get('extracted_data', {})
            
            # 기본 정보
            data.append(['URL', self.crawl_result.get('url', '')])
            data.append(['제목', basic_info.get('title', '')])
            data.append(['설명', basic_info.get('description', '')])
            data.append(['단어 수', extracted_data.get('content_analysis', {}).get('word_count', 0)])
            data.append(['이미지 수', len(basic_info.get('images', []))])
            data.append(['링크 수', len(basic_info.get('links', []))])
            
            # DataFrame 생성
            df = pd.DataFrame(data, columns=['항목', '값'])
            
            # 파일 저장
            filename = f"crawl_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "성공", f"Excel 파일이 {filename}에 저장되었습니다.")
            
        except ImportError:
            QMessageBox.warning(self, "경고", "Excel 내보내기를 위해 pandas를 설치해주세요: pip install pandas openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"Excel 내보내기 중 오류가 발생했습니다:\n{str(e)}")
            
    def clear_results(self):
        """결과 초기화"""
        self.result_text.clear()
        self.performance_text.clear()
        self.seo_text.clear()
        self.error_text.clear()
        self.summary_table.setRowCount(0)
        self.crawl_result = None
        self.save_button.setEnabled(False)
        self.export_excel_button.setEnabled(False)
        self.status_label.setText("대기 중...")

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = CommercialWebCrawlerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
