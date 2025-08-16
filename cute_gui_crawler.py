#!/usr/bin/env python3
"""
귀여운 GUI 웹 크롤러 🕷️✨
"""

import sys
import json
import re
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QProgressBar, QComboBox, QGroupBox,
                            QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QCheckBox, QListWidget, QListWidgetItem, QSplitter,
                            QFrame, QScrollArea, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QLinearGradient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import time

class CuteCrawlerThread(QThread):
    """귀여운 크롤링 작업을 별도 스레드에서 실행"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    animation_signal = pyqtSignal(int)  # 애니메이션용
    
    def __init__(self, url, options=None):
        super().__init__()
        self.url = url
        self.options = options or {}
        self.is_running = True
        
    def run(self):
        try:
            self.progress_signal.emit("🕷️ 크롤링 준비 중...")
            self.animation_signal.emit(1)
            time.sleep(0.5)
            
            self.progress_signal.emit("🌐 웹페이지에 접속 중...")
            self.animation_signal.emit(2)
            time.sleep(0.5)
            
            result = self.cute_crawl()
            
            if self.is_running:
                self.progress_signal.emit("✨ 크롤링 완료!")
                self.animation_signal.emit(100)
                self.finished_signal.emit(result)
                
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def cute_crawl(self):
        """귀여운 크롤링"""
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
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 귀여운 데이터 구조
        data = {
            'url': self.url,
            'timestamp': datetime.now().isoformat(),
            'crawler_mood': '😊',
            'extracted_data': {},
            'basic_info': {},
            'cute_stats': {}
        }
        
        # 기본 정보 추출
        basic_info = self.extract_basic_info(soup)
        data['basic_info'] = basic_info
        
        # 귀여운 통계
        data['cute_stats'] = {
            'total_images': len(basic_info.get('images', [])),
            'total_links': len(basic_info.get('links', [])),
            'word_count': len(basic_info.get('text_content', '').split()),
            'emoji_count': len(re.findall(r'[😀-🙏🌀-🗿]', basic_info.get('text_content', ''))),
            'happy_words': len(re.findall(r'좋|행복|즐거|재미|멋|최고|완벽', basic_info.get('text_content', ''))),
            'page_size': len(response.content),
            'crawler_rating': '⭐⭐⭐⭐⭐' if len(basic_info.get('text_content', '')) > 100 else '⭐⭐⭐'
        }
        
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
    
    def stop(self):
        """크롤링 중지"""
        self.is_running = False

class CuteButton(QPushButton):
    """귀여운 버튼 클래스"""
    def __init__(self, text, icon_emoji="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6B9D, stop:1 #C44569);
                border: 2px solid #FF6B9D;
                border-radius: 15px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8EAB, stop:1 #FF6B9D);
                border: 2px solid #FF8EAB;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #C44569, stop:1 #FF6B9D);
            }
            QPushButton:disabled {
                background: #CCCCCC;
                border: 2px solid #CCCCCC;
                color: #666666;
            }
        """)
        if icon_emoji:
            self.setText(f"{icon_emoji} {text}")

class CuteGroupBox(QGroupBox):
    """귀여운 그룹박스 클래스"""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #FF6B9D;
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #FFF0F5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #FFF0F5;
            }
        """)

class CuteLineEdit(QLineEdit):
    """귀여운 입력 필드 클래스"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #FF6B9D;
                background-color: #FFF0F5;
            }
        """)

class CuteWebCrawlerGUI(QMainWindow):
    """귀여운 웹 크롤러 GUI"""
    
    def __init__(self):
        super().__init__()
        self.crawler_thread = None
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("🕷️✨ 귀여운 웹 크롤러 ✨🕷️")
        self.setGeometry(100, 100, 1200, 800)
        
        # 귀여운 스타일 적용
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFE5F0, stop:1 #FFF0F5);
            }
            QLabel {
                color: #FF6B9D;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFB6C1, stop:1 #FF8EAB);
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6B9D, stop:1 #C44569);
            }
            QTextEdit {
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                padding: 10px;
                background-color: white;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QProgressBar {
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                text-align: center;
                background-color: #FFF0F5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6B9D, stop:1 #C44569);
                border-radius: 8px;
            }
            QTableWidget {
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                background-color: white;
                gridline-color: #FFB6C1;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6B9D, stop:1 #C44569);
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 귀여운 제목
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B9D, stop:1 #FF8EAB);
                border-radius: 20px;
                padding: 20px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("🕷️✨ 귀여운 웹 크롤러 ✨🕷️")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; margin: 10px;")
        
        subtitle_label = QLabel("웹사이트를 귀엽게 크롤링해요! 🎀")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: white; margin: 5px;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        layout.addWidget(title_frame)
        
        # URL 입력 그룹
        url_group = CuteGroupBox("🌐 크롤링할 웹사이트 주소")
        url_layout = QHBoxLayout(url_group)
        url_layout.setSpacing(10)
        
        url_label = QLabel("URL:")
        self.url_input = CuteLineEdit("https://example.com")
        
        self.crawl_button = CuteButton("크롤링 시작", "🕷️")
        self.crawl_button.clicked.connect(self.start_crawling)
        
        self.stop_button = CuteButton("중지", "⏹️")
        self.stop_button.clicked.connect(self.stop_crawling)
        self.stop_button.setEnabled(False)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(self.crawl_button)
        url_layout.addWidget(self.stop_button)
        
        layout.addWidget(url_group)
        
        # 진행률 표시
        progress_group = CuteGroupBox("📊 진행 상황")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #FFB6C1;
                border-radius: 15px;
                text-align: center;
                background-color: #FFF0F5;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6B9D, stop:1 #C44569);
                border-radius: 13px;
            }
        """)
        
        self.status_label = QLabel("🦋 크롤링 준비 완료! 시작해볼까요?")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FF6B9D;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #FFF0F5;
                border-radius: 10px;
                border: 2px solid #FFB6C1;
            }
        """)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 결과 탭
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.tab_widget.addTab(self.result_text, "📄 전체 결과")
        
        # 귀여운 통계 탭
        self.stats_table = QTableWidget()
        self.tab_widget.addTab(self.stats_table, "📊 귀여운 통계")
        
        # 요약 탭
        self.summary_table = QTableWidget()
        self.tab_widget.addTab(self.summary_table, "🎀 요약 정보")
        
        # 버튼 그룹
        button_group = CuteGroupBox("🎮 조작 패널")
        button_layout = QHBoxLayout(button_group)
        
        self.save_button = CuteButton("결과 저장", "💾")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        
        self.clear_button = CuteButton("초기화", "🔄")
        self.clear_button.clicked.connect(self.clear_results)
        
        self.export_button = CuteButton("Excel 내보내기", "📊")
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setEnabled(False)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        
        layout.addWidget(button_group)
        
        # 결과 데이터 저장
        self.crawl_result = None
        
    def setup_animations(self):
        """애니메이션 설정"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.current_emoji = 0
        self.emoji_list = ["🦋", "🕷️", "✨", "🎀", "🌸", "💖", "🦄", "🌈"]
        
    def update_animation(self):
        """애니메이션 업데이트"""
        self.current_emoji = (self.current_emoji + 1) % len(self.emoji_list)
        if hasattr(self, 'status_label'):
            current_text = self.status_label.text()
            if "크롤링 중" in current_text:
                base_text = current_text.split(" ")[0]
                self.status_label.setText(f"{base_text} {self.emoji_list[self.current_emoji]} 크롤링 중...")
        
    def start_crawling(self):
        """크롤링 시작"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력해주세요! 🥺")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        
        # UI 상태 변경
        self.crawl_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.status_label.setText("🦋 크롤링 준비 중...")
        
        # 애니메이션 시작
        self.animation_timer.start(500)
        
        # 크롤링 스레드 시작
        self.crawler_thread = CuteCrawlerThread(url)
        self.crawler_thread.progress_signal.connect(self.update_progress)
        self.crawler_thread.finished_signal.connect(self.crawling_finished)
        self.crawler_thread.error_signal.connect(self.crawling_error)
        self.crawler_thread.animation_signal.connect(self.update_progress_animation)
        self.crawler_thread.start()
        
    def stop_crawling(self):
        """크롤링 중지"""
        if self.crawler_thread:
            self.crawler_thread.stop()
            self.crawler_thread.wait()
        
        self.crawl_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.animation_timer.stop()
        self.status_label.setText("🦋 크롤링이 중지되었어요!")
        
    def update_progress(self, message):
        """진행률 업데이트"""
        self.status_label.setText(message)
        
    def update_progress_animation(self, value):
        """진행률 애니메이션 업데이트"""
        self.progress_bar.setValue(value)
        
    def crawling_finished(self, result):
        """크롤링 완료"""
        self.crawl_result = result
        
        # UI 상태 복원
        self.crawl_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.animation_timer.stop()
        self.status_label.setText("✨ 크롤링 완료! 잘했어요! 🎉")
        
        # 결과 표시
        self.display_results(result)
        
        # 저장 버튼 활성화
        self.save_button.setEnabled(True)
        self.export_button.setEnabled(True)
        
    def crawling_error(self, error_message):
        """크롤링 에러"""
        self.crawl_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.animation_timer.stop()
        self.status_label.setText("😢 크롤링에 실패했어요...")
        
        QMessageBox.critical(self, "에러", f"크롤링 중 오류가 발생했어요! 🥺\n{error_message}")
        
    def display_results(self, result):
        """결과 표시"""
        # 전체 결과 표시
        self.result_text.setText(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 귀여운 통계 표시
        self.display_cute_stats(result)
        
        # 요약 정보 표시
        self.display_summary(result)
        
    def display_cute_stats(self, result):
        """귀여운 통계 표시"""
        stats = result.get('cute_stats', {})
        
        self.stats_table.setRowCount(8)
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["📊 통계 항목", "🎀 값"])
        
        stats_data = [
            ("🖼️ 총 이미지 수", str(stats.get('total_images', 0))),
            ("🔗 총 링크 수", str(stats.get('total_links', 0))),
            ("📝 총 단어 수", str(stats.get('word_count', 0))),
            ("😊 이모지 수", str(stats.get('emoji_count', 0))),
            ("💖 행복한 단어 수", str(stats.get('happy_words', 0))),
            ("📦 페이지 크기", f"{stats.get('page_size', 0):,} bytes"),
            ("⭐ 크롤러 평점", stats.get('crawler_rating', '⭐⭐⭐')),
            ("😊 크롤러 기분", result.get('crawler_mood', '😊'))
        ]
        
        for i, (key, value) in enumerate(stats_data):
            self.stats_table.setItem(i, 0, QTableWidgetItem(key))
            self.stats_table.setItem(i, 1, QTableWidgetItem(value))
        
        self.stats_table.resizeColumnsToContents()
        
    def display_summary(self, result):
        """요약 정보 표시"""
        basic_info = result.get('basic_info', {})
        
        self.summary_table.setRowCount(6)
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["🎀 항목", "✨ 값"])
        
        summary_data = [
            ("🌐 URL", result.get('url', '')),
            ("📝 제목", basic_info.get('title', '')),
            ("📄 설명", basic_info.get('description', '')[:100] + "..." if len(basic_info.get('description', '')) > 100 else basic_info.get('description', '')),
            ("🖼️ 이미지 수", str(len(basic_info.get('images', [])))),
            ("🔗 링크 수", str(len(basic_info.get('links', [])))),
            ("⏰ 크롤링 시간", result.get('timestamp', ''))
        ]
        
        for i, (key, value) in enumerate(summary_data):
            self.summary_table.setItem(i, 0, QTableWidgetItem(key))
            self.summary_table.setItem(i, 1, QTableWidgetItem(value))
        
        self.summary_table.resizeColumnsToContents()
        
    def save_results(self):
        """결과 저장"""
        if not self.crawl_result:
            return
            
        filename = f"cute_crawl_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.crawl_result, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "성공", f"결과가 {filename}에 저장되었어요! 💾✨")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"저장 중 오류가 발생했어요! 🥺\n{str(e)}")
            
    def export_to_excel(self):
        """Excel로 내보내기"""
        if not self.crawl_result:
            return
            
        try:
            import pandas as pd
            
            # 데이터 준비
            data = []
            basic_info = self.crawl_result.get('basic_info', {})
            stats = self.crawl_result.get('cute_stats', {})
            
            # 기본 정보
            data.append(['URL', self.crawl_result.get('url', '')])
            data.append(['제목', basic_info.get('title', '')])
            data.append(['설명', basic_info.get('description', '')])
            data.append(['이미지 수', stats.get('total_images', 0)])
            data.append(['링크 수', stats.get('total_links', 0)])
            data.append(['단어 수', stats.get('word_count', 0)])
            data.append(['이모지 수', stats.get('emoji_count', 0)])
            data.append(['행복한 단어 수', stats.get('happy_words', 0)])
            data.append(['크롤러 평점', stats.get('crawler_rating', '⭐⭐⭐')])
            
            # DataFrame 생성
            df = pd.DataFrame(data, columns=['항목', '값'])
            
            # 파일 저장
            filename = f"cute_crawl_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "성공", f"Excel 파일이 {filename}에 저장되었어요! 📊✨")
            
        except ImportError:
            QMessageBox.warning(self, "경고", "Excel 내보내기를 위해 pandas를 설치해주세요! 📦\npip install pandas openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"Excel 내보내기 중 오류가 발생했어요! 🥺\n{str(e)}")
            
    def clear_results(self):
        """결과 초기화"""
        self.result_text.clear()
        self.stats_table.setRowCount(0)
        self.summary_table.setRowCount(0)
        self.crawl_result = None
        self.save_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.status_label.setText("🦋 크롤링 준비 완료! 시작해볼까요?")

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 귀여운 폰트 설정
    font = QFont("Arial", 9)
    app.setFont(font)
    
    window = CuteWebCrawlerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
