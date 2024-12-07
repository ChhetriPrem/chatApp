# backend/app.py
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print("A user connected")

@socketio.on('disconnect')
def on_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit('message', {"username": "Server", "text": f"{user} has left the chat."}, broadcast=True)

@socketio.on('set_username')
def set_username(username):
    users[request.sid] = username
    emit('message', {"username": "Server", "text": f"{username} has joined the chat."}, broadcast=True)

@socketio.on('message')
def handle_message(msg):
    username = users.get(request.sid, "Unknown")
    if not msg.strip():
        return  # Ignore empty messages
    formatted_message = {"username": username, "text": msg}
    emit('message', formatted_message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
