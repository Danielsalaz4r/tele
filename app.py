import os
from flask import Flask, render_template_string

app = Flask(__name__)

# --- PARRILLA COMPLETA DE CANALES MÉXICO ---
CANALES = [
    {"nombre": "Las Estrellas", "url": "https://stream7.mexicotieneorgano.com.mx/lasestrellas/index.m3u8"},
    {"nombre": "Azteca 7", "url": "https://stream7.mexicotieneorgano.com.mx/azteca7/index.m3u8"},
    {"nombre": "Canal 45 (Congreso)", "url": "https://stream7.mexicotieneorgano.com.mx/congreso/index.m3u8"},
    {"nombre": "Milenio TV", "url": "https://www.milenio.com/hls/live.m3u8"},
    {"nombre": "ADN 40", "url": "https://stream7.mexicotieneorgano.com.mx/adn40/index.m3u8"}
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        body { background: #0d0d0d; color: white; font-family: sans-serif; margin: 0; padding: 15px; text-align: center; }
        .tv-box { width: 100%; max-width: 800px; margin: 0 auto; background: #000; border: 3px solid #444; border-radius: 8px; overflow: hidden; }
        video { width: 100%; display: block; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-top: 20px; max-width: 800px; margin-left: auto; margin-right: auto; }
        button { padding: 12px; background: #222; border: 1px solid #444; color: white; border-radius: 5px; cursor: pointer; font-weight: bold; }
        button:hover { background: #0088cc; }
    </style>
</head>
<body>
    <h1>📺 Mi Tele Digital</h1>
    <div class="tv-box"><video id="video" controls autoplay muted></video></div>
    <div class="grid">
        {% for c in canales %}
            <button onclick="playCanal('{{ c.url }}')">{{ c.nombre }}</button>
        {% endfor %}
    </div>
    <script>
        var video = document.getElementById('video');
        function playCanal(url) {
            if (Hls.isSupported()) {
                var hls = new Hls();
                hls.loadSource(url);
                hls.attachMedia(video);
                video.play();
            } else { video.src = url; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, canales=CANALES)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
