from flask import Flask, request
import os

app = Flask(__name__)

VERIFY_TOKEN = "meu_token_super_secreto"

# ==============================
# VERIFICAÇÃO DO WEBHOOK META
# ==============================

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado!")
        return challenge, 200
    else:
        return "Erro de verificação", 403


# ==============================
# RECEBER EVENTOS (MENSAGENS)
# ==============================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    print("Evento recebido:")
    print(data)

    return "ok", 200


# ==============================
# STATUS
# ==============================

@app.route("/")
def home():
    return "Agente IA Facebook ativo"

# ============================
# ENDPOINT PARA WEBHOOK META
# ============================
WEBHOOK_VERIFY_TOKEN = "MEU_TOKEN"  # coloque aqui o token que você configurou na Meta

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
        print("📩 Evento recebido do Facebook:", data)
        # Aqui você pode processar o evento ou passar para o agente IA
        return "EVENTO RECEBIDO", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
