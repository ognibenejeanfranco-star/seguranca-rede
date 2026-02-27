from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import threading
import time
import os
import json

app = Flask(__name__)

# ============================
# CONFIGURAÇÕES FIXAS
# ============================
GMAIL_USER = "ognibenejeanfranco@gmail.com"
GMAIL_APP_PASSWORD = "rwbwneipsjctgmul"  # ← TROCAR PELA NOVA!
LIMITE_ALERTAS = 5
RESET_HORAS = 24

# Armazenamento em memória (persiste em arquivo)
alertas_db = {}
db_file = '/tmp/seguranca_db.json'

def carregar_db():
    global alertas_db
    try:
        with open(db_file, 'r') as f:
            alertas_db = json.load(f)
    except:
        alertas_db = {}

def salvar_db():
    with open(db_file, 'w') as f:
        json.dump(alertas_db, f)

carregar_db()

def enviar_email(mac, ip, total):
    try:
        # SALVA alerta em arquivo (você vê no servidor)
        with open('/tmp/alertas_seguranca.txt', 'a') as f:
            f.write(f"🚨 ATAQUE {datetime.now()}: {mac} {ip} {total}x\n")
        print(f"🚨 ATAQUE LOCAL: {mac} {ip} {total}x")
    except Exception as e:
        print(f"❌ Erro local: {e}")
🚨 ALERTA DE SEGURANÇA - ATAQUE DETECTADO

MAC/IP: {mac}
IP: {ip}
Total tentativas: {total}
Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

BLOQUEIO AUTOMÁTICO ATIVADO!
        """)
        msg['Subject'] = f'🚨 ATAQUE RADIUS: {mac} ({total}x)'
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email enviado para {mac}")
    except Exception as e:
        print(f"❌ Erro email: {e}")

def reset_alerta(mac):
    if mac in alertas_db:
        del alertas_db[mac]

@app.route('/log', methods=['POST'])
def log_evento():
    data = request.json
    if not data:
        return jsonify({"error": "JSON inválido"}), 400
    
    tipo = data.get('tipo', 'desconhecido')
    ip = data.get('ip', 'unknown')
    mac = data.get('mac', f"USER_{ip}")
    detalhes = data.get('detalhes', '')
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] MAC:{mac} IP:{ip} TIPO:{tipo}")
    
    if mac not in alertas_db:
        alertas_db[mac] = {
            'ultimo_alerta': datetime.now().isoformat(),
            'total': 0,
            'ip': ip
        }
    
    # Incrementa contador
    alertas_db[mac]['total'] += 1
    alertas_db[mac]['ultimo_alerta'] = datetime.now().isoformat()
    alertas_db[mac]['ip'] = ip
    
    total = alertas_db[mac]['total']
    
    # Verifica limite e dispara email
    if total >= LIMITE_ALERTAS:
        print(f"🚨 ATAQUE! {mac}: {total} tentativas")
        threading.Thread(target=enviar_email, args=(mac, ip, total)).start()
        alertas_db[mac]['bloqueado'] = True
    else:
        print(f"⚠️ Alerta {total}/{LIMITE_ALERTAS}: {mac}")
    
    salvar_db()
    
    return jsonify({
        "status": "ok",
        "alertas": total,
        "bloqueado": alertas_db[mac].get('bloqueado', False),
        "mac": mac
    })

@app.route('/status/<mac>', methods=['GET'])
def status(mac):
    if mac in alertas_db:
        return jsonify({
            "mac": mac,
            "total_alertas": alertas_db[mac]['total'],
            "bloqueado": alertas_db[mac].get('bloqueado', False),
            "ip": alertas_db[mac].get('ip', 'unknown'),
            "ultimo_alerta": alertas_db[mac].get('ultimo_alerta', '')
        })
    return jsonify({
        "mac": mac,
        "total_alertas": 0,
        "bloqueado": False
    })

@app.route('/status/<mac>', methods=['DELETE'])
def reset(mac):
    if mac in alertas_db:
        del alertas_db[mac]
        salvar_db()
    return jsonify({"status": "reset", "mac": mac})

if __name__ == '__main__':
    print("🚀 Agente IA Segurança iniciado!")
    carregar_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
