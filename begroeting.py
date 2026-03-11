import urllib.request
import urllib.parse
import json
import ssl
from datetime import datetime

ssl_context = ssl._create_unverified_context()

# Weercodes van WMO naar een leesbare beschrijving
WEERCODES = {
    0: "Heldere lucht",
    1: "Overwegend helder", 2: "Gedeeltelijk bewolkt", 3: "Bewolkt",
    45: "Mist", 48: "Rijpmist",
    51: "Lichte motregen", 53: "Motregen", 55: "Zware motregen",
    61: "Lichte regen", 63: "Regen", 65: "Zware regen",
    71: "Lichte sneeuw", 73: "Sneeuw", 75: "Zware sneeuw",
    80: "Lichte buien", 81: "Buien", 82: "Zware buien",
    95: "Onweer", 96: "Onweer met hagel", 99: "Zwaar onweer met hagel",
}

def haal_coordinaten(stad):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(stad)}&count=1&language=nl"
    with urllib.request.urlopen(url, context=ssl_context) as r:
        data = json.loads(r.read())
    resultaten = data.get("results")
    if not resultaten:
        return None, None
    return resultaten[0]["latitude"], resultaten[0]["longitude"]

def haal_weer(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())
    return data["current_weather"]

import urllib.parse

uur = datetime.now().hour

if uur < 12:
    begroeting = "Goedemorgen"
elif uur < 18:
    begroeting = "Goedemiddag"
else:
    begroeting = "Goedenavond"

naam = input("Wat is je naam? ")
stad = input("Voor welke stad wil je het weer zien? ")

print(f"\n{begroeting}, {naam}!")

lat, lon = haal_coordinaten(stad)
if lat is None:
    print(f"Stad '{stad}' niet gevonden.")
else:
    weer = haal_weer(lat, lon)
    code = weer["weathercode"]
    beschrijving = WEERCODES.get(code, "Onbekend")
    temperatuur = weer["temperature"]
    windsnelheid = weer["windspeed"]
    print(f"Weer in {stad}: {beschrijving}, {temperatuur}°C, wind {windsnelheid} km/u")
