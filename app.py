from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# ============================
# CONFIGURAÇÃO WEBHOOK META
# ============================
WEBHOOK_VERIFY_TOKEN = "MEU_TOKEN_SUPER_SECRETO"  # coloque o token que você configurou na Meta

# ============================
# ENDPOINT PARA VERIFICAÇÃO E EVENTOS
# ============================
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verificação do webhook pelo Facebook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            print("✅ Webhook verificado com sucesso!")
            return challenge, 200
        else:
            print("❌ Falha na verificação do webhook")
            return "Erro de verificação", 403

    elif request.method == 'POST':
        # Recebendo notificações de eventos do Facebook
        data = request.json
        print(f"📩 Evento recebido do Facebook ({datetime.now()}):")
        print(data)

        # Aqui você pode enviar os dados para o agente IA processar
        # Exemplo: processar_mensagem_facebook(data)

        return "EVENTO RECEBIDO", 200

# ============================
# ENDPOINT DE STATUS
# ============================
@app.route("/")
def home():
    return "Agente IA Facebook/Instagram ativo"

# ============================
# EXECUÇÃO DO SERVIDOR
# ============================
if __name__ == "__main__":
    print("🚀 Agente IA Webhook iniciado!")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
