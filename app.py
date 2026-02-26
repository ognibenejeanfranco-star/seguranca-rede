from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os

app = Flask(__name__)
GMAIL_PASSWORD = 'baxbvdjpmvzsvmds'

# Armazenamento simples
alertas_hoje = {}
bloqueados_mac = {}

@app.route('/log', methods=['POST'])
def log():
    dados = request.json
    timestamp = datetime.now()
    mac = dados.get('mac', 'unknown')
    ip = dados.get('ip', 'unknown')
    tipo = dados.get('tipo', 'unknown')
    detalhes = dados.get('detalhes', '')
    
    print(f"[{timestamp.strftime('%H:%M:%S')}] MAC:{mac} IP:{ip} TIPO:{tipo}")
    
    chave = f"{mac}_{ip}"
    
    # RADIUS BRUTEFORCE (5+ falhas)
    if tipo == 'radius_falha':
        if chave not in alertas_hoje:
            alertas_hoje[chave] = 0
        alertas_hoje[chave] += 1
        
        if alertas_hoje[chave] >= 5:
            enviar_alerta(f"🚨 BRUTEFORCE!\nMAC: {mac}\nIP: {ip}\nTentativas: {alertas_hoje[chave]}")
            bloqueados_mac[mac] = True
    
    # MALWARE DNS (IMEDIATO)
    elif tipo == 'dns_bloqueado' and ('malware' in detalhes.lower() or 'virus' in detalhes.lower()):
        print("🚨 MALWARE DETECTADO - enviando alerta!")
        enviar_alerta(f"⚠️ MALWARE BLOQUEADO!\nMAC: {mac}\nIP: {ip}\nDomínio: {detalhes}")
    
    return jsonify({
        "status": "ok", 
        "bloqueado": mac in bloqueados_mac,
        "alertas": alertas_hoje.get(chave, 0)
    })

@app.route('/status/<mac>')
def status(mac):
    return jsonify({
        "mac": mac,
        "bloqueado": mac in bloqueados_mac,
        "total_alertas": sum(alertas_hoje.values())
    })

@app.route('/relatorio')
def relatorio():
    total = sum(alertas_hoje.values())
    if total > 0:
        enviar_alerta(f"📊 RELATÓRIO DIÁRIO\nTotal incidentes: {total}\nMACs bloqueados: {len(bloqueados_mac)}")
        alertas_hoje.clear()
    return jsonify({"status": "ok", "incidentes": total})

def enviar_alerta(mensagem):
    try:
        msg = MIMEText(f"{mensagem}\n\nEnviado: {datetime.now().strftime('%d/%m %H:%M:%S')}")
        msg['Subject'] = '🚨 ALERTA SEGURANÇA'
        msg['From'] = 'ognibenejeanfranco@gmail.com'
        msg['To'] = 'ognibenejeanfranco@gmail.com'
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('ognibenejeanfranco@gmail.com', GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ EMAIL ENVIADO: {mensagem[:50]}")
    except Exception as e:
        print(f"❌ ERRO EMAIL: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
