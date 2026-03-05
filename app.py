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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
