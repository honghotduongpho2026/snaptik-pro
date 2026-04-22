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
    name = request.args.get('name', 'file_snaptik')
    if not url: return "Missing URL", 400
    try:
        # Giả lập trình duyệt để tránh bị chặn khi tải file
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = requests.get(url, stream=True, timeout=30, headers=headers)
        return Response(req.iter_content(chunk_size=1024*1024), 
                        content_type=req.headers.get('Content-Type'),
                        headers={"Content-Disposition": f"attachment; filename={name}"})
    except: return "Download Error", 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url', '')
    try:
        if "tiktok.com" in url or "douyin.com" in url:
            resp = requests.post(TIKWM_API, data={'url': url}).json()
            data = resp.get('data', {})
            return jsonify({
                'title': data.get('title', 'Video Media'),
                'thumbnail': fix_url(data.get('cover', '')),
                'video_url': fix_url(data.get('play', '')),
                'music_url': fix_url(data.get('music', '')),
            })
        
        with YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), info['url'])
            return jsonify({
                'title': info.get('title', 'Video Media'),
                'thumbnail': info.get('thumbnail', ''),
                'video_url': info.get('url', ''),
                'music_url': audio_url
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
