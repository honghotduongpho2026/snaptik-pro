from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)

TIKWM_API = "https://www.tikwm.com/api/"

def fix_url(path):
    """Sửa lỗi dính link DNS và đảm bảo link có đầy đủ https"""
    if not path: return ""
    if path.startswith('http'): return path
    clean_path = path if path.startswith('/') else '/' + path
    return f"https://www.tikwm.com{clean_path}"

@app.route('/download_file')
def download_file():
    """Hàm quan trọng: Ép trình duyệt tự động tải xuống thay vì mở trình phát"""
    url = request.args.get('url')
    if not url: return "Không tìm thấy liên kết", 400
    
    try:
        # Tải dữ liệu từ server gốc (TikTok/Douyin)
        req = requests.get(url, stream=True, timeout=15)
        
        # Gửi dữ liệu về trình duyệt kèm Header 'attachment' để kích hoạt tự động tải
        return Response(
            req.iter_content(chunk_size=1024*1024),
            content_type=req.headers.get('Content-Type'),
            headers={"Content-Disposition": "attachment; filename=video_snaptik.mp4"}
        )
    except Exception as e:
        return f"Lỗi máy chủ tải file: {str(e)}", 500

def get_tiktok_douyin(url):
    try:
        response = requests.post(TIKWM_API, data={'url': url}, timeout=10).json()
        if response.get('code') == 0:
            data = response['data']
            return {
                'title': data.get('title', 'Video TikTok'),
                'thumbnail': fix_url(data.get('cover', '')),
                'video_url': fix_url(data.get('play', '')),
                'music_url': fix_url(data.get('music', '')),
                'platform': 'tiktok'
            }
    except: return None
    return None

def get_youtube_2k_4k(url):
    ydl_opts = {'format': 'bestvideo+bestaudio/best', 'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'video_url': info.get('url'),
                'music_url': info.get('url'),
                'platform': 'youtube'
            }
        except: return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url', '')
    if not url: return jsonify({"error": "Vui lòng dán link!"}), 400
    
    if "tiktok.com" in url or "douyin.com" in url:
        result = get_tiktok_douyin(url)
        if result: return jsonify(result)
        
    result = get_youtube_2k_4k(url)
    if result: return jsonify(result)
    
    return jsonify({"error": "Liên kết không hỗ trợ hoặc lỗi!"}), 400

if __name__ == '__main__':
    app.run(debug=True)
