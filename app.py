import io
import logging
from flask import Flask, request, send_file, jsonify
from TTS.api import TTS
import soundfile as sf

# --- Khởi tạo Flask ---
app = Flask(__name__, template_folder="templates")

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Khởi tạo Coqui TTS model ---
# model_name "tts_models/vi/viet_vits" chạy offline, chất lượng cao
tts = TTS(
    model_name="tts_models/vi/viet_vits",
    progress_bar=False,
    gpu=False
)

@app.route("/api/tts", methods=["GET", "POST"])
def api_tts():
    # Lấy text từ GET hoặc POST
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        text = data.get("text", "")
    else:
        text = request.args.get("text", "")

    if not text:
        return jsonify({"error": "Missing text parameter"}), 400

    logger.info(f"Synthesizing speech for: {text[:50]}…")

    # Sinh audio (numpy array) và sample_rate
    wav, sr = tts.tts(text)

    # Ghi ra buffer WAV
    buf = io.BytesIO()
    sf.write(buf, wav, sr, format="WAV")
    buf.seek(0)

    # Trả về file WAV
    resp = send_file(
        buf,
        mimetype="audio/wav",
        as_attachment=False,
        download_name="speech.wav"
    )
    # Cho phép CORS nếu cần
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

if __name__ == "__main__":
    # Chạy local
    app.run(host="0.0.0.0", port=5000, debug=True)
