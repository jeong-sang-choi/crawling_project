#!/usr/bin/env python3
"""
GUI 웹 크롤러 - 1단계: 기본 기능
"""

import sys
import json
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QProgressBar, QComboBox, QGroupBox,
                            QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import time

class CrawlerThread(QThread):
    """크롤링 작업을 별도 스레드에서 실행"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, crawler_type="basic"):
        super().__init__()
        self.url = url
        self.crawler_type = crawler_type
        self.is_running = True
        
    def run(self):
        try:
            self.progress_signal.emit("크롤링 시작...")
            
            # 기본 크롤러 실행
            if self.crawler_type == "basic":
                result = self.basic_crawl()
            else:
                result = self.advanced_crawl()
                
            if self.is_running:
                self.finished_signal.emit(result)
                
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def basic_crawl(self):
        """기본 크롤링"""
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
        
        # 기본 정보 추출
        data = {
            'url': self.url,
            'timestamp': datetime.now().isoformat(),
            'title': '',
            'description': '',
            'keywords': [],
            'images': [],
            'links': [],
            'text_content': '',
            'headers': {},
            'meta_tags': {}
        }
        
        # 제목 추출
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)
        
        # 메타 태그 추출
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                data['description'] = content
            elif name == 'keywords':
                data['keywords'] = [kw.strip() for kw in content.split(',')]
            else:
                data['meta_tags'][name] = content
        
        # 헤더 태그 추출
        for i in range(1, 7):
            headers = soup.find_all(f'h{i}')
            data['headers'][f'h{i}'] = [h.get_text(strip=True) for h in headers]
        
        # 이미지 추출
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            data['images'].append({
                'src': urljoin(self.url, src),
                'alt': alt
            })
        
        # 링크 추출 (같은 도메인만)
        base_domain = urlparse(self.url).netloc
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(self.url, href)
            link_domain = urlparse(absolute_url).netloc
            
            if link_domain == base_domain:
                data['links'].append({
                    'url': absolute_url,
                    'text': link.get_text(strip=True),
                    'title': link.get('title', '')
                })
        
        # 텍스트 내용 추출
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text_content = soup.get_text(separator=' ', strip=True)
        data['text_content'] = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
        
        self.progress_signal.emit("크롤링 완료!")
        return data
    
    def advanced_crawl(self):
        """고급 크롤링 (기본 + 추가 정보)"""
        basic_data = self.basic_crawl()
        
        # 추가 정보 수집
        self.progress_signal.emit("고급 정보 수집 중...")
        
        # 단어 수 계산
        basic_data['word_count'] = len(basic_data['text_content'].split())
        
        # 링크 수 계산
        basic_data['link_count'] = len(basic_data['links'])
        
        # 이미지 수 계산
        basic_data['image_count'] = len(basic_data['images'])
        
        return basic_data
    
    def stop(self):
        """크롤링 중지"""
        self.is_running = False

class WebCrawlerGUI(QMainWindow):
    """웹 크롤러 GUI 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.crawler_thread = None
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("🌐 웹 크롤러 GUI")
        self.setGeometry(100, 100, 1200, 800)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # 제목
        title_label = QLabel("웹 크롤러 GUI")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # URL 입력 그룹
        url_group = QGroupBox("URL 입력")
        url_layout = QHBoxLayout(url_group)
        
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        
        self.crawler_type_combo = QComboBox()
        self.crawler_type_combo.addItems(["기본 크롤링", "고급 크롤링"])
        
        self.crawl_button = QPushButton("크롤링 시작")
        self.crawl_button.clicked.connect(self.start_crawling)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.crawler_type_combo)
        url_layout.addWidget(self.crawl_button)
        
        layout.addWidget(url_group)
        
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
        self.tab_widget.addTab(self.result_text, "크롤링 결과")
        
        # 요약 탭
        self.summary_table = QTableWidget()
        self.tab_widget.addTab(self.summary_table, "요약 정보")
        
        # 상세 정보 탭
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.tab_widget.addTab(self.detail_text, "상세 정보")
        
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
        self.progress_bar.setRange(0, 0)  # 무한 진행률
        self.status_label.setText("크롤링 준비 중...")
        
        # 크롤러 타입 결정
        crawler_type = "basic" if self.crawler_type_combo.currentText() == "기본 크롤링" else "advanced"
        
        # 크롤링 스레드 시작
        self.crawler_thread = CrawlerThread(url, crawler_type)
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
        # JSON 결과 표시
        self.result_text.setText(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 요약 정보 표시
        self.display_summary(result)
        
        # 상세 정보 표시
        self.display_details(result)
        
    def display_summary(self, result):
        """요약 정보 표시"""
        self.summary_table.setRowCount(8)
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["항목", "값"])
        
        summary_data = [
            ("URL", result.get('url', '')),
            ("제목", result.get('title', '')),
            ("설명", result.get('description', '')[:100] + "..." if len(result.get('description', '')) > 100 else result.get('description', '')),
            ("키워드 수", str(len(result.get('keywords', [])))),
            ("이미지 수", str(len(result.get('images', [])))),
            ("링크 수", str(len(result.get('links', [])))),
            ("단어 수", str(result.get('word_count', 0))),
            ("크롤링 시간", result.get('timestamp', ''))
        ]
        
        for i, (key, value) in enumerate(summary_data):
            self.summary_table.setItem(i, 0, QTableWidgetItem(key))
            self.summary_table.setItem(i, 1, QTableWidgetItem(value))
        
        self.summary_table.resizeColumnsToContents()
        
    def display_details(self, result):
        """상세 정보 표시"""
        details = []
        
        # 헤더 정보
        details.append("=== 헤더 정보 ===")
        for level, headers in result.get('headers', {}).items():
            if headers:
                details.append(f"\n{level.upper()}:")
                for header in headers[:5]:  # 상위 5개만
                    details.append(f"  - {header}")
        
        # 이미지 정보
        details.append("\n\n=== 이미지 정보 ===")
        for i, img in enumerate(result.get('images', [])[:10]):  # 상위 10개만
            details.append(f"{i+1}. {img.get('src', '')}")
            if img.get('alt'):
                details.append(f"   Alt: {img.get('alt')}")
        
        # 링크 정보
        details.append("\n\n=== 링크 정보 ===")
        for i, link in enumerate(result.get('links', [])[:10]):  # 상위 10개만
            details.append(f"{i+1}. {link.get('text', '')}")
            details.append(f"   URL: {link.get('url', '')}")
        
        self.detail_text.setText('\n'.join(details))
        
    def save_results(self):
        """결과 저장"""
        if not self.crawl_result:
            return
            
        filename = f"crawl_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.crawl_result, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "성공", f"결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"저장 중 오류가 발생했습니다:\n{str(e)}")
            
    def clear_results(self):
        """결과 초기화"""
        self.result_text.clear()
        self.summary_table.setRowCount(0)
        self.detail_text.clear()
        self.crawl_result = None
        self.save_button.setEnabled(False)
        self.status_label.setText("대기 중...")

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 모던한 스타일
    
    window = WebCrawlerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
