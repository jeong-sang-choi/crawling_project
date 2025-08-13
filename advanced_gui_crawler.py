#!/usr/bin/env python3
"""
고급 GUI 웹 크롤러 - 2단계: 사이트 템플릿 시스템
"""

import sys
import json
import re
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QProgressBar, QComboBox, QGroupBox,
                            QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QCheckBox, QListWidget, QListWidgetItem, QSplitter)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import time

class TemplateCrawler:
    """템플릿 기반 크롤러"""
    
    def __init__(self):
        self.templates = self.load_templates()
        
    def load_templates(self):
        """템플릿 파일 로드"""
        try:
            with open('site_templates.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def detect_site_type(self, url, soup):
        """사이트 유형 자동 감지"""
        # URL 패턴으로 감지
        domain = urlparse(url).netloc.lower()
        
        if any(keyword in domain for keyword in ['shop', 'store', 'mall', 'market']):
            return 'shopping'
        elif any(keyword in domain for keyword in ['news', 'press', 'media']):
            return 'news'
        elif any(keyword in domain for keyword in ['blog', 'post', 'article']):
            return 'blog'
        elif any(keyword in domain for keyword in ['forum', 'community', 'board']):
            return 'forum'
        else:
            return 'general'
    
    def extract_with_template(self, soup, template_type):
        """템플릿을 사용한 정보 추출"""
        if template_type not in self.templates:
            template_type = 'general'
        
        template = self.templates[template_type]
        result = {}
        
        # 선택자 기반 추출
        for field, selectors in template['selectors'].items():
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        if field in ['images']:
                            result[field] = []
                            for elem in elements[:10]:  # 최대 10개
                                src = elem.get('src', '')
                                alt = elem.get('alt', '')
                                result[field].append({'src': src, 'alt': alt})
                        else:
                            texts = [elem.get_text(strip=True) for elem in elements]
                            result[field] = texts[0] if len(texts) == 1 else texts
                        break
                except Exception:
                    continue
        
        # 패턴 기반 추출
        if 'patterns' in template:
            text_content = soup.get_text()
            for field, patterns in template['patterns'].items():
                for pattern in patterns:
                    matches = re.findall(pattern, text_content)
                    if matches:
                        result[f'{field}_matches'] = matches[:5]  # 최대 5개
                        break
        
        return result

class AdvancedCrawlerThread(QThread):
    """고급 크롤링 작업을 별도 스레드에서 실행"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, template_type="auto", custom_selectors=None):
        super().__init__()
        self.url = url
        self.template_type = template_type
        self.custom_selectors = custom_selectors or {}
        self.is_running = True
        self.crawler = TemplateCrawler()
        
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
        
        # User-Agent 설정
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # 페이지 가져오기
        response = requests.get(self.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        self.progress_signal.emit("페이지 파싱 중...")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 기본 정보
        data = {
            'url': self.url,
            'timestamp': datetime.now().isoformat(),
            'site_type': 'unknown',
            'extracted_data': {},
            'basic_info': {}
        }
        
        # 사이트 유형 감지
        if self.template_type == "auto":
            detected_type = self.crawler.detect_site_type(self.url, soup)
            data['site_type'] = detected_type
        else:
            data['site_type'] = self.template_type
        
        self.progress_signal.emit(f"사이트 유형: {data['site_type']}")
        
        # 템플릿 기반 추출
        self.progress_signal.emit("템플릿 기반 정보 추출 중...")
        template_data = self.crawler.extract_with_template(soup, data['site_type'])
        data['extracted_data'] = template_data
        
        # 기본 정보 추출
        self.progress_signal.emit("기본 정보 추출 중...")
        basic_info = self.extract_basic_info(soup)
        data['basic_info'] = basic_info
        
        # 커스텀 선택자 적용
        if self.custom_selectors:
            self.progress_signal.emit("커스텀 선택자 적용 중...")
            custom_data = self.extract_with_custom_selectors(soup)
            data['custom_data'] = custom_data
        
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
            'meta_tags': {}
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
                'alt': alt
            })
        
        # 링크
        base_domain = urlparse(self.url).netloc
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(self.url, href)
            link_domain = urlparse(absolute_url).netloc
            
            if link_domain == base_domain:
                info['links'].append({
                    'url': absolute_url,
                    'text': link.get_text(strip=True),
                    'title': link.get('title', '')
                })
        
        # 텍스트
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text_content = soup.get_text(separator=' ', strip=True)
        info['text_content'] = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
        
        return info
    
    def extract_with_custom_selectors(self, soup):
        """커스텀 선택자로 추출"""
        custom_data = {}
        
        for field, selector in self.custom_selectors.items():
            try:
                elements = soup.select(selector)
                if elements:
                    texts = [elem.get_text(strip=True) for elem in elements]
                    custom_data[field] = texts[0] if len(texts) == 1 else texts
            except Exception:
                continue
        
        return custom_data
    
    def stop(self):
        """크롤링 중지"""
        self.is_running = False

class AdvancedWebCrawlerGUI(QMainWindow):
    """고급 웹 크롤러 GUI"""
    
    def __init__(self):
        super().__init__()
        self.crawler_thread = None
        self.template_crawler = TemplateCrawler()
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("🌐 고급 웹 크롤러 GUI")
        self.setGeometry(100, 100, 1400, 900)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # 제목
        title_label = QLabel("고급 웹 크롤러 GUI")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # URL 입력 그룹
        url_group = QGroupBox("URL 입력")
        url_layout = QHBoxLayout(url_group)
        
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(["자동 감지", "쇼핑몰", "뉴스 사이트", "블로그", "포럼/커뮤니티", "일반 웹사이트"])
        
        self.crawl_button = QPushButton("크롤링 시작")
        self.crawl_button.clicked.connect(self.start_crawling)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.template_combo)
        url_layout.addWidget(self.crawl_button)
        
        layout.addWidget(url_group)
        
        # 커스텀 선택자 그룹
        custom_group = QGroupBox("커스텀 선택자")
        custom_layout = QHBoxLayout(custom_group)
        
        custom_label = QLabel("필드명:")
        self.custom_field_input = QLineEdit()
        self.custom_field_input.setPlaceholderText("예: price, author")
        
        selector_label = QLabel("CSS 선택자:")
        self.custom_selector_input = QLineEdit()
        self.custom_selector_input.setPlaceholderText("예: .price, #author")
        
        add_selector_button = QPushButton("추가")
        add_selector_button.clicked.connect(self.add_custom_selector)
        
        custom_layout.addWidget(custom_label)
        custom_layout.addWidget(self.custom_field_input)
        custom_layout.addWidget(selector_label)
        custom_layout.addWidget(self.custom_selector_input)
        custom_layout.addWidget(add_selector_button)
        
        layout.addWidget(custom_group)
        
        # 커스텀 선택자 목록
        self.custom_selectors_list = QListWidget()
        layout.addWidget(QLabel("추가된 커스텀 선택자:"))
        layout.addWidget(self.custom_selectors_list)
        
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
        
        # 템플릿 결과 탭
        self.template_result_text = QTextEdit()
        self.template_result_text.setReadOnly(True)
        self.tab_widget.addTab(self.template_result_text, "템플릿 결과")
        
        # 요약 탭
        self.summary_table = QTableWidget()
        self.tab_widget.addTab(self.summary_table, "요약 정보")
        
        # 버튼 그룹
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("결과 저장")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        
        self.clear_button = QPushButton("초기화")
        self.clear_button.clicked.connect(self.clear_results)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 결과 데이터 저장
        self.crawl_result = None
        self.custom_selectors = {}
        
    def add_custom_selector(self):
        """커스텀 선택자 추가"""
        field = self.custom_field_input.text().strip()
        selector = self.custom_selector_input.text().strip()
        
        if not field or not selector:
            QMessageBox.warning(self, "경고", "필드명과 선택자를 모두 입력해주세요.")
            return
        
        self.custom_selectors[field] = selector
        
        # 리스트에 추가
        item_text = f"{field}: {selector}"
        item = QListWidgetItem(item_text)
        self.custom_selectors_list.addItem(item)
        
        # 입력 필드 초기화
        self.custom_field_input.clear()
        self.custom_selector_input.clear()
        
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
        self.crawl_button.setText("크롤링 중...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("크롤링 준비 중...")
        
        # 템플릿 타입 결정
        template_map = {
            "자동 감지": "auto",
            "쇼핑몰": "shopping",
            "뉴스 사이트": "news",
            "블로그": "blog",
            "포럼/커뮤니티": "forum",
            "일반 웹사이트": "general"
        }
        template_type = template_map[self.template_combo.currentText()]
        
        # 크롤링 스레드 시작
        self.crawler_thread = AdvancedCrawlerThread(url, template_type, self.custom_selectors)
        self.crawler_thread.progress_signal.connect(self.update_progress)
        self.crawler_thread.finished_signal.connect(self.crawling_finished)
        self.crawler_thread.error_signal.connect(self.crawling_error)
        self.crawler_thread.start()
        
    def update_progress(self, message):
        """진행률 업데이트"""
        self.status_label.setText(message)
        
    def crawling_finished(self, result):
        """크롤링 완료"""
        self.crawl_result = result
        
        # UI 상태 복원
        self.crawl_button.setEnabled(True)
        self.crawl_button.setText("크롤링 시작")
        self.progress_bar.setVisible(False)
        self.status_label.setText("크롤링 완료!")
        
        # 결과 표시
        self.display_results(result)
        
        # 저장 버튼 활성화
        self.save_button.setEnabled(True)
        
    def crawling_error(self, error_message):
        """크롤링 에러"""
        self.crawl_button.setEnabled(True)
        self.crawl_button.setText("크롤링 시작")
        self.progress_bar.setVisible(False)
        self.status_label.setText("크롤링 실패!")
        
        QMessageBox.critical(self, "에러", f"크롤링 중 오류가 발생했습니다:\n{error_message}")
        
    def display_results(self, result):
        """결과 표시"""
        # 전체 결과 표시
        self.result_text.setText(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 템플릿 결과 표시
        template_data = result.get('extracted_data', {})
        self.template_result_text.setText(json.dumps(template_data, ensure_ascii=False, indent=2))
        
        # 요약 정보 표시
        self.display_summary(result)
        
    def display_summary(self, result):
        """요약 정보 표시"""
        self.summary_table.setRowCount(10)
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["항목", "값"])
        
        basic_info = result.get('basic_info', {})
        extracted_data = result.get('extracted_data', {})
        
        summary_data = [
            ("URL", result.get('url', '')),
            ("사이트 유형", result.get('site_type', '')),
            ("제목", basic_info.get('title', '')),
            ("설명", basic_info.get('description', '')[:100] + "..." if len(basic_info.get('description', '')) > 100 else basic_info.get('description', '')),
            ("이미지 수", str(len(basic_info.get('images', [])))),
            ("링크 수", str(len(basic_info.get('links', [])))),
            ("추출된 필드 수", str(len(extracted_data))),
            ("커스텀 필드 수", str(len(result.get('custom_data', {})))),
            ("크롤링 시간", result.get('timestamp', '')),
            ("상태", "완료")
        ]
        
        for i, (key, value) in enumerate(summary_data):
            self.summary_table.setItem(i, 0, QTableWidgetItem(key))
            self.summary_table.setItem(i, 1, QTableWidgetItem(value))
        
        self.summary_table.resizeColumnsToContents()
        
    def save_results(self):
        """결과 저장"""
        if not self.crawl_result:
            return
            
        filename = f"advanced_crawl_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.crawl_result, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "성공", f"결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"저장 중 오류가 발생했습니다:\n{str(e)}")
            
    def clear_results(self):
        """결과 초기화"""
        self.result_text.clear()
        self.template_result_text.clear()
        self.summary_table.setRowCount(0)
        self.custom_selectors_list.clear()
        self.crawl_result = None
        self.custom_selectors = {}
        self.save_button.setEnabled(False)
        self.status_label.setText("대기 중...")

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = AdvancedWebCrawlerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
