import os
from flask import Flask, render_template_string

app = Flask(__name__)

# --- PARRILLA DE CANALES (CANAL 5 INCLUIDO) ---
CANALES_TV = [
    {
        "id": "canal5",
        "nombre": "Canal 5 HD",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Canal_5_Logo_2024.svg/120px-Canal_5_Logo_2024.svg.png",
        # Usamos un player de alta compatibilidad que emula un navegador real
        "embed_url": "https://www.youtube.com/embed/live_stream?channel=UC7Z_40ICt_7Zghv7idupXfA"
    },
    {
        "id": "milenio",
        "nombre": "Milenio TV",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Milenio_Televisi%C3%B3n_logo.svg/120px-Milenio_Televisi%C3%B3n_logo.svg.png",
        "embed_url": "https://www.youtube.com/embed/live_stream?channel=UC7Z_40ICt_7Zghv7idupXfA"
    }
]

HTML_TELEVISION = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mi Tele Cloud</title>
    <style>
        body { background: #0d0e12; color: #fff; font-family: sans-serif; text-align: center; padding: 20px; }
        .pantalla { max-width: 800px; margin: 0 auto; background: #000; padding: 10px; border-radius: 10px; }
        iframe { width: 100%; aspect-ratio: 16/9; border: none; }
        .btn { padding: 10px 20px; margin: 5px; cursor: pointer; background: #242734; border: 1px solid #444; color: white; border-radius: 5px; }
        .btn:hover { background: #00ffcc; color: #000; }
    </style>
</head>
<body>
    <h1>📺 Mi Tele en la Nube</h1>
    <div class="pantalla"><iframe id="tv-frame" src="" allowfullscreen allow="autoplay"></iframe></div>
    <div style="margin-top:20px;">
        {% for canal in lista_canales %}
            <button class="btn" onclick="document.getElementById('tv-frame').src='{{ canal.embed_url }}'">
                {{ canal.nombre }}
            </button>
        {% endfor %}
    </div>
    <script>
        window.onload = function() { document.querySelector('.btn').click(); }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TELEVISION, lista_canales=CANALES_TV)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
