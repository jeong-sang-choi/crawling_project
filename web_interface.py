#!/usr/bin/env python3
"""
웹 크롤러 웹 인터페이스
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import os
import json
from datetime import datetime
from web_crawler import WebCrawler
from advanced_crawler import AdvancedWebCrawler
import threading
import time

app = Flask(__name__)

# 전역 변수로 크롤링 상태 관리
crawling_status = {
    'is_running': False,
    'progress': 0,
    'current_url': '',
    'total_pages': 0,
    'crawled_pages': 0,
    'start_time': None,
    'end_time': None,
    'error': None
}

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>웹 크롤러</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background-color: #007bff;
            transition: width 0.3s ease;
        }
        .results {
            margin-top: 30px;
        }
        .file-list {
            list-style: none;
            padding: 0;
        }
        .file-list li {
            padding: 10px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }
        .success {
            color: #155724;
            background-color: #d4edda;
            border-color: #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 웹 크롤러</h1>
        
        <form id="crawlerForm">
            <div class="form-group">
                <label for="url">크롤링할 URL:</label>
                <input type="url" id="url" name="url" required placeholder="https://example.com">
            </div>
            
            <div class="form-group">
                <label for="crawler_type">크롤러 타입:</label>
                <select id="crawler_type" name="crawler_type">
                    <option value="basic">기본 크롤러</option>
                    <option value="advanced">고급 크롤러</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="max_pages">최대 페이지 수:</label>
                <input type="number" id="max_pages" name="max_pages" value="10" min="1" max="1000">
            </div>
            
            <div class="form-group">
                <label for="max_depth">최대 깊이:</label>
                <input type="number" id="max_depth" name="max_depth" value="2" min="1" max="10">
            </div>
            
            <div class="form-group">
                <label for="delay">지연 시간 (초):</label>
                <input type="number" id="delay" name="delay" value="1" min="0.1" max="10" step="0.1">
            </div>
            
            <button type="submit" id="startBtn">크롤링 시작</button>
            <button type="button" id="stopBtn" disabled>크롤링 중지</button>
        </form>
        
        <div id="status" class="status" style="display: none;">
            <h3>크롤링 상태</h3>
            <div id="statusText"></div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div id="progressText"></div>
        </div>
        
        <div class="results">
            <h3>📁 결과 파일</h3>
            <ul id="fileList" class="file-list">
                <!-- 파일 목록이 여기에 표시됩니다 -->
            </ul>
        </div>
    </div>

    <script>
        let statusInterval;
        
        document.getElementById('crawlerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            startCrawling();
        });
        
        document.getElementById('stopBtn').addEventListener('click', function() {
            stopCrawling();
        });
        
        function startCrawling() {
            const formData = new FormData(document.getElementById('crawlerForm'));
            const data = Object.fromEntries(formData);
            
            fetch('/start_crawling', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    document.getElementById('status').style.display = 'block';
                    updateStatus();
                } else {
                    alert('크롤링 시작 실패: ' + data.error);
                }
            });
        }
        
        function stopCrawling() {
            fetch('/stop_crawling', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    clearInterval(statusInterval);
                }
            });
        }
        
        function updateStatus() {
            statusInterval = setInterval(() => {
                fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusText = document.getElementById('statusText');
                    const progressFill = document.getElementById('progressFill');
                    const progressText = document.getElementById('progressText');
                    
                    if (data.is_running) {
                        statusText.innerHTML = `
                            <strong>크롤링 중...</strong><br>
                            현재 URL: ${data.current_url}<br>
                            진행률: ${data.crawled_pages}/${data.total_pages} 페이지
                        `;
                        
                        const progress = data.total_pages > 0 ? (data.crawled_pages / data.total_pages) * 100 : 0;
                        progressFill.style.width = progress + '%';
                        progressText.textContent = Math.round(progress) + '% 완료';
                    } else {
                        statusText.innerHTML = `
                            <strong>크롤링 완료!</strong><br>
                            총 ${data.crawled_pages}개 페이지 크롤링됨
                        `;
                        progressFill.style.width = '100%';
                        progressText.textContent = '100% 완료';
                        
                        document.getElementById('startBtn').disabled = false;
                        document.getElementById('stopBtn').disabled = true;
                        clearInterval(statusInterval);
                        
                        updateFileList();
                    }
                    
                    if (data.error) {
                        statusText.innerHTML += `<br><span class="error">에러: ${data.error}</span>`;
                    }
                });
            }, 1000);
        }
        
        function updateFileList() {
            fetch('/files')
            .then(response => response.json())
            .then(data => {
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                
                data.files.forEach(file => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <strong>${file.name}</strong> (${file.size} bytes)<br>
                        <small>수정일: ${file.modified}</small>
                        <button onclick="downloadFile('${file.name}')" style="float: right;">다운로드</button>
                    `;
                    fileList.appendChild(li);
                });
            });
        }
        
        function downloadFile(filename) {
            window.open(`/download/${filename}`, '_blank');
        }
        
        // 페이지 로드 시 파일 목록 업데이트
        updateFileList();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start_crawling', methods=['POST'])
def start_crawling():
    global crawling_status
    
    if crawling_status['is_running']:
        return jsonify({'success': False, 'error': '이미 크롤링이 실행 중입니다.'})
    
    try:
        data = request.get_json()
        url = data.get('url')
        crawler_type = data.get('crawler_type', 'basic')
        max_pages = int(data.get('max_pages', 10))
        max_depth = int(data.get('max_depth', 2))
        delay = float(data.get('delay', 1))
        
        # 크롤링 상태 초기화
        crawling_status.update({
            'is_running': True,
            'progress': 0,
            'current_url': url,
            'total_pages': max_pages,
            'crawled_pages': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'error': None
        })
        
        # 별도 스레드에서 크롤링 실행
        def run_crawler():
            global crawling_status
            try:
                if crawler_type == 'basic':
                    crawler = WebCrawler(
                        delay_range=(delay, delay + 1),
                        max_pages=max_pages,
                        output_file=f"web_crawled_{int(time.time())}.json"
                    )
                    crawler.crawl(url, max_depth=max_depth)
                else:
                    config = {
                        'delay_range': (delay, delay + 1),
                        'max_pages': max_pages,
                        'max_depth': max_depth,
                        'max_workers': 2,
                        'respect_robots': True,
                        'output_file': f"advanced_crawled_{int(time.time())}.json"
                    }
                    crawler = AdvancedWebCrawler(config)
                    crawler.crawl(url)
                
                crawling_status.update({
                    'is_running': False,
                    'end_time': datetime.now(),
                    'crawled_pages': len(crawler.crawled_data) if hasattr(crawler, 'crawled_data') else 0
                })
                
            except Exception as e:
                crawling_status.update({
                    'is_running': False,
                    'error': str(e),
                    'end_time': datetime.now()
                })
        
        thread = threading.Thread(target=run_crawler)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop_crawling', methods=['POST'])
def stop_crawling():
    global crawling_status
    crawling_status['is_running'] = False
    return jsonify({'success': True})

@app.route('/status')
def get_status():
    return jsonify(crawling_status)

@app.route('/files')
def get_files():
    files = []
    for filename in os.listdir('.'):
        if filename.endswith('.json') and 'crawled' in filename:
            filepath = os.path.join('.', filename)
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify({'files': files})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    print("🌐 웹 크롤러 인터페이스가 시작되었습니다!")
    print("📱 브라우저에서 http://localhost:5000 으로 접속하세요.")
    app.run(debug=True, host='0.0.0.0', port=5000)
