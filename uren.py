import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pycountry
from datetime import date, datetime
from supabase import create_client

LANDEN = sorted([c.name for c in pycountry.countries])
STANDAARD_LAND = "Netherlands"
LOGO_PAD = "daauw kl.png"
OPDRACHT_STATUSSEN = ["Actief", "Aangevraagd", "Gepauzeerd", "Afgerond"]
EENHEDEN = ["uur", "dag", "week", "stuk", "project"]
EENHEID_MEERVOUD = {"uur": "uren", "dag": "dagen", "week": "weken", "stuk": "stuks", "project": "projecten"}

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #ffffff !important;
}
[data-testid="stHeader"] {
    background-color: #ffffff !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}
section[data-testid="stSidebar"] {
    background-color: #f4f6f7 !important;
    border-right: 1px solid #d5d8dc !important;
}
h1 { color: #1a5276 !important; font-size: 1.6rem !important; font-weight: 700 !important; }
h2 { color: #1a5276 !important; font-weight: 600 !important; }
h3 { color: #1a5276 !important; font-size: 0.85rem !important; font-weight: 700 !important;
     letter-spacing: 0.04em !important; text-transform: uppercase !important; margin-bottom: 2px !important; }
p, label, .stMarkdown p { color: #2c3e50 !important; }

[data-testid="stForm"] {
    background-color: #f8f9fa !important;
    border: 1px solid #d5d8dc !important;
    border-top: 3px solid #1a5276 !important;
    border-radius: 8px !important;
    padding: 1.2rem 1.4rem !important;
}
.stTextInput input, .stNumberInput input, .stDateInput input {
    background-color: #ffffff !important; color: #2c3e50 !important;
    border: 1px solid #aab7b8 !important; border-radius: 6px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
    border-color: #1a5276 !important; box-shadow: 0 0 0 2px rgba(26,82,118,0.12) !important;
}
.stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label {
    color: #7f8c8d !important; font-size: 0.82rem !important; font-weight: 600 !important;
}
.stSelectbox [data-baseweb="select"] > div {
    background-color: #ffffff !important; border-color: #aab7b8 !important; border-radius: 6px !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div { color: #2c3e50 !important; }
[data-baseweb="popover"] {
    background-color: #ffffff !important; border-color: #aab7b8 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.10) !important;
}
[data-baseweb="menu"] { background-color: #ffffff !important; }
[role="option"] { background-color: #ffffff !important; color: #2c3e50 !important; }
[role="option"]:hover { background-color: #eaf0fb !important; color: #1a5276 !important; }

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p { color: #2c3e50 !important; }

.stButton > button {
    background-color: #ffffff !important; color: #7f8c8d !important;
    border: 1px solid #d5d8dc !important; border-radius: 6px !important;
    font-size: 0.85rem !important; padding: 4px 10px !important;
    transition: border-color 0.15s, background-color 0.15s, color 0.15s !important;
}
.stButton > button:hover {
    background-color: #eaf0fb !important; border-color: #1a5276 !important; color: #1a5276 !important;
}
.stFormSubmitButton > button {
    background-color: #1a5276 !important; color: #ffffff !important; border: none !important;
    border-radius: 6px !important; font-weight: 600 !important; width: 100% !important;
    padding: 8px !important; transition: background-color 0.15s !important;
}
.stFormSubmitButton > button:hover { background-color: #154360 !important; }
[data-testid="stAlert"] { border-radius: 6px !important; }
hr { border-color: #d5d8dc !important; opacity: 1 !important; margin: 6px 0 !important; }

.uren-sectie-label {
    color: #1a5276; font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding-bottom: 6px; border-bottom: 2px solid #1a5276; margin-bottom: 0;
}
.uren-kaart {
    background-color: #f8f9fa; border-radius: 8px; padding: 12px 16px;
    margin-bottom: 6px; border: 1px solid #d5d8dc; border-left: 3px solid #1a5276;
}
.uren-kaart-title { font-weight: 700; font-size: 1rem; color: #1a5276; margin-bottom: 2px; }
.uren-kaart-sub { color: #2c3e50; font-size: 0.85rem; margin-bottom: 4px; }
.uren-kaart-meta { color: #7f8c8d; font-size: 0.82rem; }
.uren-badge {
    display: inline-block; background-color: #1a5276; color: #ffffff;
    border-radius: 6px; padding: 2px 10px; font-size: 0.82rem;
    font-weight: 600; float: right; margin-top: -2px;
}
.badge-groen {
    display: inline-block; background-color: #1e8449; color: #ffffff;
    border-radius: 6px; padding: 2px 10px; font-size: 0.82rem; font-weight: 600;
    float: right; margin-top: -2px;
}
.badge-grijs {
    display: inline-block; background-color: #7f8c8d; color: #ffffff;
    border-radius: 6px; padding: 2px 10px; font-size: 0.82rem; font-weight: 600;
    float: right; margin-top: -2px;
}
.totaal-rij {
    text-align: right; color: #1a5276; font-size: 0.9rem; font-weight: 700;
    border-top: 1px solid #d5d8dc; padding-top: 6px; margin-top: 4px;
}
[data-testid="stImage"] {
    overflow: visible !important; max-width: none !important; padding-right: 1rem !important;
}
[data-testid="stImage"] img { max-width: none !important; overflow: visible !important; }
</style>
"""


# ── Supabase ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=60)
def laad_klanten() -> pd.DataFrame:
    res = get_client().table("klanten").select("*").order("bedrijfsnaam").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "bedrijfsnaam", "straat", "postcode", "plaats", "land"])


@st.cache_data(ttl=60)
def laad_contactpersonen() -> pd.DataFrame:
    res = get_client().table("contactpersonen").select("*").order("voornaam").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "klant_id", "voornaam", "achternaam", "email", "telefoonnummer"])


@st.cache_data(ttl=60)
def laad_activiteiten() -> pd.DataFrame:
    res = get_client().table("activiteiten").select("*").order("omschrijving").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "omschrijving", "eenheid", "standaard_tarief"])


@st.cache_data(ttl=60)
def laad_opdrachten() -> pd.DataFrame:
    res = get_client().table("opdrachten").select("*").order("projectcode").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "klant_id", "projectcode", "omschrijving", "startdatum", "einddatum", "status"])


@st.cache_data(ttl=60)
def laad_uren() -> pd.DataFrame:
    res = get_client().table("uren").select("*").order("datum", desc=True).execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "klant_id", "opdracht_id", "activiteit_id", "datum", "aantal_eenheden", "eenheidstarief"])


def login(email: str, wachtwoord: str):
    try:
        res = get_client().auth.sign_in_with_password({"email": email, "password": wachtwoord})
        return res.user
    except Exception:
        return None


# ── CRUD ───────────────────────────────────────────────────────────────────────
def _ts():
    return datetime.now().isoformat()


def voeg_klant_toe(rij: dict):
    get_client().table("klanten").insert(rij).execute()
    laad_klanten.clear()


def voeg_contactpersoon_toe(rij: dict):
    get_client().table("contactpersonen").insert(rij).execute()
    laad_contactpersonen.clear()


def voeg_activiteit_toe(rij: dict):
    get_client().table("activiteiten").insert(rij).execute()
    laad_activiteiten.clear()


def voeg_opdracht_toe(rij: dict):
    get_client().table("opdrachten").insert(rij).execute()
    laad_opdrachten.clear()


def sla_uren_op(rij: dict):
    rij["timestamp"] = _ts()
    get_client().table("uren").insert(rij).execute()
    laad_uren.clear()


def verwijder_uur(rij_id: int):
    get_client().table("uren").delete().eq("id", rij_id).execute()
    laad_uren.clear()


def verwijder_klant(rij_id: int):
    get_client().table("klanten").delete().eq("id", rij_id).execute()
    laad_klanten.clear()


def verwijder_contactpersoon(rij_id: int):
    get_client().table("contactpersonen").delete().eq("id", rij_id).execute()
    laad_contactpersonen.clear()


def verwijder_activiteit(rij_id: int):
    get_client().table("activiteiten").delete().eq("id", rij_id).execute()
    laad_activiteiten.clear()


def verwijder_opdracht(rij_id: int):
    get_client().table("opdrachten").delete().eq("id", rij_id).execute()
    laad_opdrachten.clear()


# ── Pagina-config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="daauw – Urenregistratie", page_icon="⏱️", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

# ── Login ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("ingelogd"):
    _, col, _ = st.columns([1, 2, 1])
    with col:
        try:
            st.image(LOGO_PAD, width=240, use_container_width=False)
        except Exception:
            pass
        st.title("Inloggen")
        with st.form("login_formulier"):
            email_input = st.text_input("E-mailadres")
            wachtwoord_input = st.text_input("Wachtwoord", type="password")
            inloggen = st.form_submit_button("Inloggen", type="primary", use_container_width=True)
        if inloggen:
            user = login(email_input.strip(), wachtwoord_input)
            if user:
                st.session_state["ingelogd"] = True
                st.session_state["gebruiker_email"] = user.email
                naam = (user.user_metadata or {}).get("full_name") or user.email
                st.session_state["gebruiker_naam"] = naam
                st.rerun()
            else:
                st.error("E-mailadres of wachtwoord onjuist.")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{st.session_state['gebruiker_naam']}**")
    st.divider()
    pagina = st.radio(
        "Navigatie",
        ["Urenregistratie", "Klanten", "Contactpersonen", "Activiteiten", "Opdrachten"],
        label_visibility="collapsed",
    )
    st.divider()
    if st.button("Uitloggen", use_container_width=True):
        get_client().auth.sign_out()
        for k in ["ingelogd", "gebruiker_naam", "gebruiker_email"]:
            st.session_state[k] = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA: Urenregistratie
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "Urenregistratie":
    try:
        st.image(LOGO_PAD, width=200, use_container_width=False)
    except Exception:
        pass
    st.title("Urenregistratie")

    df_klanten = laad_klanten()
    df_activiteiten = laad_activiteiten()
    df_opdrachten = laad_opdrachten()

    if df_klanten.empty:
        st.warning("Voeg eerst een klant toe via 'Klanten'.")
    elif df_activiteiten.empty:
        st.warning("Voeg eerst een activiteit toe via 'Activiteiten'.")
    else:
        klant_namen = df_klanten["bedrijfsnaam"].tolist()
        act_namen = df_activiteiten["omschrijving"].tolist()

        st.markdown("### Nieuwe uren invoeren")

        # Klant en activiteit buiten het formulier voor auto-fill
        col1, col2 = st.columns(2)
        with col1:
            klant_naam = st.selectbox("Klant *", klant_namen, key="uren_klant_sb")
        with col2:
            act_naam = st.selectbox("Activiteit *", act_namen, key="uren_act_sb")

        def _get_tarief(omschrijving):
            r = df_activiteiten[df_activiteiten["omschrijving"] == omschrijving]
            return float(r.iloc[0]["standaard_tarief"]) if not r.empty else 0.0

        def _get_eenheid(omschrijving):
            r = df_activiteiten[df_activiteiten["omschrijving"] == omschrijving]
            return r.iloc[0]["eenheid"] if not r.empty else "uur"

        # Auto-fill tarief wanneer activiteit wijzigt
        if st.session_state.get("_uren_prev_act") != act_naam:
            st.session_state["_uren_prev_act"] = act_naam
            st.session_state["_uren_default_tarief"] = _get_tarief(act_naam)
            if "_uren_tarief_input" in st.session_state:
                del st.session_state["_uren_tarief_input"]

        default_tarief = st.session_state.get("_uren_default_tarief", _get_tarief(act_naam))
        eenheid = _get_eenheid(act_naam)
        mv = EENHEID_MEERVOUD.get(eenheid, eenheid + "en")

        # Opdrachten voor gekozen klant
        klant_row = df_klanten[df_klanten["bedrijfsnaam"] == klant_naam].iloc[0]
        klant_id = str(klant_row["id"])
        actieve_opdrachten = (
            df_opdrachten[
                (df_opdrachten["klant_id"].astype(str) == klant_id) &
                (df_opdrachten["status"] == "Actief")
            ]
            if not df_opdrachten.empty
            else pd.DataFrame()
        )
        opdracht_opties = ["— geen opdracht —"]
        if not actieve_opdrachten.empty:
            opdracht_opties += (
                actieve_opdrachten["projectcode"] + " · " + actieve_opdrachten["omschrijving"]
            ).tolist()

        with st.form("uren_formulier", clear_on_submit=True):
            col3, col4 = st.columns(2)
            with col3:
                opdracht_keuze = st.selectbox("Opdracht (optioneel)", opdracht_opties)
                datum = st.date_input("Datum", value=date.today())
            with col4:
                eenheden = st.number_input(
                    f"Aantal {mv}", min_value=0.0, step=0.5, format="%.1f"
                )
                tarief = st.number_input(
                    f"Tarief per {eenheid} (€)",
                    min_value=0.0,
                    value=default_tarief,
                    step=1.0,
                    format="%.2f",
                    key="_uren_tarief_input",
                )
            opslaan = st.form_submit_button("Opslaan", type="primary", use_container_width=True)

        if opslaan:
            if eenheden <= 0:
                st.error(f"Aantal {mv} moet groter zijn dan 0.")
            else:
                opdracht_id = None
                if opdracht_keuze != "— geen opdracht —":
                    code = opdracht_keuze.split(" · ")[0]
                    match = actieve_opdrachten[actieve_opdrachten["projectcode"] == code]
                    if not match.empty:
                        opdracht_id = str(match.iloc[0]["id"])

                act_id = str(df_activiteiten[df_activiteiten["omschrijving"] == act_naam].iloc[0]["id"])
                sla_uren_op({
                    "klant_id": klant_id,
                    "opdracht_id": opdracht_id,
                    "activiteit_id": act_id,
                    "datum": datum.strftime("%Y-%m-%d"),
                    "aantal_eenheden": eenheden,
                    "eenheidstarief": tarief,
                })
                st.success(f"Opgeslagen: {eenheden:.1f} {mv} voor {klant_naam}")
                st.rerun()

    # Overzicht
    st.markdown("<hr style='margin:1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### Overzicht")
    df_uren = laad_uren()

    if df_uren.empty:
        st.info("Nog geen uren geregistreerd.")
    else:
        df_k = laad_klanten()[["id", "bedrijfsnaam"]].rename(columns={"id": "klant_id", "bedrijfsnaam": "klant_naam"})
        df_a = (
            laad_activiteiten()[["id", "omschrijving", "eenheid"]]
            .rename(columns={"id": "activiteit_id", "omschrijving": "activiteit_naam"})
        )
        df_o = (
            laad_opdrachten()[["id", "projectcode"]]
            .rename(columns={"id": "opdracht_id"})
        )

        for col in ["klant_id", "activiteit_id", "opdracht_id"]:
            if col in df_uren.columns:
                df_uren[col] = df_uren[col].astype(str)
        df_k["klant_id"] = df_k["klant_id"].astype(str)
        df_a["activiteit_id"] = df_a["activiteit_id"].astype(str)
        df_o["opdracht_id"] = df_o["opdracht_id"].astype(str)

        df_view = (
            df_uren
            .merge(df_k, on="klant_id", how="left")
            .merge(df_a, on="activiteit_id", how="left")
            .merge(df_o, on="opdracht_id", how="left")
        )
        df_view["aantal_eenheden"] = pd.to_numeric(df_view["aantal_eenheden"], errors="coerce")
        df_view["eenheidstarief"] = pd.to_numeric(df_view["eenheidstarief"], errors="coerce")
        df_view["totaal"] = df_view["aantal_eenheden"] * df_view["eenheidstarief"]

        for klant, kdf in df_view.groupby("klant_naam"):
            st.markdown(f"<div class='uren-sectie-label'>{klant}</div>", unsafe_allow_html=True)
            for _, row in kdf.iterrows():
                rij_id = row["id"]
                datum_str = pd.to_datetime(row["datum"]).strftime("%d %b %Y")
                opr_str = f" &nbsp;·&nbsp; {row['projectcode']}" if pd.notna(row.get("projectcode")) else ""
                eh = row["eenheid"] if pd.notna(row.get("eenheid")) else "eenheid"
                mv_row = EENHEID_MEERVOUD.get(eh, eh + "en")

                kaart_col, btn_col = st.columns([12, 1])
                with kaart_col:
                    st.markdown(
                        f"""<div class='uren-kaart'>
                            <div class='uren-kaart-title'>
                                {datum_str}{opr_str}
                                <span class='uren-badge'>€ {row['totaal']:.2f}</span>
                            </div>
                            <div class='uren-kaart-sub'>{row['activiteit_naam']}</div>
                            <div class='uren-kaart-meta'>{row['aantal_eenheden']:.1f} {mv_row} &nbsp;·&nbsp; € {row['eenheidstarief']:.2f}/{eh}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with btn_col:
                    st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_uur_{rij_id}", help="Verwijderen"):
                        verwijder_uur(str(rij_id))
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            tot_eenheden = kdf["aantal_eenheden"].sum()
            tot_bedrag = kdf["totaal"].sum()
            st.markdown(
                f"<div class='totaal-rij'>Totaal {klant}: "
                f"<strong>{tot_eenheden:.1f} eenheden</strong> &nbsp;|&nbsp; "
                f"<strong>€ {tot_bedrag:.2f}</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA: Klanten
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Klanten":
    st.title("Klanten")

    with st.expander("➕ Nieuwe klant toevoegen"):
        with st.form("klant_formulier", clear_on_submit=True):
            naam = st.text_input("Bedrijfsnaam *")
            col1, col2 = st.columns(2)
            with col1:
                straat = st.text_input("Straat")
                plaats = st.text_input("Plaats")
            with col2:
                postcode = st.text_input("Postcode")
                land = st.selectbox("Land", LANDEN, index=LANDEN.index(STANDAARD_LAND))
            opslaan = st.form_submit_button("Klant toevoegen", type="primary")

        if opslaan:
            if not naam.strip():
                st.error("Bedrijfsnaam is verplicht.")
            else:
                voeg_klant_toe({
                    "bedrijfsnaam": naam.strip(),
                    "straat": straat.strip(),
                    "postcode": postcode.strip(),
                    "plaats": plaats.strip(),
                    "land": land,
                })
                st.success(f"Klant '{naam.strip()}' toegevoegd.")
                st.rerun()

    df = laad_klanten()
    if df.empty:
        st.info("Nog geen klanten.")
    else:
        for _, row in df.iterrows():
            col_info, col_del = st.columns([12, 1])
            with col_info:
                adres_delen = [
                    row.get("straat", ""),
                    " ".join(filter(None, [row.get("postcode", ""), row.get("plaats", "")])),
                    row.get("land", ""),
                ]
                adres_str = " &nbsp;·&nbsp; ".join(d for d in adres_delen if d)
                st.markdown(
                    f"<div class='uren-kaart'>"
                    f"<div class='uren-kaart-title'>{row['bedrijfsnaam']}</div>"
                    f"<div class='uren-kaart-meta'>{adres_str}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with col_del:
                st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_klant_{row['id']}", help="Verwijderen"):
                    verwijder_klant(row["id"])
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA: Contactpersonen
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Contactpersonen":
    st.title("Contactpersonen")

    df_klanten = laad_klanten()
    if df_klanten.empty:
        st.warning("Voeg eerst een klant toe via 'Klanten'.")
    else:
        klant_namen = df_klanten["bedrijfsnaam"].tolist()

        with st.expander("➕ Nieuwe contactpersoon toevoegen"):
            with st.form("contact_formulier", clear_on_submit=True):
                klant_keuze = st.selectbox("Klant *", klant_namen)
                col1, col2 = st.columns(2)
                with col1:
                    voornaam = st.text_input("Voornaam *")
                    achternaam = st.text_input("Achternaam")
                with col2:
                    email = st.text_input("E-mailadres")
                    telefoonnummer = st.text_input("Telefoonnummer")
                opslaan = st.form_submit_button("Contactpersoon toevoegen", type="primary")

            if opslaan:
                if not voornaam.strip():
                    st.error("Voornaam is verplicht.")
                else:
                    klant_id = str(df_klanten[df_klanten["bedrijfsnaam"] == klant_keuze].iloc[0]["id"])
                    voeg_contactpersoon_toe({
                        "klant_id": klant_id,
                        "voornaam": voornaam.strip(),
                        "achternaam": achternaam.strip(),
                        "email": email.strip(),
                        "telefoonnummer": telefoonnummer.strip(),
                    })
                    st.success(f"Contactpersoon '{voornaam.strip()}' toegevoegd.")
                    st.rerun()

        df_cp = laad_contactpersonen()
        if df_cp.empty:
            st.info("Nog geen contactpersonen.")
        else:
            df_cp["klant_id"] = df_cp["klant_id"].astype(str)
            df_klanten["id"] = df_klanten["id"].astype(str)
            df_cp = df_cp.merge(
                df_klanten[["id", "bedrijfsnaam"]].rename(columns={"id": "klant_id", "bedrijfsnaam": "klant_naam"}),
                on="klant_id",
                how="left",
            )

            for klant, kdf in df_cp.groupby("klant_naam"):
                st.markdown(f"<div class='uren-sectie-label'>{klant}</div>", unsafe_allow_html=True)
                for _, row in kdf.iterrows():
                    col_info, col_del = st.columns([12, 1])
                    with col_info:
                        volledige_naam = " ".join(filter(None, [row.get("voornaam", ""), row.get("achternaam", "")]))
                        details = " &nbsp;·&nbsp; ".join(
                            filter(None, [row.get("email", ""), row.get("telefoonnummer", "")])
                        )
                        st.markdown(
                            f"<div class='uren-kaart'>"
                            f"<div class='uren-kaart-title'>{volledige_naam}</div>"
                            f"<div class='uren-kaart-meta'>{details}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    with col_del:
                        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_cp_{row['id']}", help="Verwijderen"):
                            verwijder_contactpersoon(row["id"])
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA: Activiteiten
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Activiteiten":
    st.title("Activiteiten")

    with st.expander("➕ Nieuwe activiteit toevoegen"):
        with st.form("activiteit_formulier", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                omschrijving = st.text_input("Omschrijving *")
                eenheid = st.selectbox("Eenheid", EENHEDEN)
            with col2:
                standaard_tarief = st.number_input("Standaard tarief (€)", min_value=0.0, step=1.0, format="%.2f")
            opslaan = st.form_submit_button("Activiteit toevoegen", type="primary")

        if opslaan:
            if not omschrijving.strip():
                st.error("Omschrijving is verplicht.")
            else:
                voeg_activiteit_toe({
                    "omschrijving": omschrijving.strip(),
                    "eenheid": eenheid,
                    "standaard_tarief": standaard_tarief,
                })
                st.success(f"Activiteit '{omschrijving.strip()}' toegevoegd.")
                st.rerun()

    df = laad_activiteiten()
    if df.empty:
        st.info("Nog geen activiteiten.")
    else:
        for _, row in df.iterrows():
            col_info, col_del = st.columns([12, 1])
            with col_info:
                eh = row.get("eenheid", "eenheid")
                st.markdown(
                    f"<div class='uren-kaart'>"
                    f"<div class='uren-kaart-title'>{row['omschrijving']}"
                    f"<span class='uren-badge'>€ {float(row['standaard_tarief']):.2f}/{eh}</span></div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with col_del:
                st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_act_{row['id']}", help="Verwijderen"):
                    verwijder_activiteit(row["id"])
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA: Opdrachten
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Opdrachten":
    st.title("Opdrachten")

    df_klanten = laad_klanten()
    if df_klanten.empty:
        st.warning("Voeg eerst een klant toe via 'Klanten'.")
    else:
        klant_namen = df_klanten["bedrijfsnaam"].tolist()

        with st.expander("➕ Nieuwe opdracht toevoegen"):
            with st.form("opdracht_formulier", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    klant_keuze = st.selectbox("Klant *", klant_namen)
                    projectcode = st.text_input("Projectcode *")
                    startdatum = st.date_input("Startdatum", value=date.today())
                with col2:
                    omschrijving = st.text_input("Omschrijving *")
                    status = st.selectbox("Status", OPDRACHT_STATUSSEN)
                    einddatum = st.date_input("Einddatum (optioneel)", value=None)
                opslaan = st.form_submit_button("Opdracht toevoegen", type="primary")

            if opslaan:
                if not projectcode.strip() or not omschrijving.strip():
                    st.error("Projectcode en omschrijving zijn verplicht.")
                else:
                    klant_id = str(df_klanten[df_klanten["bedrijfsnaam"] == klant_keuze].iloc[0]["id"])
                    voeg_opdracht_toe({
                        "klant_id": klant_id,
                        "projectcode": projectcode.strip(),
                        "omschrijving": omschrijving.strip(),
                        "startdatum": startdatum.strftime("%Y-%m-%d"),
                        "einddatum": einddatum.strftime("%Y-%m-%d") if einddatum else None,
                        "status": status,
                    })
                    st.success(f"Opdracht '{projectcode.strip()}' toegevoegd.")
                    st.rerun()

        df = laad_opdrachten()
        if df.empty:
            st.info("Nog geen opdrachten.")
        else:
            df["klant_id"] = df["klant_id"].astype(str)
            df_klanten["id"] = df_klanten["id"].astype(str)
            df = df.merge(
                df_klanten[["id", "bedrijfsnaam"]].rename(columns={"id": "klant_id", "bedrijfsnaam": "klant_naam"}),
                on="klant_id",
                how="left",
            )

            STATUS_BADGE = {
                "Actief": "badge-groen",
                "Aangevraagd": "uren-badge",
                "Gepauzeerd": "badge-grijs",
                "Afgerond": "badge-grijs",
            }

            for klant, kdf in df.groupby("klant_naam"):
                st.markdown(f"<div class='uren-sectie-label'>{klant}</div>", unsafe_allow_html=True)
                for _, row in kdf.iterrows():
                    col_info, col_del = st.columns([12, 1])
                    with col_info:
                        datum_str = ""
                        if pd.notna(row.get("startdatum")) and row["startdatum"]:
                            datum_str = str(row["startdatum"])
                        if pd.notna(row.get("einddatum")) and row["einddatum"]:
                            datum_str += f" → {row['einddatum']}"
                        badge_cls = STATUS_BADGE.get(row.get("status", ""), "badge-grijs")
                        st.markdown(
                            f"<div class='uren-kaart'>"
                            f"<div class='uren-kaart-title'>"
                            f"{row['projectcode']} &nbsp;·&nbsp; {row['omschrijving']}"
                            f"<span class='{badge_cls}'>{row.get('status', '')}</span></div>"
                            f"<div class='uren-kaart-meta'>{datum_str}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    with col_del:
                        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_opr_{row['id']}", help="Verwijderen"):
                            verwijder_opdracht(row["id"])
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)
