from flask import Flask, request, send_file, jsonify, render_template
import io, logging
import soundfile as sf
from TTS.api import TTS

app = Flask(__name__, template_folder="templates")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo Coqui TTS – model tiếng Việt VITS, GPU=False nếu bạn không có CUDA
tts = TTS(
    model_name="tts_models/vi/viet_vits",  # model VITS tiếng Việt
    progress_bar=False,
    gpu=False
)

@app.route("/")
def index():
    return render_template("TTS.html")

@app.route("/api/tts", methods=["GET", "POST"])
def api_tts():
    # Lấy text
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        text = data.get("text", "")
    else:
        text = request.args.get("text", "")

    if not text:
        return jsonify({"error": "Missing text parameter"}), 400

    logger.info(f"Synthesizing: {text[:50]}…")

    # Sinh audio (numpy array) và sample_rate
    wav, sr = tts.tts(text)

    # Ghi vào BytesIO dưới định dạng WAV
    buf = io.BytesIO()
    sf.write(buf, wav, sr, format="WAV")
    buf.seek(0)

    # Trả về cho client
    resp = send_file(
        buf,
        mimetype="audio/wav",
        as_attachment=False,
        download_name="speech.wav"
    )
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
