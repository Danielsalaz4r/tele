import os
from flask import Flask, render_template_string

app = Flask(__name__)

# Parrilla de canales que implementamos previamente con embeds estables
CANALES_TV = [
    {
        "id": "milenio",
        "nombre": "Milenio TV",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Milenio_Televisi%C3%B3n_logo.svg/120px-Milenio_Televisi%C3%B3n_logo.svg.png",
        "embed_url": "https://www.youtube.com/embed/live_stream?channel=UC7Z_40ICt_7Zghv7idupXfA"
    },
    {
        "id": "canal40",
        "nombre": "ADN 40",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Adn40_logo.svg/120px-Adn40_logo.svg.png",
        "embed_url": "https://www.youtube.com/embed/live_stream?channel=UC_Enr77itI_f-XgOiaMv3gQ"
    }
]

HTML_TELEVISION = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Tele en la Nube</title>
    <style>
        body { background-color: #0d0e12; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .tv-container { width: 100%; max-width: 1000px; background: #1a1c23; border-radius: 16px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.7); border: 1px solid #2d313f; }
        .header-tv h1 { margin: 0 0 15px 0; font-size: 24px; color: #00ffcc; border-bottom: 2px solid #2d313f; padding-bottom: 10px; }
        .pantalla-box { width: 100%; background: #000; border-radius: 10px; overflow: hidden; position: relative; padding-bottom: 56.25%; height: 0; }
        .pantalla-box iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
        .control-remoto { margin-top: 20px; }
        .grid-canales { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
        .boton-canal { background: #242734; border: 1px solid #3f445b; border-radius: 8px; padding: 12px; color: #fff; font-weight: bold; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 8px; }
        .boton-canal img { height: 35px; object-fit: contain; }
        .boton-canal.activo { background: linear-gradient(135deg, #00ffcc 0%, #0099ff 100%); color: #000; }
    </style>
</head>
<body>
    <div class="tv-container">
        <div class="header-tv"><h1>📺 Mi Smart TV Cloud</h1></div>
        <div class="pantalla-box"><iframe id="tv-frame" src="" allowfullscreen allow="autoplay; encrypted-media"></iframe></div>
        <div class="control-remoto">
            <div class="grid-canales">
                {% for canal in lista_canales %}
                    <button class="boton-canal" id="btn-{{ canal.id }}" onclick="cambiarCanal('{{ canal.embed_url }}', '{{ canal.id }}')">
                        <img src="{{ canal.logo }}" alt="{{ canal.nombre }}">
                        <span>{{ canal.nombre }}</span>
                    </button>
                {% endfor %}
            </div>
        </div>
    </div>
    <script>
        var iframe = document.getElementById('tv-frame');
        function cambiarCanal(embedUrl, idBoton) {
            iframe.src = embedUrl;
            document.querySelectorAll('.boton-canal').forEach(btn => btn.classList.remove('activo'));
            document.getElementById('btn-' + idBoton).classList.add('activo');
        }
        window.onload = function() { if(document.querySelector('.boton-canal')) { document.querySelector('.boton-canal').click(); } }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TELEVISION, lista_canales=CANALES_TV)

if __name__ == '__main__':
    # Render nos asigna un puerto dinámico en la variable de entorno 'PORT'
    puerto = int(os.environ.get("PORT", 5000))
    # En producción desactivamos debug=True y escuchamos en 0.0.0.0
    app.run(host="0.0.0.0", port=puerto)