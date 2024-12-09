from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import logging

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Flask-SocketIO setup with CORS and logging
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=25, ping_interval=10, logger=True, engineio_logger=True)

# User data
users = {}

# Logging setup
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')  # Assuming you have your HTML in the 'templates' folder

@socketio.on('connect')
def on_connect():
    logging.debug("A user connected")

@socketio.on('disconnect')
def on_disconnect():
    user = users.pop(request.sid, None)
    if user:
        logging.debug(f"{user} disconnected")
        emit('message', {"username": "Server", "text": f"{user} has left the chat."}, broadcast=True)

@socketio.on('set_username')
def set_username(username):
    users[request.sid] = username
    logging.debug(f"{username} set as username")
    emit('message', {"username": "Server", "text": f"{username} has joined the chat."}, broadcast=True)

@socketio.on('message')
def handle_message(msg):
    username = users.get(request.sid, "Unknown")
    logging.debug(f"Received message from {username}: {msg}")  # Debugging message
    if not msg.strip():
        return  # Ignore empty messages
    
    if msg.get('type') == 'image':
        # If the message is an image (base64 string), broadcast the image to everyone
        logging.debug(f"Broadcasting image from {username}")
        emit('message', {'username': username, 'src': msg['src'], 'type': 'image'}, broadcast=True)
    else:
        # Otherwise, it's a regular text message
        logging.debug(f"Broadcasting text message from {username}: {msg['text']}")
        formatted_message = {"username": username, "text": msg['text'], "type": 'text'}
        emit('message', formatted_message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
