import os
import re
import urllib.parse
import mimetypes
from flask import Flask, render_template, request, jsonify, Response, stream_template
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'your-secret-key-here')

class FileScanner:
    def __init__(self):
        self.file_extensions = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'executables': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.apk'],
            'others': []
        }

    def get_file_type(self, url):
        """Determine file type based on URL extension"""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        for category, extensions in self.file_extensions.items():
            if any(path.endswith(ext) for ext in extensions):
                return category
        return 'others'

    def extract_filename(self, url):
        """Extract filename from URL"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        if not filename or '.' not in filename:
            # Try to get from query parameters
            query_params = urllib.parse.parse_qs(parsed_url.query)
            for param in ['filename', 'file', 'name']:
                if param in query_params:
                    return query_params[param][0]
            # Fallback to last part of path
            parts = path.strip('/').split('/')
            return parts[-1] if parts and parts[-1] else 'unknown_file'
        return filename

    def get_file_size(self, url):
        """Get file size without downloading the entire file"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                content_length = response.headers.get('content-length')
                if content_length:
                    size_bytes = int(content_length)
                    return self.format_file_size(size_bytes)
        except:
            pass
        return 'Unknown'

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"

    def is_direct_file_link(self, url):
        """Check if URL points to a direct file"""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Check for file extension
        for extensions in self.file_extensions.values():
            if any(path.endswith(ext) for ext in extensions):
                return True
        
        # Check Content-Type header
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            content_type = response.headers.get('content-type', '').lower()
            
            file_types = ['image/', 'video/', 'audio/', 'application/pdf', 'application/zip', 
                         'application/octet-stream', 'application/x-', 'text/plain']
            return any(content_type.startswith(ft) for ft in file_types)
        except:
            return False

    def scan_url(self, url):
        """Scan URL and extract all downloadable file links"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = set()
            
            # Extract from <a> tags
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    if self.is_direct_file_link(absolute_url):
                        links.add(absolute_url)
            
            # Extract from <img> tags
            for img in soup.find_all('img', src=True):
                src = img.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    links.add(absolute_url)
            
            # Extract from <video> and <source> tags
            for video in soup.find_all(['video', 'source'], src=True):
                src = video.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    links.add(absolute_url)
            
            # Extract from <audio> tags
            for audio in soup.find_all('audio', src=True):
                src = audio.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    links.add(absolute_url)
            
            # Process found links
            files = []
            for link in links:
                try:
                    file_info = {
                        'url': link,
                        'filename': self.extract_filename(link),
                        'type': self.get_file_type(link),
                        'size': self.get_file_size(link)
                    }
                    files.append(file_info)
                except Exception as e:
                    continue
            
            return {
                'success': True,
                'files': files,
                'total_files': len(files)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error scanning URL: {str(e)}',
                'files': [],
                'total_files': 0
            }

scanner = FileScanner()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_url():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'})
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return jsonify({'success': False, 'error': 'Invalid URL format'})
    except:
        return jsonify({'success': False, 'error': 'Invalid URL format'})
    
    # Scan URL for files
    result = scanner.scan_url(url)
    return jsonify(result)

@app.route('/download')
def download_file():
    url = request.args.get('url')
    filename = request.args.get('filename')
    
    if not url:
        return "URL parameter is required", 400
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get content type
        content_type = response.headers.get('content-type', 'application/octet-stream')
        
        # Set filename
        if not filename:
            filename = scanner.extract_filename(url)
        
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            mimetype=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': 'no-cache'
            }
        )
        
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
