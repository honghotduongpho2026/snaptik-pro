from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)

TIKWM_API = "https://www.tikwm.com/api/"

def fix_url(path):
    """Hàm xử lý thông minh: Nếu link có http rồi thì giữ nguyên, nếu chưa thì mới nối domain"""
    if not path:
        return ""
    if path.startswith('http'):
        return path
    # Đảm bảo path bắt đầu bằng / để nối chuỗi không bị lỗi
    clean_path = path if path.startswith('/') else '/' + path
    return f"https://www.tikwm.com{clean_path}"

def get_tiktok_douyin(url):
    try:
        response = requests.post(TIKWM_API, data={'url': url}, timeout=10).json()
        if response.get('code') == 0:
            data = response['data']
            return {
                'title': data.get('title', 'Video TikTok'),
                'thumbnail': fix_url(data.get('cover', '')),
                'video_url': fix_url(data.get('play', '')), # Sửa lỗi DNS tại đây
                'music_url': fix_url(data.get('music', '')),
                'platform': 'tiktok'
            }
    except Exception as e:
        print(f"Lỗi TikTok: {e}")
    return None

def get_youtube_2k_4k(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'no_warnings': True
    }
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
        except:
            return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url', '')
    if not url:
        return jsonify({"error": "Vui lòng dán link!"}), 400
    
    if "tiktok.com" in url or "douyin.com" in url:
        result = get_tiktok_douyin(url)
        if result: return jsonify(result)
        
    result = get_youtube_2k_4k(url)
    if result: return jsonify(result)
    
    return jsonify({"error": "Không lấy được link video này!"}), 400

if __name__ == '__main__':
    app.run(debug=True)
