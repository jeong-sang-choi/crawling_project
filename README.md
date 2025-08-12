# 웹 크롤러 프로젝트

구글 봇과 같은 웹 크롤러를 만드는 프로젝트입니다. 다양한 기능을 가진 크롤러들을 제공합니다.

## 🚀 주요 기능

### 기본 크롤러 (`web_crawler.py`)
- 웹페이지 수집 및 파싱
- 링크 추출 및 순회
- 봇 감지 방지 (랜덤 지연, User-Agent 변경)
- JSON 형태로 데이터 저장
- 로깅 시스템

### 고급 크롤러 (`advanced_crawler.py`)
- 멀티스레드 지원
- robots.txt 준수
- 캐시 시스템
- 더 상세한 데이터 추출 (이미지, 헤더, 메타 태그 등)
- 중복 콘텐츠 감지
- 에러 처리 및 복구

## 📦 설치

1. 가상환경 활성화:
```bash
# Windows
Scripts\activate

# Linux/Mac
source Scripts/activate
```

2. 필요한 라이브러리 설치:
```bash
pip install -r requirements.txt
```

## 🛠️ 사용법

### 기본 크롤러 사용

```python
from web_crawler import WebCrawler

# 크롤러 생성
crawler = WebCrawler(
    delay_range=(1, 3),  # 1-3초 지연
    max_pages=100,       # 최대 100페이지
    output_file="data.json"
)

# 크롤링 시작
crawler.crawl("https://example.com", max_depth=3)

# 통계 확인
stats = crawler.get_statistics()
print(stats)
```

### 고급 크롤러 사용

```python
from advanced_crawler import AdvancedWebCrawler

# 설정
config = {
    'delay_range': (1, 2),
    'max_pages': 50,
    'max_depth': 2,
    'max_workers': 3,
    'respect_robots': True,
    'output_file': 'advanced_data.json'
}

# 크롤러 생성 및 실행
crawler = AdvancedWebCrawler(config)
crawler.crawl("https://example.com")
```

### 예시 실행

```bash
python example_usage.py
```

## 📊 수집되는 데이터

### 기본 크롤러
- URL
- 제목
- 텍스트 내용
- 메타 설명
- 메타 키워드
- 링크 목록

### 고급 크롤러
- 기본 크롤러 데이터 +
- 이미지 정보
- 헤더 태그 (h1-h6)
- 단어 수
- 콘텐츠 해시
- 메타 robots 태그

## ⚙️ 설정 옵션

### 기본 크롤러 설정
- `delay_range`: 요청 간 지연 시간 (초)
- `max_pages`: 최대 크롤링할 페이지 수
- `output_file`: 결과 저장 파일명

### 고급 크롤러 설정
- `delay_range`: 요청 간 지연 시간 (초)
- `max_pages`: 최대 크롤링할 페이지 수
- `max_depth`: 최대 크롤링 깊이
- `max_workers`: 동시 작업 스레드 수
- `timeout`: 요청 타임아웃 (초)
- `respect_robots`: robots.txt 준수 여부
- `output_file`: 결과 저장 파일명
- `cache_file`: 캐시 파일명

## 🔧 커스터마이징

### 커스텀 파싱 로직 추가

```python
class CustomCrawler(WebCrawler):
    def parse_page(self, url, html_content):
        # 기본 파싱
        page_data = super().parse_page(url, html_content)
        
        # 커스텀 로직 추가
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 특정 요소 추출
        page_data['custom_data'] = {
            'specific_elements': [elem.get_text() for elem in soup.find_all('div', class_='target')]
        }
        
        return page_data
```

## 📝 주의사항

1. **웹사이트 이용약관 준수**: 크롤링하기 전에 해당 웹사이트의 이용약관을 확인하세요.
2. **robots.txt 준수**: 웹사이트의 robots.txt 파일을 확인하고 준수하세요.
3. **적절한 지연**: 서버에 과부하를 주지 않도록 적절한 지연 시간을 설정하세요.
4. **개인정보 보호**: 개인정보가 포함된 데이터는 수집하지 마세요.

## 🐛 문제 해결

### 일반적인 문제들

1. **연결 오류**: 네트워크 연결을 확인하고 타임아웃 설정을 조정하세요.
2. **봇 차단**: User-Agent를 변경하거나 지연 시간을 늘려보세요.
3. **메모리 부족**: `max_pages` 설정을 줄이거나 `max_workers`를 줄여보세요.

### 로그 확인

크롤러 실행 중 발생하는 문제는 로그 파일에서 확인할 수 있습니다:
- `crawler.log`: 기본 크롤러 로그
- `advanced_crawler.log`: 고급 크롤러 로그

## 📄 라이선스

이 프로젝트는 교육 목적으로 만들어졌습니다. 상업적 사용 시에는 해당 웹사이트의 이용약관을 확인하세요.

## 🤝 기여

버그 리포트나 기능 제안은 언제든 환영합니다!

---

**⚠️ 면책 조항**: 이 도구는 교육 목적으로만 사용되어야 합니다. 웹사이트 크롤링 시 해당 사이트의 이용약관과 robots.txt를 반드시 준수하세요.
