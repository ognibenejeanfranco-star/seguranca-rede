from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def receber_log():
    dados = request.json
    print(f"Log recebido: {dados}")  # Debug
    
    # REGRA SIMPLES: 5 falhas RADIUS = alerta
    if dados.get('tipo') == 'radius_falha':
        print("🚨 RADIUS suspeito detectado!")
        enviar_alerta(f"🚨 {dados['ip']} - {dados['detalhes'][:100]}")
    
    return jsonify({"status": "ok"}), 200

@app.route('/status/<ip>')
def status_ip(ip):
    return jsonify({"ip": ip, "bloqueado": False})

def enviar_alerta(mensagem):
    print(f"📧 Enviando alerta: {mensagem}")  # Debug email
    # TODO: Configurar email depois

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
