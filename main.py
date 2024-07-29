import json
import threading
import socket
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, abort

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message')
def message():
    return render_template('message.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    username = request.form['username']
    message = request.form['message']
    
    data = {
        'username': username,
        'message': message
    }
    
    # Відправка даних на socket сервер
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(json.dumps(data).encode(), ('127.0.0.1', 5000))
    
    return 'Message sent!'

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('127.0.0.1', 6000))
    
    while True:
        message, address = server_socket.recvfrom(1024)
        data = json.loads(message.decode())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # Завантаження існуючих даних
        try:
            with open('storage/data.json', 'r') as f:
                messages = json.load(f)
        except FileNotFoundError:
            messages = {}
        
        # Додавання нового повідомлення
        messages[timestamp] = data
        
        # Збереження даних
        with open('storage/data.json', 'w') as f:
            json.dump(messages, f, indent=4)

if __name__ == '__main__':
    # Запуск HTTP сервера та socket сервера у різних потоках
    threading.Thread(target=socket_server).start()
    app.run(port=3000)
