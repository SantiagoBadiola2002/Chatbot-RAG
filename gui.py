from flask import Flask, request, jsonify, render_template
from app import hybrid_chatbot  # tu función

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")  # el HTML que haremos

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    respuesta = hybrid_chatbot(user_input)
    return jsonify({"reply": str(respuesta)})

if __name__ == "__main__":
    app.run(debug=True)
