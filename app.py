from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import threading
import os
import json

app = Flask(__name__)

# ============================
# CONFIGURAÇÕES
# ============================
GMAIL_USER = "ognibenejeanfranco@gmail.com"
GMAIL_APP_PASSWORD = "rwbwneipsjctgmul"

LIMITE_ALERTAS = 5
TEMPO_BLOQUEIO_HORAS = 24

db_file = '/tmp/seguranca_db.json'
alertas_db = {}

# ============================
# BANCO LOCAL
# ============================
def carregar_db():
    global alertas_db
    try:
        with open(db_file, 'r') as f:
            alertas_db = json.load(f)
    except:
        alertas_db = {}

def salvar_db():
    try:
        with open(db_file, 'w') as f:
            json.dump(alertas_db, f)
    except:
        pass

carregar_db()

# ============================
# ENVIO DE EMAIL REAL
# ============================
def enviar_email(mac, ip, total):
    try:
        msg = MIMEText(f"""
🚨 ATAQUE RADIUS DETECTADO!

Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
MAC: {mac}
IP: {ip}
Tentativas: {total}

IP BLOQUEADO POR {TEMPO_BLOQUEIO_HORAS} HORAS (bloqueio lógico no servidor).
        """)

        msg['Subject'] = "🚨 ALERTA DE SEGURANÇA - ATAQUE DETECTADO"
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, [GMAIL_USER], msg.as_string())
        server.quit()

        print("📧 Email enviado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")

# ============================
# LIMPEZA AUTOMÁTICA BLOQUEIO
# ============================
def limpar_bloqueios_expirados():
    agora = datetime.now()
    alterado = False

    for mac in list(alertas_db.keys()):
        bloqueado = alertas_db[mac].get("bloqueado", False)
        if bloqueado:
            data_bloqueio = datetime.fromisoformat(alertas_db[mac]["data_bloqueio"])
            if agora - data_bloqueio > timedelta(hours=TEMPO_BLOQUEIO_HORAS):
                print(f"🔓 Desbloqueando automaticamente {mac}")
                del alertas_db[mac]
                alterado = True

    if alterado:
        salvar_db()

# ============================
# ROTA PRINCIPAL
# ============================
@app.route('/log', methods=['POST'])
def log_evento():
    limpar_bloqueios_expirados()

    data = request.json
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    tipo = data.get('tipo', 'desconhecido')
    ip = data.get('ip', 'unknown')
    mac = data.get('mac', f"USER_{ip}")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] MAC:{mac} IP:{ip} TIPO:{tipo}")

    # Se já bloqueado → rejeita imediatamente
    if mac in alertas_db and alertas_db[mac].get("bloqueado", False):
        print(f"🚫 ACESSO BLOQUEADO: {mac}")
        return jsonify({"status": "bloqueado"}), 403

    if mac not in alertas_db:
        alertas_db[mac] = {
            "total": 0,
            "ip": ip
        }

    alertas_db[mac]["total"] += 1
    total = alertas_db[mac]["total"]

    if total >= LIMITE_ALERTAS:
        print(f"🚨 ATAQUE DETECTADO! {mac} - {total} tentativas")

        alertas_db[mac]["bloqueado"] = True
        alertas_db[mac]["data_bloqueio"] = datetime.now().isoformat()

        threading.Thread(target=enviar_email, args=(mac, ip, total)).start()

    else:
        print(f"⚠️ Alerta {total}/{LIMITE_ALERTAS}: {mac}")

    salvar_db()

    return jsonify({
        "status": "ok",
        "alertas": total,
        "bloqueado": alertas_db[mac].get("bloqueado", False)
    })

# ============================
# STATUS
# ============================
@app.route('/status/<mac>', methods=['GET'])
def status(mac):
    limpar_bloqueios_expirados()

    if mac in alertas_db:
        return jsonify(alertas_db[mac])

    return jsonify({"mac": mac, "total": 0, "bloqueado": False})

# ============================
# RESET MANUAL
# ============================
@app.route('/status/<mac>', methods=['DELETE'])
def reset(mac):
    if mac in alertas_db:
        del alertas_db[mac]
        salvar_db()
    return jsonify({"status": "reset", "mac": mac})

# ============================
# LISTAGEM
# ============================
@app.route('/alertas', methods=['GET'])
def listar_alertas():
    return jsonify(alertas_db)

# ============================
# START
# ============================
if __name__ == '__main__':
    print("🚀 Agente IA Segurança iniciado!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
