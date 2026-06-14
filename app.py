from flask import Flask, render_template, jsonify, request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import pytz

app = Flask(__name__, template_folder='.', static_folder='.')

STREAM_LINKS = [
    {"name": "TUDN", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=tudn_mx"},
    {"name": "VTVplus", "quality": "ES • HD", "url": "https://la18hd.com/vivo/canales.php?stream=vtvplus"},
    {"name": "AmericaTV", "quality": "ES • HD", "url": "https://la18hd.com/vivo/canales.php?stream=americatv"},
    {"name": "DSports", "quality": "ES • HD", "url": "https://la18hd.com/vivo/canales.php?stream=dsports"},
    {"name": "TyC Sports", "quality": "ES • HD", "url": "https://la18hd.com/vivo/canales.php?stream=tycsports"},
    {"name": "Telefe", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=telefe"},
    {"name": "Caracol TV", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=caracol"},
    {"name": "Canal 5", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=canal5"},
    {"name": "DSports Plus", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=dsportsplus"},
    {"name": "ESPN 6", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=espn6"},
    {"name": "Fox Deportes", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=foxdeportes"},
    {"name": "Fox Sports 1", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=foxsports1_usa"},
    {"name": "BeIN Sports Español", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=beinsportes"},
    {"name": "Univisión", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=univision"},
    {"name": "ESPN Deportes", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=espndeportes"},
    {"name": "Win Sports", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=winsports"},
    {"name": "Win Sports Plus", "quality": "• HD", "url": "https://la18hd.com/vivo/canales.php?stream=winsportsplus"}
]

MATCHES = [
    {"id": 1, "group": "A", "status": "finished", "home": "México", "away": "Sudáfrica", "city": "CDMX", "score_home": 2, "score_away": 0, "date": "2026-06-11", "time_mex": "13:00", "is_mexico": True, "stadium": "Estadio Azteca", "flag_home": "https://flagcdn.com/w320/mx.png", "flag_away": "https://flagcdn.com/w320/za.png"},
    {"id": 2, "group": "A", "status": "finished", "home": "Corea del Sur", "away": "Rep. Checa", "city": "Guadalajara", "score_home": 2, "score_away": 1, "date": "2026-06-11", "time_mex": "20:00", "is_mexico": False, "stadium": "Estadio Akron", "flag_home": "https://flagcdn.com/w320/kr.png", "flag_away": "https://flagcdn.com/w320/cz.png"},
    {"id": 3, "group": "B", "status": "finished", "home": "Canadá", "away": "Bosnia y Herz.", "city": "Toronto", "score_home": 1, "score_away": 1, "date": "2026-06-12", "time_mex": "13:00", "is_mexico": False, "stadium": "BMO Field", "flag_home": "https://flagcdn.com/w320/ca.png", "flag_away": "https://flagcdn.com/w320/ba.png"},
    {"id": 4, "group": "D", "status": "finished", "home": "Estados Unidos", "away": "Paraguay", "city": "Los Ángeles", "score_home": 4, "score_away": 1, "date": "2026-06-12", "time_mex": "19:00", "is_mexico": False, "stadium": "SoFi Stadium", "flag_home": "https://flagcdn.com/w320/us.png", "flag_away": "https://flagcdn.com/w320/py.png"},
    {"id": 5, "group": "C", "status": "finished", "home": "Qatar", "away": "Suiza", "city": "San Francisco", "score_home": 1, "score_away": 1, "date": "2026-06-13", "time_mex": "13:00", "is_mexico": False, "stadium": "Levi's Stadium", "flag_home": "https://flagcdn.com/w320/qa.png", "flag_away": "https://flagcdn.com/w320/ch.png"},
    {"id": 6, "group": "C", "status": "finished", "home": "Brasil", "away": "Marruecos", "city": "Nueva Jersey", "score_home": 1, "score_away": 1, "date": "2026-06-13", "time_mex": "16:00", "is_mexico": False, "stadium": "MetLife Stadium", "flag_home": "https://flagcdn.com/w320/br.png", "flag_away": "https://flagcdn.com/w320/ma.png"},
    {"id": 7, "group": "C", "status": "finished", "home": "Haití", "away": "Escocia", "city": "Boston", "score_home": 0, "score_away": 1, "date": "2026-06-13", "time_mex": "19:00", "is_mexico": False, "stadium": "Gillette Stadium", "flag_home": "https://flagcdn.com/w320/ht.png", "flag_away": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/320px-Flag_of_Scotland.svg.png"},
    {"id": 8, "group": "D", "status": "live", "home": "Australia", "away": "Turquía", "city": "Vancouver", "score_home": 0, "score_away": 0, "date": "2026-06-13", "time_mex": "22:00", "is_mexico": False, "stadium": "BC Place", "flag_home": "https://flagcdn.com/w320/au.png", "flag_away": "https://flagcdn.com/w320/tr.png"},
    {"id": 9, "group": "E", "status": "upcoming", "home": "Alemania", "away": "Curazao", "city": "Houston", "score_home": None, "score_away": None, "date": "2026-06-14", "time_mex": "11:00", "is_mexico": False, "stadium": "NRG Stadium", "flag_home": "https://flagcdn.com/w320/de.png", "flag_away": "https://flagcdn.com/w320/cw.png"},
    {"id": 10, "group": "F", "status": "upcoming", "home": "Países Bajos", "away": "Japón", "city": "Dallas", "score_home": None, "score_away": None, "date": "2026-06-14", "time_mex": "14:00", "is_mexico": False, "stadium": "AT&T Stadium", "flag_home": "https://flagcdn.com/w320/nl.png", "flag_away": "https://flagcdn.com/w320/jp.png"},
    {"id": 11, "group": "G", "status": "upcoming", "home": "España", "away": "Nigeria", "city": "Nueva Jersey", "score_home": None, "score_away": None, "date": "2026-06-15", "time_mex": "13:00", "is_mexico": False, "stadium": "MetLife Stadium", "flag_home": "https://flagcdn.com/w320/es.png", "flag_away": "https://flagcdn.com/w320/ng.png"},
    {"id": 12, "group": "H", "status": "upcoming", "home": "Francia", "away": "Honduras", "city": "Miami", "score_home": None, "score_away": None, "date": "2026-06-15", "time_mex": "16:00", "is_mexico": False, "stadium": "Hard Rock Stadium", "flag_home": "https://flagcdn.com/w320/fr.png", "flag_away": "https://flagcdn.com/w320/hn.png"},
    {"id": 13, "group": "I", "status": "upcoming", "home": "Argentina", "away": "Argelia", "city": "Santa Clara", "score_home": None, "score_away": None, "date": "2026-06-16", "time_mex": "18:00", "is_mexico": False, "stadium": "Levi's Stadium", "flag_home": "https://flagcdn.com/w320/ar.png", "flag_away": "https://flagcdn.com/w320/dz.png"},
    {"id": 14, "group": "J", "status": "upcoming", "home": "Italia", "away": "Camerún", "city": "Los Ángeles", "score_home": None, "score_away": None, "date": "2026-06-16", "time_mex": "21:00", "is_mexico": False, "stadium": "SoFi Stadium", "flag_home": "https://flagcdn.com/w320/it.png", "flag_away": "https://flagcdn.com/w320/cm.png"},
    {"id": 15, "group": "K", "status": "upcoming", "home": "Portugal", "away": "Uzbekistán", "city": "CDMX", "score_home": None, "score_away": None, "date": "2026-06-17", "time_mex": "13:00", "is_mexico": False, "stadium": "Estadio Azteca", "flag_home": "https://flagcdn.com/w320/pt.png", "flag_away": "https://flagcdn.com/w320/uz.png"},
    {"id": 16, "group": "L", "status": "upcoming", "home": "Colombia", "away": "Croacia", "city": "Monterrey", "score_home": None, "score_away": None, "date": "2026-06-17", "time_mex": "16:00", "is_mexico": False, "stadium": "Estadio BBVA", "flag_home": "https://flagcdn.com/w320/co.png", "flag_away": "https://flagcdn.com/w320/hr.png"}
]

MEXICO_TIME = pytz.timezone('America/Mexico_City')
MATCH_START = MEXICO_TIME.localize(datetime(2026, 6, 13, 22, 0, 0))

MARCADORES_FILE = 'marcadores.json'

def load_marcadores():
    try:
        with open(MARCADORES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_marcadores(data):
    with open(MARCADORES_FILE, 'w') as f:
        json.dump(data, f)

def get_matches_with_live_data():
    """Devuelve MATCHES combinado con el estado guardado en marcadores.json"""
    marcadores = load_marcadores()
    result = []
    for m in MATCHES:
        match = dict(m)
        live = marcadores.get(str(match["id"]))
        if live:
            match["status"] = live.get("status", match["status"])
            match["score_home"] = live.get("score_home", match["score_home"])
            match["score_away"] = live.get("score_away", match["score_away"])
            match["minute"] = live.get("minute", match.get("minute", "0"))
        result.append(match)
    return result

@app.route('/')
def index():
    return render_template('index.html', matches=get_matches_with_live_data())

@app.route('/match/<int:match_id>')
def match_view(match_id):
    # Buscamos el partido (con datos actualizados)
    match = next((m for m in get_matches_with_live_data() if m["id"] == match_id), None)
    
    # Si no existe el partido, devolvemos un error 404
    if match is None:
        return "Partido no encontrado", 404
        
    # Pasamos la lista completa de STREAM_LINKS que definiste arriba
    return render_template('stream.html', match=match, stream_links=STREAM_LINKS)

@app.route('/admin')
def admin_panel():
    return render_template('admin.html', matches=get_matches_with_live_data())

# API: estado de TODOS los partidos (para refrescar la sección "En Vivo" dinámicamente)
@app.route('/api/status')
def api_status_all():
    matches = get_matches_with_live_data()
    return jsonify([
        {
            "id": m["id"],
            "home": m["home"],
            "away": m["away"],
            "minute": m.get("minute", "0"),
            "score_home": m.get("score_home") or 0,
            "score_away": m.get("score_away") or 0,
            "status": m.get("status", "upcoming")
        }
        for m in matches
    ])

# API: estado de UN partido específico
@app.route('/api/status/<int:match_id>')
def api_status(match_id):
    match = next((m for m in get_matches_with_live_data() if m["id"] == match_id), None)
    if match is None:
        return jsonify({"error": "Partido no encontrado"}), 404
    return jsonify({
        "minute": match.get("minute", "0"),
        "score_home": match.get("score_home") or 0,
        "score_away": match.get("score_away") or 0,
        "status": match.get("status", "upcoming")
    })

# Esta ruta es tu CONTROL REMOTO (por partido)
@app.route('/admin/update')
def update_score():
    match_id = request.args.get('id')
    if not match_id:
        return "Falta el parámetro id (id del partido)", 400

    marcadores = load_marcadores()
    marcadores[match_id] = {
        "minute": request.args.get('m'),
        "score_home": int(request.args.get('h')),
        "score_away": int(request.args.get('a')),
        "status": request.args.get('s')
    }
    save_marcadores(marcadores)
    return "Actualizado correctamente"
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)
