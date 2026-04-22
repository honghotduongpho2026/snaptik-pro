from flask import Flask, render_template, request, jsonify
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)

# API lấy video TikTok không logo
TIKWM_API = "https://www.tikwm.com/api/"

def get_tiktok_douyin(url):
    try:
        response = requests.post(TIKWM_API, data={'url': url}).json()
        if response.get('code') == 0:
            data = response['data']
            return {
                'title': data.get('title', 'Video TikTok'),
                'thumbnail': 'https://www.tikwm.com' + data.get('cover', ''),
                'video_url': 'https://www.tikwm.com' + data.get('play', ''),
                'music_url': 'https://www.tikwm.com' + data.get('music', ''),
                'platform': 'tiktok'
            }
    except: return None
    return None

def get_youtube_2k_4k(url):
    # Cấu hình lấy chất lượng cao nhất (2K, 4K nếu có)
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
        except Exception as e:
            return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    if not url: return jsonify({"error": "Vui lòng dán link!"}), 400
    
    if "tiktok.com" in url or "douyin.com" in url:
        result = get_tiktok_douyin(url)
        if result: return jsonify(result)
        
    result = get_youtube_2k_4k(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)