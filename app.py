import os
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from flask_cors import CORS

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

CONTEXTO_POLITICO = """
Ciudad: Baradero, Buenos Aires.
- Intendente: Esteban "Tito" Sanzio (Unión por la Patria).
- Oposición: Juan Ramos (Agrupación Baradero 400 Años), ganó las elecciones de 2025.
- Temas: Seguridad, emergencia hídrica, obras.
"""

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api_chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pregunta = data.get("pregunta", "").strip()
    contexto_datos = data.get("contexto", "").strip()
    
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400

    try:
        r = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Contexto político: {CONTEXTO_POLITICO}\nDatos de seguidores: {contexto_datos}\n\nPregunta: {pregunta}\n\nUsá la búsqueda web para encontrar noticias recientes si es necesario. Respondé como consultor político, máximo 2 párrafos."
            }],
            model="openai/gpt-oss-120b",
            temperature=0.5,
            max_tokens=1000,
            # 👇 ESTAS DOS LÍNEAS ACTIVAN LA BÚSQUEDA EN GROQ
            tools=[{"type": "browser_search"}],
            tool_choice="required" 
        )
        return jsonify({"respuesta": r.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api_generar", methods=["POST"])
def api_generar():
    data = request.json or {}
    contexto_datos = data.get("contexto", "").strip()
    try:
        r = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Contexto político: {CONTEXTO_POLITICO}\nDatos de seguidores: {contexto_datos}\n\nRedactá un informe ejecutivo táctico para Baradero. Buscá en internet las últimas noticias sobre la ciudad para enriquecer el análisis."
            }],
            model="openai/gpt-oss-120b",
            temperature=0.3,
            max_tokens=3000,
            # 👇 ACÁ TAMBIÉN LE DECIMOS QUE BUSQUE
            tools=[{"type": "browser_search"}],
            tool_choice="required"
        )
        return jsonify({"report": r.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

