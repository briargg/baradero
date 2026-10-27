import os

from flask import Flask, request, jsonify, send_from_directory
from groq import Groq

# La API Key se lee desde una variable de entorno en Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = Flask(__name__, static_folder=".", static_url_path="")

# ==========================================
# DATOS DE BARADERO
# ==========================================
# PEGÁ ACÁ EL ARRAY DATA COMPLETO QUE ESTÁ EN TU HTML ORIGINAL
DATA = [
    # ["mauri.cio1088","MAURICIO RIOS","GODOY CRUZ 2105 S/N","ESTUDIANTE","M","36-45",0,-33.695876,-59.50818],
    # ... y los 721 registros restantes
]

df = pd.DataFrame(DATA, columns=["handle","nombre","domicilio","profesion","genero","edad","es_negocio","lat","lng"])

personas = df[df["es_negocio"] == 0]
metricas = {
    "total": len(df),
    "personas": int(len(personas)),
    "negocios": int((df["es_negocio"] == 1).sum()),
    "mujeres": int((personas["genero"] == "F").sum()),
    "hombres": int((personas["genero"] == "M").sum()),
    "geolocalizados": int((df["lat"] != 0).sum()),
    "edad_top": personas["edad"].value_counts().head(5).to_dict(),
    "profesiones_top": personas["profesion"].replace("", pd.NA).dropna().value_counts().head(8).to_dict(),
    "apellidos_top": personas["nombre"].apply(lambda n: n.split()[-1] if isinstance(n, str) else "").value_counts().head(8).to_dict(),
}

CONTEXTO = f"""
Baradero, Buenos Aires. Base: {metricas['total']} seguidores.
Personas: {metricas['personas']} / Negocios: {metricas['negocios']}.
Mujeres: {metricas['mujeres']}, Hombres: {metricas['hombres']}.
Geolocalizados: {metricas['geolocalizados']}.
Edades top: {metricas['edad_top']}.
Profesiones top: {metricas['profesiones_top']}.
Apellidos frecuentes: {metricas['apellidos_top']}.
Núcleo estratégico: mujeres 26-45 años, emprendedoras y comerciantes locales.
"""

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api_chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pregunta = data.get("pregunta", "").strip()
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    try:
        r = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Contexto: {CONTEXTO}\n\nPregunta: {pregunta}\n\nRespondé como consultor político, máximo 2 párrafos."}],
            model="openai/gpt-oss-120b",
            temperature=0.5,
            max_tokens=1000,
        )
        return jsonify({"respuesta": r.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api_generar", methods=["POST"])
def api_generar():
    try:
        r = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Contexto: {CONTEXTO}\n\nRedactá un informe ejecutivo táctico para Baradero con: resumen, análisis demográfico, estrategia por segmento y recomendaciones."}],
            model="openai/gpt-oss-120b",
            temperature=0.3,
            max_tokens=3000,
        )
        return jsonify({"metrics": metricas, "report": r.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
