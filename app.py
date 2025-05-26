from flask import Flask, request, send_file, jsonify, render_template
import io, logging
from google.cloud import texttospeech
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, template_folder="templates")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo client TTS
tts_client = texttospeech.TextToSpeechClient()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tts", methods=["GET", "POST"])
def tts():
    # Lấy text từ GET hoặc POST JSON/form
    text = ""
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        text = data.get("text", "")
    else:
        text = request.args.get("text", "")

    if not text:
        return jsonify({"error": "Missing text parameter"}), 400

    logger.info(f"Generating speech for: {text[:50]}…")

    # Cấu hình request cho Google TTS
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Chọn voice tiếng Việt (Wavenet)
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Wavenet-A",    # hoặc vi-VN-Neural2-A, vi-VN-Standard-A,...
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Chọn output config: MP3, tốc độ 1.0, cao độ mặc định
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0.0
    )

    # Gửi request
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Đưa dữ liệu âm thanh vào buffer và trả về
    buf = io.BytesIO(response.audio_content)
    buf.seek(0)
    flask_resp = send_file(
        buf,
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="speech.mp3"
    )
    flask_resp.headers["Access-Control-Allow-Origin"] = "*"
    return flask_resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
