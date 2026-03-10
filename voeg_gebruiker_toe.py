import bcrypt
import gspread

# ── Instellingen ───────────────────────────────────────────────
CREDENTIALS_PAD = "/Users/tleeggangers/Downloads/ambient-net-489719-d1-852ddb2e0654.json"
SHEET_ID        = "1e8mtGjw2Z3PVPCmcZbYIfc7GWlo915d9qGhBDCwT1eM"  # pas aan

GEBRUIKERSNAAM  = "ton"
WACHTWOORD      = "Tl011068!"
NAAM            = "Ton Leeggangers"
# ───────────────────────────────────────────────────────────────

wachtwoord_hash = bcrypt.hashpw(WACHTWOORD.encode(), bcrypt.gensalt()).decode()

client      = gspread.service_account(filename=CREDENTIALS_PAD)
spreadsheet = client.open_by_key(SHEET_ID)

bestaande_namen = [ws.title for ws in spreadsheet.worksheets()]
if "gebruikers" not in bestaande_namen:
    sheet = spreadsheet.add_worksheet("gebruikers", rows=100, cols=3)
    sheet.append_row(["gebruikersnaam", "wachtwoord_hash", "naam"])
else:
    sheet = spreadsheet.worksheet("gebruikers")

# Bestaande rij bijwerken als gebruiker al bestaat, anders toevoegen
records = sheet.get_all_records()
bestaande_rij = next((i + 2 for i, r in enumerate(records) if r["gebruikersnaam"] == GEBRUIKERSNAAM), None)

if bestaande_rij:
    sheet.update(f"A{bestaande_rij}:C{bestaande_rij}", [[GEBRUIKERSNAAM, wachtwoord_hash, NAAM]])
    print(f"Gebruiker '{GEBRUIKERSNAAM}' bijgewerkt op rij {bestaande_rij}.")
else:
    sheet.append_row([GEBRUIKERSNAAM, wachtwoord_hash, NAAM])
    print(f"Gebruiker '{GEBRUIKERSNAAM}' toegevoegd.")

print(f"Hash: {wachtwoord_hash}")
