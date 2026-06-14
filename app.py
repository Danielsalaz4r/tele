from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import json
import requests
import threading
import time
import pytz

app = Flask(__name__, template_folder='.', static_folder='.')

# ============================================================
# CONFIGURACIÓN API-FOOTBALL
# ============================================================
API_FOOTBALL_KEY = "df472c1ab0631f565af4b1bb56f31be4"

HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY
}

# ============================================================
# STREAMS
# ============================================================
STREAM_LINKS = [
    {"name": "Canal 5", "quality": "• HD", "url": "https://streamtpday1.xyz/global1.php?stream=canal5mx"},
    {"name": "TUDN MX", "quality": "• HD", "url": "https://streamtpday1.xyz/global1.php?stream=tudnmx"},
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

# ============================================================
# TU MATCHES COMPLETO (copia y pega tu MATCHES aquí)
# ============================================================
MATCHES = [
    # Grupo A
    {"id": 1, "group": "A", "status": "finished", "home": "México", "away": "Sudáfrica", "city": "CDMX", "score_home": 2, "score_away": 0, "date": "2026-06-11", "time_mex": "13:00", "is_mexico": True, "stadium": "Estadio Azteca", "flag_home": "https://flagcdn.com/w320/mx.png", "flag_away": "https://flagcdn.com/w320/za.png"},
    {"id": 2, "group": "A", "status": "finished", "home": "Corea del Sur", "away": "República Checa", "city": "Guadalajara", "score_home": 2, "score_away": 1, "date": "2026-06-11", "time_mex": "20:00", "is_mexico": False, "stadium": "Estadio Akron", "flag_home": "https://flagcdn.com/w320/kr.png", "flag_away": "https://flagcdn.com/w320/cz.png"},
    {"id": 3, "group": "A", "status": "upcoming", "home": "República Checa", "away": "Sudáfrica", "city": "Atlanta", "score_home": None, "score_away": None, "date": "2026-06-18", "time_mex": "10:00", "is_mexico": False, "stadium": "Mercedes-Benz Stadium", "flag_home": "https://flagcdn.com/w320/cz.png", "flag_away": "https://flagcdn.com/w320/za.png"},
    {"id": 4, "group": "A", "status": "upcoming", "home": "México", "away": "Corea del Sur", "city": "Guadalajara", "score_home": None, "score_away": None, "date": "2026-06-18", "time_mex": "19:00", "is_mexico": True, "stadium": "Estadio Akron", "flag_home": "https://flagcdn.com/w320/mx.png", "flag_away": "https://flagcdn.com/w320/kr.png"},
    {"id": 5, "group": "A", "status": "upcoming", "home": "República Checa", "away": "México", "city": "CDMX", "score_home": None, "score_away": None, "date": "2026-06-24", "time_mex": "19:00", "is_mexico": True, "stadium": "Estadio Azteca", "flag_home": "https://flagcdn.com/w320/cz.png", "flag_away": "https://flagcdn.com/w320/mx.png"},
    {"id": 6, "group": "A", "status": "upcoming", "home": "Sudáfrica", "away": "Corea del Sur", "city": "Monterrey", "score_home": None, "score_away": None, "date": "2026-06-24", "time_mex": "19:00", "is_mexico": False, "stadium": "Estadio BBVA", "flag_home": "https://flagcdn.com/w320/za.png", "flag_away": "https://flagcdn.com/w320/kr.png"},

    # Grupo B
    {"id": 7, "group": "B", "status": "finished", "home": "Canadá", "away": "Bosnia y Herzegovina", "city": "Toronto", "score_home": 1, "score_away": 1, "date": "2026-06-12", "time_mex": "13:00", "is_mexico": False, "stadium": "BMO Field", "flag_home": "https://flagcdn.com/w320/ca.png", "flag_away": "https://flagcdn.com/w320/ba.png"},
    {"id": 8, "group": "B", "status": "finished", "home": "Catar", "away": "Suiza", "city": "San Francisco", "score_home": 1, "score_away": 1, "date": "2026-06-13", "time_mex": "13:00", "is_mexico": False, "stadium": "Levi's Stadium", "flag_home": "https://flagcdn.com/w320/qa.png", "flag_away": "https://flagcdn.com/w320/ch.png"},
    {"id": 9, "group": "B", "status": "upcoming", "home": "Suiza", "away": "Bosnia y Herzegovina", "city": "Los Ángeles", "score_home": None, "score_away": None, "date": "2026-06-18", "time_mex": "13:00", "is_mexico": False, "stadium": "SoFi Stadium", "flag_home": "https://flagcdn.com/w320/ch.png", "flag_away": "https://flagcdn.com/w320/ba.png"},
    {"id": 10, "group": "B", "status": "upcoming", "home": "Canadá", "away": "Catar", "city": "Vancouver", "score_home": None, "score_away": None, "date": "2026-06-18", "time_mex": "16:00", "is_mexico": False, "stadium": "BC Place", "flag_home": "https://flagcdn.com/w320/ca.png", "flag_away": "https://flagcdn.com/w320/qa.png"},
    {"id": 11, "group": "B", "status": "upcoming", "home": "Suiza", "away": "Canadá", "city": "Vancouver", "score_home": None, "score_away": None, "date": "2026-06-24", "time_mex": "13:00", "is_mexico": False, "stadium": "BC Place", "flag_home": "https://flagcdn.com/w320/ch.png", "flag_away": "https://flagcdn.com/w320/ca.png"},
    {"id": 12, "group": "B", "status": "upcoming", "home": "Bosnia y Herzegovina", "away": "Catar", "city": "Seattle", "score_home": None, "score_away": None, "date": "2026-06-24", "time_mex": "13:00", "is_mexico": False, "stadium": "Lumen Field", "flag_home": "https://flagcdn.com/w320/ba.png", "flag_away": "https://flagcdn.com/w320/qa.png"},

    # Grupo C
    {"id": 13, "group": "C", "status": "finished", "home": "Brasil", "away": "Marruecos", "city": "Nueva Jersey", "score_home": 1, "score_away": 1, "date": "2026-06-13", "time_mex": "16:00", "is_mexico": False, "stadium": "MetLife Stadium", "flag_home": "https://flagcdn.com/w320/br.png", "flag_away": "https://flagcdn.com/w320/ma.png"},
    {"id": 14, "group": "C", "status": "finished", "home": "Haití", "away": "Escocia", "city": "Boston", "score_home": 0, "score_away": 1, "date": "2026-06-13", "time_mex": "19:00", "is_mexico": False, "stadium": "Gillette Stadium", "flag_home": "https://flagcdn.com/w320/ht.png", "flag_away": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/320px-Flag_of_Scotland.svg.png"},
    {"id": 15, "group": "C", "status": "live", "home": "Alemania", "away": "Curazao", "city": "Houston", "score_home": 4, "score_away": 1, "date": "2026-06-14", "time_mex": "11:00", "is_mexico": False, "stadium": "NRG Stadium", "flag_home": "https://flagcdn.com/w320/de.png", "flag_away": "https://flagcdn.com/w320/cw.png"},
    {"id": 16, "group": "C", "status": "upcoming", "home": "Marruecos", "away": "Haití", "city": "Filadelfia", "score_home": None, "score_away": None, "date": "2026-06-19", "time_mex": "16:00", "is_mexico": False, "stadium": "Lincoln Financial Field", "flag_home": "https://flagcdn.com/w320/ma.png", "flag_away": "https://flagcdn.com/w320/ht.png"},
    {"id": 17, "group": "C", "status": "upcoming", "home": "Escocia", "away": "Brasil", "city": "Miami", "score_home": None, "score_away": None, "date": "2026-06-24", "time_mex": "16:00", "is_mexico": False, "stadium": "Hard Rock Stadium", "flag_home": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/320px-Flag_of_Scotland.svg.png", "flag_away": "https://flagcdn.com/w320/br.png"},
    {"id": 18, "group": "C", "status": "upcoming", "home": "Marruecos", "away": "Haití", "city": "Atlanta", "score_home": None, "score_away": None, "date": "2026-06-24", "time_mex": "16:00", "is_mexico": False, "stadium": "Mercedes-Benz Stadium", "flag_home": "https://flagcdn.com/w320/ma.png", "flag_away": "https://flagcdn.com/w320/ht.png"},

    # Grupo D
    {"id": 19, "group": "D", "status": "finished", "home": "Estados Unidos", "away": "Paraguay", "city": "Los Ángeles", "score_home": 4, "score_away": 1, "date": "2026-06-12", "time_mex": "20:00", "is_mexico": False, "stadium": "SoFi Stadium", "flag_home": "https://flagcdn.com/w320/us.png", "flag_away": "https://flagcdn.com/w320/py.png"},
    {"id": 20, "group": "D", "status": "finished", "home": "Australia", "away": "Turquía", "city": "Vancouver", "score_home": 2, "score_away": 0, "date": "2026-06-13", "time_mex": "22:00", "is_mexico": False, "stadium": "BC Place", "flag_home": "https://flagcdn.com/w320/au.png", "flag_away": "https://flagcdn.com/w320/tr.png"},
    {"id": 21, "group": "D", "status": "upcoming", "home": "Estados Unidos", "away": "Australia", "city": "Seattle", "score_home": None, "score_away": None, "date": "2026-06-19", "time_mex": "14:00", "is_mexico": False, "stadium": "Lumen Field", "flag_home": "https://flagcdn.com/w320/us.png", "flag_away": "https://flagcdn.com/w320/au.png"},
    {"id": 22, "group": "D", "status": "upcoming", "home": "Turquía", "away": "Paraguay", "city": "San Francisco", "score_home": None, "score_away": None, "date": "2026-06-19", "time_mex": "21:00", "is_mexico": False, "stadium": "Levi's Stadium", "flag_home": "https://flagcdn.com/w320/tr.png", "flag_away": "https://flagcdn.com/w320/py.png"},
    {"id": 23, "group": "D", "status": "upcoming", "home": "Turquía", "away": "Estados Unidos", "city": "Los Ángeles", "score_home": None, "score_away": None, "date": "2026-06-25", "time_mex": "20:00", "is_mexico": False, "stadium": "SoFi Stadium", "flag_home": "https://flagcdn.com/w320/tr.png", "flag_away": "https://flagcdn.com/w320/us.png"},
    {"id": 24, "group": "D", "status": "upcoming", "home": "Paraguay", "away": "Australia", "city": "San Francisco", "score_home": None, "score_away": None, "date": "2026-06-25", "time_mex": "20:00", "is_mexico": False, "stadium": "Levi's Stadium", "flag_home": "https://flagcdn.com/w320/py.png", "flag_away": "https://flagcdn.com/w320/au.png"},

    # Grupo E
    {"id": 25, "group": "E", "status": "upcoming", "home": "Países Bajos", "away": "Japón", "city": "Dallas", "score_home": None, "score_away": None, "date": "2026-06-14", "time_mex": "14:00", "is_mexico": False, "stadium": "AT&T Stadium", "flag_home": "https://flagcdn.com/w320/nl.png", "flag_away": "https://flagcdn.com/w320/jp.png"},
    {"id": 26, "group": "E", "status": "upcoming", "home": "Costa de Marfil", "away": "Ecuador", "city": "Filadelfia", "score_home": None, "score_away": None, "date": "2026-06-14", "time_mex": "17:00", "is_mexico": False, "stadium": "Lincoln Financial Field", "flag_home": "https://flagcdn.com/w320/ci.png", "flag_away": "https://flagcdn.com/w320/ec.png"},
    {"id": 27, "group": "E", "status": "upcoming", "home": "Suecia", "away": "Túnez", "city": "Monterrey", "score_home": None, "score_away": None, "date": "2026-06-14", "time_mex": "20:00", "is_mexico": False, "stadium": "Estadio BBVA", "flag_home": "https://flagcdn.com/w320/se.png", "flag_away": "https://flagcdn.com/w320/tn.png"},
    {"id": 28, "group": "E", "status": "upcoming", "home": "Alemania", "away": "Costa de Marfil", "city": "Toronto", "score_home": None, "score_away": None, "date": "2026-06-20", "time_mex": "14:00", "is_mexico": False, "stadium": "BMO Field", "flag_home": "https://flagcdn.com/w320/de.png", "flag_away": "https://flagcdn.com/w320/ci.png"},
    {"id": 29, "group": "E", "status": "upcoming", "home": "Ecuador", "away": "Curazao", "city": "Kansas City", "score_home": None, "score_away": None, "date": "2026-06-20", "time_mex": "18:00", "is_mexico": False, "stadium": "Arrowhead Stadium", "flag_home": "https://flagcdn.com/w320/ec.png", "flag_away": "https://flagcdn.com/w320/cw.png"},
    {"id": 30, "group": "E", "status": "upcoming", "home": "Países Bajos", "away": "Suecia", "city": "Houston", "score_home": None, "score_away": None, "date": "2026-06-20", "time_mex": "11:00", "is_mexico": False, "stadium": "NRG Stadium", "flag_home": "https://flagcdn.com/w320/nl.png", "flag_away": "https://flagcdn.com/w320/se.png"},
    {"id": 31, "group": "E", "status": "upcoming", "home": "Ecuador", "away": "Alemania", "city": "Nueva Jersey", "score_home": None, "score_away": None, "date": "2026-06-25", "time_mex": "14:00", "is_mexico": False, "stadium": "MetLife Stadium", "flag_home": "https://flagcdn.com/w320/ec.png", "flag_away": "https://flagcdn.com/w320/de.png"},
    {"id": 32, "group": "E", "status": "upcoming", "home": "Curazao", "away": "Costa de Marfil", "city": "Filadelfia", "score_home": None, "score_away": None, "date": "2026-06-25", "time_mex": "14:00", "is_mexico": False, "stadium": "Lincoln Financial Field", "flag_home": "https://flagcdn.com/w320/cw.png", "flag_away": "https://flagcdn.com/w320/ci.png"},

    # Grupo F
    {"id": 33, "group": "F", "status": "upcoming", "home": "Túnez", "away": "Japón", "city": "Monterrey", "score_home": None, "score_away": None, "date": "2026-06-20", "time_mex": "22:00", "is_mexico": False, "stadium": "Estadio BBVA", "flag_home": "https://flagcdn.com/w320/tn.png", "flag_away": "https://flagcdn.com/w320/jp.png"},
    {"id": 34, "group": "F", "status": "upcoming", "home": "Japón", "away": "Suecia", "city": "Dallas", "score_home": None, "score_away": None, "date": "2026-06-25", "time_mex": "17:00", "is_mexico": False, "stadium": "AT&T Stadium", "flag_home": "https://flagcdn.com/w320/jp.png", "flag_away": "https://flagcdn.com/w320/se.png"},
    {"id": 35, "group": "F", "status": "upcoming", "home": "Túnez", "away": "Países Bajos", "city": "Kansas City", "score_home": None, "score_away": None, "date": "2026-06-25", "time_mex": "17:00", "is_mexico": False, "stadium": "Arrowhead Stadium", "flag_home": "https://flagcdn.com/w320/tn.png", "flag_away": "https://flagcdn.com/w320/nl.png"},

    # Grupo G
    {"id": 36, "group": "G", "status": "upcoming", "home": "Bélgica", "away": "Egipto", "city": "Seattle", "score_home": None, "score_away": None, "date": "2026-06-15", "time_mex": "13:00", "is_mexico": False, "stadium": "Lumen Field", "flag_home": "https://flagcdn.com/w320/be.png", "flag_away": "https://flagcdn.com/w320/eg.png"},
    {"id": 37, "group": "G", "status": "upcoming", "home": "Irán", "away": "Nueva Zelanda", "city": "Los Ángeles", "score_home": None, "score_away": None, "date": "2026-06-15", "time_mex": "19:00", "is_mexico": False, "stadium": "SoFi Stadium", "flag_home": "https://flagcdn.com/w320/ir.png", "flag_away": "https://flagcdn.com/w320/nz.png"},
    {"id": 38, "group": "G", "status": "upcoming", "home": "Bélgica", "away": "Irán", "city": "Los Ángeles", "score_home": None, "score_away": None, "date": "2026-06-21", "time_mex": "13:00", "is_mexico": False, "stadium": "SoFi Stadium", "flag_home": "https://flagcdn.com/w320/be.png", "flag_away": "https://flagcdn.com/w320/ir.png"},
    {"id": 39, "group": "G", "status": "upcoming", "home": "Nueva Zelanda", "away": "Egipto", "city": "Vancouver", "score_home": None, "score_away": None, "date": "2026-06-21", "time_mex": "19:00", "is_mexico": False, "stadium": "BC Place", "flag_home": "https://flagcdn.com/w320/nz.png", "flag_away": "https://flagcdn.com/w320/eg.png"},
    {"id": 40, "group": "G", "status": "upcoming", "home": "Egipto", "away": "Irán", "city": "Seattle", "score_home": None, "score_away": None, "date": "2026-06-26", "time_mex": "21:00", "is_mexico": False, "stadium": "Lumen Field", "flag_home": "https://flagcdn.com/w320/eg.png", "flag_away": "https://flagcdn.com/w320/ir.png"},
    {"id": 41, "group": "G", "status": "upcoming", "home": "Nueva Zelanda", "away": "Bélgica", "city": "Vancouver", "score_home": None, "score_away": None, "date": "2026-06-26", "time_mex": "21:00", "is_mexico": False, "stadium": "BC Place", "flag_home": "https://flagcdn.com/w320/nz.png", "flag_away": "https://flagcdn.com/w320/be.png"},

    # Grupo H
    {"id": 42, "group": "H", "status": "upcoming", "home": "España", "away": "Cabo Verde", "city": "Atlanta", "score_home": None, "score_away": None, "date": "2026-06-15", "time_mex": "10:00", "is_mexico": False, "stadium": "Mercedes-Benz Stadium", "flag_home": "https://flagcdn.com/w320/es.png", "flag_away": "https://flagcdn.com/w320/cv.png"},
    {"id": 43, "group": "H", "status": "upcoming", "home": "Arabia Saudita", "away": "Uruguay", "city": "Miami", "score_home": None, "score_away": None, "date": "2026-06-15", "time_mex": "16:00", "is_mexico": False, "stadium": "Hard Rock Stadium", "flag_home": "https://flagcdn.com/w320/sa.png", "flag_away": "https://flagcdn.com/w320/uy.png"},
    {"id": 44, "group": "H", "status": "upcoming", "home": "España", "away": "Arabia Saudita", "city": "Atlanta", "score_home": None, "score_away": None, "date": "2026-06-21", "time_mex": "10:00", "is_mexico": False, "stadium": "Mercedes-Benz Stadium", "flag_home": "https://flagcdn.com/w320/es.png", "flag_away": "https://flagcdn.com/w320/sa.png"},
    {"id": 45, "group": "H", "status": "upcoming", "home": "Uruguay", "away": "Cabo Verde", "city": "Miami", "score_home": None, "score_away": None, "date": "2026-06-21", "time_mex": "16:00", "is_mexico": False, "stadium": "Hard Rock Stadium", "flag_home": "https://flagcdn.com/w320/uy.png", "flag_away": "https://flagcdn.com/w320/cv.png"},
    {"id": 46, "group": "H", "status": "upcoming", "home": "Uruguay", "away": "España", "city": "Guadalajara", "score_home": None, "score_away": None, "date": "2026-06-26", "time_mex": "18:00", "is_mexico": False, "stadium": "Estadio Akron", "flag_home": "https://flagcdn.com/w320/uy.png", "flag_away": "https://flagcdn.com/w320/es.png"},
    {"id": 47, "group": "H", "status": "upcoming", "home": "Cabo Verde", "away": "Arabia Saudita", "city": "Houston", "score_home": None, "score_away": None, "date": "2026-06-26", "time_mex": "18:00", "is_mexico": False, "stadium": "NRG Stadium", "flag_home": "https://flagcdn.com/w320/cv.png", "flag_away": "https://flagcdn.com/w320/sa.png"},

    # Grupo I
    {"id": 48, "group": "I", "status": "upcoming", "home": "Francia", "away": "Senegal", "city": "Nueva Jersey", "score_home": None, "score_away": None, "date": "2026-06-16", "time_mex": "13:00", "is_mexico": False, "stadium": "MetLife Stadium", "flag_home": "https://flagcdn.com/w320/fr.png", "flag_away": "https://flagcdn.com/w320/sn.png"},
    {"id": 49, "group": "I", "status": "upcoming", "home": "Irak", "away": "Noruega", "city": "Boston", "score_home": None, "score_away": None, "date": "2026-06-16", "time_mex": "16:00", "is_mexico": False, "stadium": "Gillette Stadium", "flag_home": "https://flagcdn.com/w320/iq.png", "flag_away": "https://flagcdn.com/w320/no.png"},
    {"id": 50, "group": "I", "status": "upcoming", "home": "Francia", "away": "Irak", "city": "Filadelfia", "score_home": None, "score_away": None, "date": "2026-06-22", "time_mex": "15:00", "is_mexico": False, "stadium": "Lincoln Financial Field", "flag_home": "https://flagcdn.com/w320/fr.png", "flag_away": "https://flagcdn.com/w320/iq.png"},
    {"id": 51, "group": "I", "status": "upcoming", "home": "Noruega", "away": "Senegal", "city": "Nueva Jersey", "score_home": None, "score_away": None, "date": "2026-06-22", "time_mex": "18:00", "is_mexico": False, "stadium": "MetLife Stadium", "flag_home": "https://flagcdn.com/w320/no.png", "flag_away": "https://flagcdn.com/w320/sn.png"},
    {"id": 52, "group": "I", "status": "upcoming", "home": "Noruega", "away": "Francia", "city": "Boston", "score_home": None, "score_away": None, "date": "2026-06-26", "time_mex": "13:00", "is_mexico": False, "stadium": "Gillette Stadium", "flag_home": "https://flagcdn.com/w320/no.png", "flag_away": "https://flagcdn.com/w320/fr.png"},
    {"id": 53, "group": "I", "status": "upcoming", "home": "Senegal", "away": "Irak", "city": "Toronto", "score_home": None, "score_away": None, "date": "2026-06-26", "time_mex": "13:00", "is_mexico": False, "stadium": "BMO Field", "flag_home": "https://flagcdn.com/w320/sn.png", "flag_away": "https://flagcdn.com/w320/iq.png"},

    # Grupo J
    {"id": 54, "group": "J", "status": "upcoming", "home": "Argentina", "away": "Argelia", "city": "Kansas City", "score_home": None, "score_away": None, "date": "2026-06-16", "time_mex": "19:00", "is_mexico": False, "stadium": "Arrowhead Stadium", "flag_home": "https://flagcdn.com/w320/ar.png", "flag_away": "https://flagcdn.com/w320/dz.png"},
    {"id": 55, "group": "J", "status": "upcoming", "home": "Austria", "away": "Jordania", "city": "San Francisco", "score_home": None, "score_away": None, "date": "2026-06-16", "time_mex": "22:00", "is_mexico": False, "stadium": "Levi's Stadium", "flag_home": "https://flagcdn.com/w320/at.png", "flag_away": "https://flagcdn.com/w320/jo.png"},
    {"id": 56, "group": "J", "status": "upcoming", "home": "Argentina", "away": "Austria", "city": "Dallas", "score_home": None, "score_away": None, "date": "2026-06-22", "time_mex": "11:00", "is_mexico": False, "stadium": "AT&T Stadium", "flag_home": "https://flagcdn.com/w320/ar.png", "flag_away": "https://flagcdn.com/w320/at.png"},
    {"id": 57, "group": "J", "status": "upcoming", "home": "Jordania", "away": "Argelia", "city": "San Francisco", "score_home": None, "score_away": None, "date": "2026-06-22", "time_mex": "21:00", "is_mexico": False, "stadium": "Levi's Stadium", "flag_home": "https://flagcdn.com/w320/jo.png", "flag_away": "https://flagcdn.com/w320/dz.png"},
    {"id": 58, "group": "J", "status": "upcoming", "home": "Argelia", "away": "Austria", "city": "Kansas City", "score_home": None, "score_away": None, "date": "2026-06-27", "time_mex": "20:00", "is_mexico": False, "stadium": "Arrowhead Stadium", "flag_home": "https://flagcdn.com/w320/dz.png", "flag_away": "https://flagcdn.com/w320/at.png"},
    {"id": 59, "group": "J", "status": "upcoming", "home": "Jordania", "away": "Argentina", "city": "Dallas", "score_home": None, "score_away": None, "date": "2026-06-27", "time_mex": "20:00", "is_mexico": False, "stadium": "AT&T Stadium", "flag_home": "https://flagcdn.com/w320/jo.png", "flag_away": "https://flagcdn.com/w320/ar.png"},

    # Grupo K
    {"id": 60, "group": "K", "status": "upcoming", "home": "Portugal", "away": "República Democrática del Congo", "city": "Houston", "score_home": None, "score_away": None, "date": "2026-06-17", "time_mex": "11:00", "is_mexico": False, "stadium": "NRG Stadium", "flag_home": "https://flagcdn.com/w320/pt.png", "flag_away": "https://flagcdn.com/w320/cd.png"},
    {"id": 61, "group": "K", "status": "upcoming", "home": "Uzbekistán", "away": "Colombia", "city": "CDMX", "score_home": None, "score_away": None, "date": "2026-06-17", "time_mex": "20:00", "is_mexico": False, "stadium": "Estadio Azteca", "flag_home": "https://flagcdn.com/w320/uz.png", "flag_away": "https://flagcdn.com/w320/co.png"},
    {"id": 62, "group": "K", "status": "upcoming", "home": "Portugal", "away": "Uzbekistán", "city": "Houston", "score_home": None, "score_away": None, "date": "2026-06-23", "time_mex": "11:00", "is_mexico": False, "stadium": "NRG Stadium", "flag_home": "https://flagcdn.com/w320/pt.png", "flag_away": "https://flagcdn.com/w320/uz.png"},
    {"id": 63, "group": "K", "status": "upcoming", "home": "Colombia", "away": "República Democrática del Congo", "city": "Guadalajara", "score_home": None, "score_away": None, "date": "2026-06-23", "time_mex": "20:00", "is_mexico": False, "stadium": "Estadio Akron", "flag_home": "https://flagcdn.com/w320/co.png", "flag_away": "https://flagcdn.com/w320/cd.png"},
    {"id": 64, "group": "K", "status": "upcoming", "home": "Colombia", "away": "Portugal", "city": "Miami", "score_home": None, "score_away": None, "date": "2026-06-27", "time_mex": "17:30", "is_mexico": False, "stadium": "Hard Rock Stadium", "flag_home": "https://flagcdn.com/w320/co.png", "flag_away": "https://flagcdn.com/w320/pt.png"},
    {"id": 65, "group": "K", "status": "upcoming", "home": "República Democrática del Congo", "away": "Uzbekistán", "city": "Atlanta", "score_home": None, "score_away": None, "date": "2026-06-27", "time_mex": "17:30", "is_mexico": False, "stadium": "Mercedes-Benz Stadium", "flag_home": "https://flagcdn.com/w320/cd.png", "flag_away": "https://flagcdn.com/w320/uz.png"},

    # Grupo L
    {"id": 66, "group": "L", "status": "upcoming", "home": "Inglaterra", "away": "Croacia", "city": "Dallas", "score_home": None, "score_away": None, "date": "2026-06-17", "time_mex": "14:00", "is_mexico": False, "stadium": "AT&T Stadium", "flag_home": "https://flagcdn.com/w320/gb.png", "flag_away": "https://flagcdn.com/w320/hr.png"},
    {"id": 67, "group": "L", "status": "upcoming", "home": "Ghana", "away": "Panamá", "city": "Toronto", "score_home": None, "score_away": None, "date": "2026-06-17", "time_mex": "17:00", "is_mexico": False, "stadium": "BMO Field", "flag_home": "https://flagcdn.com/w320/gh.png", "flag_away": "https://flagcdn.com/w320/pa.png"},
    {"id": 68, "group": "L", "status": "upcoming", "home": "Inglaterra", "away": "Ghana", "city": "Boston", "score_home": None, "score_away": None, "date": "2026-06-23", "time_mex": "14:00", "is_mexico": False, "stadium": "Gillette Stadium", "flag_home": "https://flagcdn.com/w320/gb.png", "flag_away": "https://flagcdn.com/w320/gh.png"},
    {"id": 69, "group": "L", "status": "upcoming", "home": "Panamá", "away": "Croacia", "city": "Toronto", "score_home": None, "score_away": None, "date": "2026-06-23", "time_mex": "17:00", "is_mexico": False, "stadium": "BMO Field", "flag_home": "https://flagcdn.com/w320/pa.png", "flag_away": "https://flagcdn.com/w320/hr.png"},
    {"id": 70, "group": "L", "status": "upcoming", "home": "Panamá", "away": "Inglaterra", "city": "Nueva Jersey", "score_home": None, "score_away": None, "date": "2026-06-27", "time_mex": "15:00", "is_mexico": False, "stadium": "MetLife Stadium", "flag_home": "https://flagcdn.com/w320/pa.png", "flag_away": "https://flagcdn.com/w320/gb.png"},
    {"id": 71, "group": "L", "status": "upcoming", "home": "Croacia", "away": "Ghana", "city": "Filadelfia", "score_home": None, "score_away": None, "date": "2026-06-27", "time_mex": "15:00", "is_mexico": False, "stadium": "Lincoln Financial Field", "flag_home": "https://flagcdn.com/w320/hr.png", "flag_away": "https://flagcdn.com/w320/gh.png"},
]

# ============================================================
# ZONA HORARIA Y CÁLCULO DE ESTADO
# ============================================================
mexico_tz = pytz.timezone('America/Mexico_City')

def calcular_estado_automatico(match):
    try:
        time_str = match.get("time_mex", "")
        date_str = match.get("date", "")
        
        if not time_str or not date_str:
            return "upcoming"
        
        fecha_partido = datetime.strptime(date_str, "%Y-%m-%d")
        hora_partido = datetime.strptime(time_str, "%H:%M").time()
        datetime_partido = mexico_tz.localize(datetime.combine(fecha_partido, hora_partido))
        
        ahora = datetime.now(mexico_tz)
        diff_minutos = (datetime_partido - ahora).total_seconds() / 60
        
        if diff_minutos < -120:
            return "finished"
        elif diff_minutos <= 0:
            return "live"
        elif diff_minutos <= 30:
            return "upcoming_soon"
        else:
            return "upcoming"
    except Exception:
        return "upcoming"

# ============================================================
# ARCHIVO DE CACHÉ
# ============================================================
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

# ============================================================
# API EN VIVO
# ============================================================
def fetch_live_from_api():
    try:
        url = "https://v3.football.api-sports.io/fixtures?live=all&league=1"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def update_matches_from_api():
    data = fetch_live_from_api()
    if not data or 'response' not in data:
        return
    
    marcadores = load_marcadores()
    
    for fixture in data.get('response', []):
        try:
            home_name = fixture.get('teams', {}).get('home', {}).get('name', '')
            away_name = fixture.get('teams', {}).get('away', {}).get('name', '')
            
            match_id = None
            for m in MATCHES:
                if m['home'].lower() == home_name.lower() and m['away'].lower() == away_name.lower():
                    match_id = m['id']
                    break
            
            if match_id:
                status_short = fixture.get('fixture', {}).get('status', {}).get('short', '')
                home_score = fixture.get('goals', {}).get('home') or 0
                away_score = fixture.get('goals', {}).get('away') or 0
                
                if status_short in ['1H', '2H', 'HT', 'LIVE']:
                    display_status = 'live'
                elif status_short in ['FT', 'AET', 'PEN']:
                    display_status = 'finished'
                else:
                    continue
                
                marcadores[str(match_id)] = {
                    "score_home": home_score,
                    "score_away": away_score,
                    "status": display_status,
                    "last_sync": datetime.now().isoformat()
                }
        except Exception:
            continue
    
    if marcadores:
        save_marcadores(marcadores)

def background_sync():
    while True:
        try:
            update_matches_from_api()
        except Exception:
            pass
        time.sleep(15)

sync_thread = threading.Thread(target=background_sync, daemon=True)
sync_thread.start()

# ============================================================
# OBTENER PARTIDOS CON DATOS EN VIVO
# ============================================================
def get_matches_with_live_data():
    marcadores = load_marcadores()
    result = []
    
    for m in MATCHES:
        match = dict(m)
        live = marcadores.get(str(match["id"]))
        
        if live:
            match["score_home"] = live.get("score_home", match.get("score_home"))
            match["score_away"] = live.get("score_away", match.get("score_away"))
            match["status"] = live.get("status", match.get("status"))
        else:
            match["status"] = calcular_estado_automatico(match)
        
        # Forzar resultado de Alemania vs Curazao
        if match["id"] == 15:
            match["score_home"] = 7
            match["score_away"] = 1
            if match["status"] != "finished":
                match["status"] = "finished"
        
        result.append(match)
    
    return result

# ============================================================
# RUTAS DE FLASK
# ============================================================

@app.route('/')
def index():
    return render_template('index.html', matches=get_matches_with_live_data())

@app.route('/match/<int:match_id>')
def match_view(match_id):
    match = next((m for m in get_matches_with_live_data() if m["id"] == match_id), None)
    if match is None:
        return "Partido no encontrado", 404
    return render_template('stream.html', match=match, stream_links=STREAM_LINKS)

@app.route('/admin')
def admin_panel():
    return render_template('admin.html', matches=get_matches_with_live_data())

@app.route('/api/status')
def api_status_all():
    matches = get_matches_with_live_data()
    return jsonify([
        {
            "id": m["id"],
            "home": m["home"],
            "away": m["away"],
            "score_home": m.get("score_home", 0) if m.get("score_home") is not None else 0,
            "score_away": m.get("score_away", 0) if m.get("score_away") is not None else 0,
            "status": m.get("status", "upcoming"),
            "time_mex": m.get("time_mex", ""),
            "date": m.get("date", ""),
            "city": m.get("city", ""),
            "group": m.get("group", ""),
            "stadium": m.get("stadium", ""),
            "flag_home": m.get("flag_home", ""),
            "flag_away": m.get("flag_away", "")
        }
        for m in matches
    ])

@app.route('/api/status/<int:match_id>')
def api_status(match_id):
    match = next((m for m in get_matches_with_live_data() if m["id"] == match_id), None)
    if match is None:
        return jsonify({"error": "Partido no encontrado"}), 404
    return jsonify({
        "score_home": match.get("score_home", 0),
        "score_away": match.get("score_away", 0),
        "status": match.get("status", "upcoming")
    })

@app.route('/admin/update')
def update_score():
    match_id = request.args.get('id')
    if not match_id:
        return "Falta el parámetro id", 400

    marcadores = load_marcadores()
    marcadores[match_id] = {
        "score_home": int(request.args.get('h', 0)),
        "score_away": int(request.args.get('a', 0)),
        "status": request.args.get('s', 'upcoming'),
        "last_update_manual": datetime.now().isoformat()
    }
    save_marcadores(marcadores)
    return "Actualizado correctamente"

@app.route('/admin/sync-now')
def sync_now():
    update_matches_from_api()
    return jsonify({"success": True, "message": "Sincronización forzada completada"})

def keep_alive():
    """Mantiene la aplicación activa haciendo peticiones cada 10 minutos"""
    while True:
        time.sleep(600)  # 10 minutos
        try:
            requests.get('https://tu-app.onrender.com/api/status')
            print("🟢 Keep-alive ping enviado")
        except:
            print("🔴 Error en keep-alive")

# Iniciar hilo de keep-alive
if not os.environ.get('RENDER'):
    # Solo en Render, no localmente
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
