from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import requests

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
        # Ưu tiên sử dụng TikWM API cho TikTok và Douyin để lấy ảnh/video nhanh nhất
        resp = requests.post(TIKWM_API, data={'url': url}, timeout=10).json()
        data = resp.get('data', {})
        if data:
            return jsonify({
                'title': data.get('title', 'SnapTik Video'),
                'thumbnail': fix_url(data.get('cover', '')),
                'video_url': fix_url(data.get('play', '')),
                'music_url': fix_url(data.get('music', '')),
            })
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_file')
def download_file():
    url = request.args.get('url')
    name = request.args.get('name', 'snaptik_file')
    if not url: return "Lỗi link", 400
    req = requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
    return Response(req.iter_content(chunk_size=1024), 
                    content_type=req.headers.get('Content-Type'),
                    headers={"Content-Disposition": f"attachment; filename={name}"})

if __name__ == '__main__':
    app.run(debug=True)
