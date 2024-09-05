from flask import Flask, request, jsonify, send_from_directory, session, render_template
from flask_cors import CORS
from g4f.client import Client
import os

app = Flask(__name__)
app.secret_key = 'huankk123@@'  # Thay thế 'your_secret_key' bằng một chuỗi ngẫu nhiên an toàn
CORS(app)
client = Client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')

    if 'conversation' not in session:
        session['conversation'] = []

    # Thêm tin nhắn người dùng vào cuộc trò chuyện
    session['conversation'].append({"role": "user", "content": user_input})

    # Gửi toàn bộ lịch sử cuộc trò chuyện đến GPT-4
    print("Lịch sử cuộc trò chuyện gửi đi:", session['conversation'])  # Log lịch sử cuộc trò chuyện

    response = client.chat.completions.create(
        model="gpt-4",
        messages=session['conversation'],
    )
    
    reply = response.choices[0].message.content
    print("Phản hồi từ GPT-4:", reply)  # Log phản hồi từ GPT-4

    # Thêm phản hồi của chatbot vào lịch sử cuộc trò chuyện
    session['conversation'].append({"role": "assistant", "content": reply})

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run()
