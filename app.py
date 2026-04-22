from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)

TIKWM_API = "https://www.tikwm.com/api/"

def fix_url(path):
    if not path: return ""
    return path if path.startswith('http') else f"https://www.tikwm.com{path if path.startswith('/') else '/' + path}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url', '')
    if not url: return jsonify({"error": "No URL"}), 400
    try:
        # TikTok / Douyin: Ưu tiên link HD không logo
        if "tiktok.com" in url or "douyin.com" in url:
            resp = requests.post(TIKWM_API, data={'url': url}, timeout=10).json()
            data = resp.get('data', {})
            if data:
                return jsonify({
                    'title': data.get('title', 'SnapTik Video'),
                    'thumbnail': fix_url(data.get('cover', '')),
                    'video_url': fix_url(data.get('hdplay', data.get('play', ''))), # Lấy bản HD nếu có
                    'music_url': fix_url(data.get('music', '')),
                })
        
        # YouTube: Lấy best quality
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'format': 'bestvideo+bestaudio/best' # Ép lấy chất lượng tốt nhất
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Lọc lấy link MP3 riêng biệt (Audio only) chất lượng cao nhất
            audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), info['url'])
            return jsonify({
                'title': info.get('title', 'Video Content'),
                'thumbnail': info.get('thumbnail', ''),
                'video_url': info['url'], # Link video tổng hợp
                'music_url': audio_url
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
