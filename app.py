import os
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from flask_cors import CORS

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ==========================================
# ACÁ VAS A PONER EL CONTEXTO POLÍTICO
# ==========================================
CONTEXTO_POLITICO = """
Ciudad: Baradero, Buenos Aires.
- Intendente actual: [Nombre del intendente].
- Elecciones próximas: [Año/Mes].
- Candidatos principales: [Candidato A] (Espacio A), [Candidato B] (Espacio B), [Candidato C] (Espacio C).
- Encuestas recientes: [Candidato A] 40%, [Candidato B] 30%, [Candidato C] 15%.
- Temas principales: Inseguridad, empleo local, obras públicas, producción agropecuaria.
- Núcleo estratégico de seguidores: Mujeres de 26-45 años, emprendedores y comerciantes.
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
                # ACÁ LE SUMAMOS EL CONTEXTO POLÍTICO AL PROMPT
                "content": f"Sos un consultor político experto. Usá este contexto para responder:\n{CONTEXTO_POLITICO}\n\nDatos de la base de seguidores:\n{contexto_datos}\n\nPregunta del usuario: {pregunta}\n\nRespondé de forma clara, directa y profesional. Máximo 2 párrafos."
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
    contexto_datos = data.get("contexto", "").strip()
    try:
        r = client.chat.completions.create(
            messages=[{
                "role": "user",
                # ACÁ TAMBIÉN LE SUMAMOS EL CONTEXTO PARA EL INFORME
                "content": f"Sos un consultor político experto. Usá este contexto general:\n{CONTEXTO_POLITICO}\n\nY estos datos de seguidores:\n{contexto_datos}\n\nRedactá un informe ejecutivo táctico para Baradero con: resumen ejecutivo, análisis demográfico, estrategia por segmento y recomendaciones tácticas concretas."
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
