from flask import Flask, render_template, send_from_directory
import os
import socket
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lobby')
def lobby():
    return render_template('lobby.html')

if __name__ == '__main__':
    # Ensure static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')
        
    # Auto-move bg_gif.gif to static folder if it's currently in the root
    if os.path.exists('bg_gif.gif') and not os.path.exists(os.path.join('static', 'bg_gif.gif')):
        try:
            shutil.move('bg_gif.gif', os.path.join('static', 'bg_gif.gif'))
            print("Successfully moved 'bg_gif.gif' to the 'static' folder.")
        except Exception as e:
            print(f"Failed to move 'bg_gif.gif': {e}")
    # Find local IP to display
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("="*50)
    print("Starting Focus Fighter Web App...")
    print(f"Open this link in your browser: http://127.0.0.1:5000")
    print(f"Or on your local network: http://{local_ip}:5000")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
