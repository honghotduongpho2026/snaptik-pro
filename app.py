from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)

TIKWM_API = "https://www.tikwm.com/api/"

def fix_url(path):
    if not path: return ""
    return path if path.startswith('http') else f"https://www.tikwm.com{path if path.startswith('/') else '/' + path}"

@app.route('/download_file')
def download_file():
    url = request.args.get('url')
    filename = request.args.get('name', 'video_snaptik.mp4')
    if not url: return "Missing URL", 400
    try:
        req = requests.get(url, stream=True, timeout=30)
        return Response(req.iter_content(chunk_size=1024*1024), 
                        content_type=req.headers.get('Content-Type'),
                        headers={"Content-Disposition": f"attachment; filename={filename}"})
    except: return "Download Error", 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url', '')
    try:
        # Xử lý TikTok & Douyin qua TikWM
        if "tiktok.com" in url or "douyin.com" in url:
            resp = requests.post(TIKWM_API, data={'url': url}).json()
            data = resp['data']
            return jsonify({
                'title': data.get('title', 'Video TikTok/Douyin'),
                'thumbnail': fix_url(data.get('cover', '')),
                'video_url': fix_url(data.get('play', '')),
                'music_url': fix_url(data.get('music', '')),
                'platform': 'tiktok'
            })
        
        # Xử lý YouTube & các nền tảng khác qua yt-dlp
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'noplaylist': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Tìm link audio riêng nếu có
            audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), info['url'])
            return jsonify({
                'title': info.get('title', 'Video Youtube'),
                'thumbnail': info.get('thumbnail', ''),
                'video_url': info.get('url', ''),
                'music_url': audio_url,
                'platform': 'youtube'
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
