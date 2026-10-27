import os
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = Flask(__name__, static_folder=".", static_url_path="")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api_chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pregunta = data.get("pregunta", "").strip()
    contexto = data.get("contexto", "").strip()
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    try:
        r = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Contexto de la base de seguidores de Baradero:\n{contexto}\n\nPregunta: {pregunta}\n\nRespondé como consultor político, máximo 2 párrafos."
            }],
            model="openai/gpt-oss-120b",
            temperature=0.5,
            max_tokens=1000,
        )
        return jsonify({"respuesta": r.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api_generar", methods=["POST"])
def api_generar():
    data = request.json or {}
    contexto = data.get("contexto", "").strip()
    try:
        r = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Contexto de la base de seguidores de Baradero:\n{contexto}\n\nRedactá un informe ejecutivo táctico para Baradero con: resumen ejecutivo, análisis demográfico, estrategia por segmento y recomendaciones tácticas concretas."
            }],
            model="openai/gpt-oss-120b",
            temperature=0.3,
            max_tokens=3000,
        )
        return jsonify({"report": r.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
