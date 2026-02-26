from flask import Flask, request, jsonify
from datetime import datetime
app = Flask(__name__)

@app.route('/log', methods=['POST'])
def log():
    print("Log recebido:", request.json)
    return jsonify({"status": "ok"})

@app.route('/status/<ip>')
def status(ip):
    return jsonify({"ip": ip, "bloqueado": False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
