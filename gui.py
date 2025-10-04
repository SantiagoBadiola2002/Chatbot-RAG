from flask import Flask, request, jsonify, render_template
import uuid
from services.chatbot import hybrid_chatbot


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("chat.html")  # el HTML que haremos


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_input = data.get("message", "")
    session_id = data.get("session_id")  # puede ser None

    # Si el cliente no envía session_id, generamos uno y lo devolvemos
    generated = False
    if not session_id:
        session_id = str(uuid.uuid4())
        generated = True

    respuesta = hybrid_chatbot(user_input, session_id=session_id)
    resp = {"reply": str(respuesta)}
    if generated:
        resp["session_id"] = session_id
    return jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True)
