from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)

TIKWM_API = "https://www.tikwm.com/api/"

def fix_url(path):
    if not path: return ""
    if path.startswith('http'): return path
    clean_path = path if path.startswith('/') else '/' + path
    return f"https://www.tikwm.com{clean_path}"

@app.route('/download_file')
def download_file():
    url = request.args.get('url')
    if not url: return "No URL", 400
    try:
        req = requests.get(url, stream=True, timeout=15)
        return Response(
            req.iter_content(chunk_size=1024*1024),
            content_type=req.headers.get('Content-Type'),
            headers={"Content-Disposition": "attachment; filename=video_snaptik.mp4"}
        )
    except: return "Error", 500

def get_tiktok_douyin(url):
    try:
        response = requests.post(TIKWM_API, data={'url': url}, timeout=10).json()
        if response.get('code') == 0:
            data = response['data']
            return {
                'title': data.get('title', 'Video TikTok'),
                'thumbnail': fix_url(data.get('cover', '')),
                'video_url': fix_url(data.get('play', '')),
                'platform': 'tiktok'
            }
    except: return None

def get_youtube_2k_4k(url):
    ydl_opts = {'format': 'bestvideo+bestaudio/best', 'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'video_url': info.get('url'),
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
    if "tiktok.com" in url or "douyin.com" in url:
        result = get_tiktok_douyin(url)
        if result: return jsonify(result)
    result = get_youtube_2k_4k(url)
    if result: return jsonify(result)
    return jsonify({"error": "Lỗi link!"}), 400

if __name__ == '__main__':
    app.run(debug=True)
