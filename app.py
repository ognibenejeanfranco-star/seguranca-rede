from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# SUA SENHA APP (16 dígitos SEM espaços)
GMAIL_PASSWORD = 'baxbvdjpmvzsvmds'

# Contadores (memória)
alertas_hoje = {}
bloqueados_mac = {}
alerta_enviado = {}  # Evita spam

@app.route('/log', methods=['POST'])
def log():
    dados = request.json
    timestamp = datetime.now()
    mac = dados.get('mac', dados.get('ip', 'unknown'))
    ip = dados.get('ip', 'unknown')
    tipo = dados.get('tipo', 'unknown')
    
    print(f"[{timestamp.strftime('%H:%M:%S')}] MAC:{mac} IP:{ip} TIPO:{tipo}")
    
    # SALVAR LOG (simples arquivo memória)
    chave = f"{mac}_{ip}"
    
    if tipo == 'radius_falha':
        if chave not in alertas_hoje:
            alertas_hoje[chave] = []
        alertas_hoje[chave].append(timestamp)
        
        # ALERTA IMEDIATO: 5+ falhas em 10min
        recentes = [t for t in alertas_hoje[chave] if timestamp - t < timedelta(minutes=10)]
        if len(recentes) >= 5 and chave not in alerta_enviado:
            enviar_alerta_imediato(f"🚨 BRUTEFORCE DETECTADO!\nMAC: `{mac}`\nIP: `{ip}`\nTentativas: {len(recentes)} em 10min")
            alerta_enviado[chave] = True
            bloqueados_mac[mac] = True
    
    # ALERTA MALWARE DNS
    elif tipo == 'dns_bloqueado' and ('malware' in dados.get('detalhes', '').lower() or 'phishing' in dados.get('detalhes', '').lower()):
        enviar_alerta_imediato(f"⚠️ MALWARE BLOQUEADO!\nMAC: `{mac}`\nIP: `{ip}`\nDomínio: {dados.get('detalhes', 'bloqueado')}")
    
    return jsonify({
        "status": "ok", 
        "bloqueado": mac in bloqueados_mac,
        "alertas": len(alertas_hoje.get(chave, []))
    })

@app.route('/status/<mac>')
def status(mac):
    return jsonify({
        "mac": mac,
        "bloqueado": mac in bloqueados_mac,
        "total_alertas": sum(len(v) for v in alertas_hoje.values())
    })

@app.route('/relatorio')
def relatorio():
    total_incidentes = sum(len(inc) for inc in alertas_hoje.values())
    if total_incidentes > 0:
        enviar_relatorio_diario()
        # Reset diário
        alertas_hoje.clear()
        alerta_enviado.clear()
    return jsonify({"status": "ok", "incidentes_hoje": total_incidentes})

def enviar_alerta_imediato(mensagem):
    try:
        msg = MIMEText(f"""
🚨 ALERTA IMEDIATO - {datetime.now().strftime('%d/%m %H:%M:%S')}

{mensagem}

🔍 Status completo: https://seguranca-rede.onrender.com/status/{mensagem.split('`')[1]}
📊 Relatório diário: https://seguranca-rede.onrender.com/relatorio
        """)
        msg['Subject'] = f'🚨 INVASÃO DETECTADA - {datetime.now().strftime("%d/%m %H:%M")}'
        msg['From'] = 'ognibenejeanfranco@gmail.com'
        msg['To'] = 'ognibenejeanfranco@gmail.com'
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('ognibenejeanfranco@gmail.com', GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ ALERTA ENVIADO: {mensagem[:50]}...")
    except Exception as e:
        print(f"❌ ERRO EMAIL: {e}")

def enviar_relatorio_diario():
    total = sum(len(inc) for inc in alertas_hoje.values())
    macs_suspeitos = list(bloqueados_mac.keys())
    
    msg = MIMEText(f"""
📊 RELATÓRIO DIÁRIO DE SEGURANÇA
{datetime.now().strftime('%d/%m/%Y - %A')}

🔢 TOTAL INCIDENTES: {total}
🚫 DISPOSITIVOS BLOQUEADOS: {len(macs_suspeitos)}
📱 SUSPEITOS: {', '.join(macs_suspeitos[:5])}

✅ Sistema funcionando normalmente.
🔗 Dashboard: https://seguranca-rede.onrender.com/status/ALL
    """)
    msg['Subject'] = f'📊 RELATÓRIO DIÁRIO - {datetime.now().strftime("%d/%m/%Y")}'
    msg['From'] = 'ognibenejeanfranco@gmail.com'
    msg['To'] = 'ognibenejeanfranco@gmail.com'
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('ognibenejeanfranco@gmail.com', GMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    
    print("✅ RELATÓRIO DIÁRIO ENVIADO!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Agente de segurança iniciado!")
    app.run(host='0.0.0.0', port=port, debug=False)
