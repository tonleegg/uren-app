import tkinter as tk
from tkinter import font
import urllib.request
import urllib.parse
import json
import ssl
import threading
from datetime import datetime

ssl_context = ssl._create_unverified_context()

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
    with urllib.request.urlopen(url, context=ssl_context) as r:
        data = json.loads(r.read())
    return data["current_weather"]

def bepaal_begroeting():
    uur = datetime.now().hour
    if uur < 12:
        return "Goedemorgen"
    elif uur < 18:
        return "Goedemiddag"
    return "Goedenavond"


class BegroetingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Begroeting")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self._build_ui()

    def _build_ui(self):
        padding = {"padx": 20, "pady": 10}

        # Titel
        titel_font = font.Font(family="Helvetica Neue", size=22, weight="bold")
        tk.Label(self.root, text="Begroeting", font=titel_font,
                 bg="#f0f0f0", fg="#000000").grid(row=0, column=0, columnspan=2,
                 pady=(24, 4))

        # Naam
        label_font = font.Font(family="Helvetica Neue", size=13)
        tk.Label(self.root, text="Naam", font=label_font,
                 bg="#f0f0f0", fg="black", anchor="w").grid(row=1, column=0, columnspan=2,
                 sticky="w", padx=20, pady=(10, 0))

        self.naam_var = tk.StringVar()
        naam_entry = tk.Entry(self.root, textvariable=self.naam_var,
                              font=label_font, width=32, relief="flat",
                              fg="black", bg="white", highlightthickness=1,
                              highlightbackground="#cccccc",
                              highlightcolor="#0066cc")
        naam_entry.grid(row=2, column=0, columnspan=2, **padding)
        naam_entry.bind("<Return>", lambda e: self.verwerk())

        # Stad
        tk.Label(self.root, text="Stad", font=label_font,
                 bg="#f0f0f0", fg="black", anchor="w").grid(row=3, column=0, columnspan=2,
                 sticky="w", padx=20, pady=(0, 0))

        self.stad_var = tk.StringVar()
        stad_entry = tk.Entry(self.root, textvariable=self.stad_var,
                              font=label_font, width=32, relief="flat",
                              fg="black", bg="white", highlightthickness=1,
                              highlightbackground="#cccccc",
                              highlightcolor="#0066cc")
        stad_entry.grid(row=4, column=0, columnspan=2, **padding)
        stad_entry.bind("<Return>", lambda e: self.verwerk())

        # Knop
        knop_font = font.Font(family="Helvetica Neue", size=13, weight="bold")
        self.knop = tk.Button(self.root, text="Toon begroeting",
                              font=knop_font, bg="#0066cc", fg="white",
                              activebackground="#0052a3", activeforeground="white",
                              relief="flat", cursor="hand2", padx=16, pady=8,
                              command=self.verwerk)
        self.knop.grid(row=5, column=0, columnspan=2, pady=(4, 16))

        # Resultaatvak
        self.resultaat_var = tk.StringVar()
        resultaat_font = font.Font(family="Helvetica Neue", size=14)
        self.resultaat_label = tk.Label(self.root, textvariable=self.resultaat_var,
                                        font=resultaat_font, bg="#ffffff",
                                        fg="#000000", wraplength=340,
                                        justify="center", relief="flat",
                                        width=36, height=4)
        self.resultaat_label.grid(row=6, column=0, columnspan=2,
                                  padx=20, pady=(0, 24))
        self.resultaat_label.grid_remove()

    def verwerk(self):
        naam = self.naam_var.get().strip()
        stad = self.stad_var.get().strip()

        if not naam:
            self._toon_resultaat("Vul eerst je naam in.", fout=True)
            return
        if not stad:
            self._toon_resultaat("Vul eerst een stad in.", fout=True)
            return

        self.knop.config(state="disabled", text="Bezig...")
        self._toon_resultaat("Weer ophalen...", fout=False)

        threading.Thread(target=self._haal_data, args=(naam, stad), daemon=True).start()

    def _haal_data(self, naam, stad):
        try:
            lat, lon = haal_coordinaten(stad)
            if lat is None:
                self.root.after(0, self._toon_resultaat,
                                f"Stad '{stad}' niet gevonden.", True)
                return

            weer = haal_weer(lat, lon)
            begroeting = bepaal_begroeting()
            code = weer["weathercode"]
            beschrijving = WEERCODES.get(code, "Onbekend")
            temperatuur = weer["temperature"]
            windsnelheid = weer["windspeed"]

            tekst = (f"{begroeting}, {naam}!\n\n"
                     f"{stad.title()}: {beschrijving}\n"
                     f"{temperatuur}°C  •  Wind {windsnelheid} km/u")
            self.root.after(0, self._toon_resultaat, tekst, False)

        except Exception as e:
            self.root.after(0, self._toon_resultaat, f"Fout: {e}", True)

    def _toon_resultaat(self, tekst, fout=False):
        self.resultaat_var.set(tekst)
        self.resultaat_label.config(fg="#cc0000" if fout else "#000000")
        self.resultaat_label.grid()
        self.knop.config(state="normal", text="Toon begroeting")


if __name__ == "__main__":
    root = tk.Tk()
    app = BegroetingApp(root)
    root.mainloop()
