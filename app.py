from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)  # Hỗ trợ xử lý các yêu cầu từ trình duyệt tốt hơn

# API lấy video TikTok không logo
TIKWM_API = "https://www.tikwm.com/api/"

def get_tiktok_douyin(url):
    try:
        response = requests.post(TIKWM_API, data={'url': url}).json()
        if response.get('code') == 0:
            data = response['data']
            
            # SỬA LỖI: Kiểm tra xem link đã có https chưa trước khi nối chuỗi
            video_url = data.get('play', '')
            if video_url and not video_url.startswith('http'):
                video_url = 'https://www.tikwm.com' + video_url
                
            music_url = data.get('music', '')
            if music_url and not music_url.startswith('http'):
                music_url = 'https://www.tikwm.com' + music_url

            thumbnail = data.get('cover', '')
            if thumbnail and not thumbnail.startswith('http'):
                thumbnail = 'https://www.tikwm.com' + thumbnail

            return {
                'title': data.get('title', 'Video TikTok'),
                'thumbnail': thumbnail,
                'video_url': video_url,
                'music_url': music_url,
                'platform': 'tiktok'
            }
    except Exception as e:
        print(f"Lỗi TikTok: {e}")
        return None
    return None

def get_youtube_2k_4k(url):
    # Cấu hình lấy chất lượng cao nhất
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'force_generic_extractor': False
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
            print(f"Lỗi YouTube: {e}")
            return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Vui lòng dán link!"}), 400
    
    # Xử lý cho TikTok hoặc Douyin
    if "tiktok.com" in url or "douyin.com" in url:
        result = get_tiktok_douyin(url)
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Không thể lấy thông tin video TikTok này!"}), 400
        
    # Xử lý cho YouTube và các nền tảng khác
    result = get_youtube_2k_4k(url)
    if result:
        return jsonify(result)
    
    return jsonify({"error": "Liên kết không được hỗ trợ hoặc có lỗi xảy ra!"}), 400

if __name__ == '__main__':
    # Chạy trên port 5000 cho local, Render sẽ tự dùng Gunicorn cho production
    app.run(debug=True, port=5000)
