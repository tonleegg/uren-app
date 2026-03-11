import streamlit as st
import pandas as pd
from datetime import date, datetime
from supabase import create_client
KOLOMMEN = ["klant", "project", "datum", "uren", "uurtarief"]

CSS = """
<style>
/* ── Achtergrond & basiskleur ── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0c1929 !important;
}
[data-testid="stHeader"] { background-color: #0c1929 !important; box-shadow: none !important; }
section[data-testid="stSidebar"] { background-color: #0a1520 !important; }

/* ── Titels ── */
h1 { color: #ffffff !important; font-size: 1.6rem !important; font-weight: 700 !important; }
h2 { color: #ffffff !important; font-weight: 600 !important; }
h3 { color: #4fc3f7 !important; font-size: 0.85rem !important;
     font-weight: 600 !important; letter-spacing: 0.04em !important;
     text-transform: uppercase !important; margin-bottom: 2px !important; }
p, label, .stMarkdown p { color: #c8d8e8 !important; }

/* ── Formuliercontainer ── */
[data-testid="stForm"] {
    background-color: #132035 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem !important;
}

/* ── Invoervelden ── */
.stTextInput input, .stNumberInput input, .stDateInput input {
    background-color: #1a2f4a !important;
    color: #e8f0f8 !important;
    border: 1px solid #2a4a6a !important;
    border-radius: 8px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
    border-color: #4fc3f7 !important;
    box-shadow: 0 0 0 2px rgba(79,195,247,0.15) !important;
}
.stTextInput label, .stNumberInput label, .stDateInput label,
.stSelectbox label { color: #7a9bbf !important; font-size: 0.82rem !important; }

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #1a2f4a !important;
    border-color: #2a4a6a !important;
    border-radius: 8px !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div { color: #e8f0f8 !important; }
[data-baseweb="popover"] { background-color: #1a2f4a !important; border-color: #2a4a6a !important; }
[data-baseweb="menu"] { background-color: #1a2f4a !important; }
[role="option"] { background-color: #1a2f4a !important; color: #e8f0f8 !important; }
[role="option"]:hover { background-color: #1e3a5f !important; }

/* ── Knoppen ── */
.stButton > button {
    background-color: #1a2f4a !important;
    color: #c8d8e8 !important;
    border: 1px solid #2a4a6a !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    padding: 4px 10px !important;
    transition: border-color 0.15s, background-color 0.15s !important;
}
.stButton > button:hover {
    background-color: #1e3a5f !important;
    border-color: #4fc3f7 !important;
    color: #ffffff !important;
}

/* ── Formulierknoppen ── */
.stFormSubmitButton > button {
    background-color: #1565c0 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 8px !important;
}
.stFormSubmitButton > button:hover { background-color: #1976d2 !important; }

/* ── Berichten ── */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* ── Scheidingslijn ── */
hr { border-color: #1e3a5f !important; opacity: 1 !important; margin: 6px 0 !important; }

/* ── Uren-kaart (overzicht) ── */
.uren-sectie-label {
    color: #4fc3f7;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e3a5f;
    margin-bottom: 0;
}
.uren-kaart {
    background-color: #132035;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 6px;
    border-left: 3px solid #1e3a5f;
}
.uren-kaart-title {
    font-weight: 700;
    font-size: 1rem;
    color: #ffffff;
    margin-bottom: 2px;
}
.uren-kaart-sub {
    color: #7a9bbf;
    font-size: 0.85rem;
    margin-bottom: 4px;
}
.uren-kaart-meta {
    color: #7a9bbf;
    font-size: 0.82rem;
}
.uren-badge {
    display: inline-block;
    background-color: #1a2f4a;
    color: #c8d8e8;
    border: 1px solid #2a4a6a;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.82rem;
    font-weight: 600;
    float: right;
    margin-top: -2px;
}
.subtotaal-rij {
    text-align: right;
    color: #7a9bbf;
    font-size: 0.82rem;
    padding: 4px 0 8px 0;
}
.totaal-rij {
    text-align: right;
    color: #c8d8e8;
    font-size: 0.9rem;
    font-weight: 600;
    border-top: 1px solid #1e3a5f;
    padding-top: 6px;
    margin-top: 4px;
}
</style>
"""


@st.cache_resource
def get_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=60)
def laad_data() -> pd.DataFrame:
    res = get_client().table("uren").select("*").order("datum").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id"] + KOLOMMEN + ["timestamp"])


def laad_suggesties() -> dict:
    df = laad_data()
    if df.empty:
        return {"klanten": [], "projecten": []}
    return {
        "klanten": sorted(df["klant"].dropna().unique().tolist()),
        "projecten": sorted(df["project"].dropna().unique().tolist()),
    }


def sla_op(rij: dict) -> None:
    rij["timestamp"] = datetime.now().isoformat()
    get_client().table("uren").insert(rij).execute()
    laad_data.clear()


def bewerk_rij(rij_id: int, rij: dict) -> None:
    get_client().table("uren").update(rij).eq("id", rij_id).execute()
    laad_data.clear()


def verwijder_rij(rij_id: int) -> None:
    get_client().table("uren").delete().eq("id", rij_id).execute()
    laad_data.clear()


def login(email: str, wachtwoord: str):
    try:
        res = get_client().auth.sign_in_with_password({"email": email, "password": wachtwoord})
        return res.user
    except Exception:
        return None


NIEUW_KLANT = "--- Nieuwe klant toevoegen ---"
NIEUW_PROJECT = "--- Nieuw project toevoegen ---"


# ── Pagina-config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Urenregistratie", page_icon="⏱️", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

if not st.session_state.get("ingelogd"):
    st.title("Urenregistratie")
    with st.form("login_formulier"):
        email_input = st.text_input("E-mailadres")
        wachtwoord_input = st.text_input("Wachtwoord", type="password")
        inloggen = st.form_submit_button("Inloggen", type="primary")
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

with st.sidebar:
    st.markdown(f"Ingelogd als **{st.session_state['gebruiker_naam']}**")
    if st.button("Uitloggen"):
        get_client().auth.sign_out()
        st.session_state["ingelogd"] = False
        st.session_state["gebruiker_naam"] = None
        st.session_state["gebruiker_email"] = None
        st.rerun()

st.title("Urenregistratie")

bewerkregel = st.session_state.get("bewerkregel")
save_cnt = st.session_state.get("save_cnt", 0)

# ── Formulier: nieuw of bewerken ───────────────────────────────────────────────
if bewerkregel is not None:
    df_all = laad_data()
    rij_match = df_all[df_all["id"] == bewerkregel]
    if rij_match.empty:
        st.session_state.bewerkregel = None
        st.rerun()
    rij = rij_match.iloc[0]

    st.markdown("### Regel bewerken")
    suggesties_edit = laad_suggesties()
    klant_opties_edit = [NIEUW_KLANT] + suggesties_edit["klanten"]
    project_opties_edit = [NIEUW_PROJECT] + suggesties_edit["projecten"]

    col1, col2 = st.columns(2)
    with col1:
        klant_idx = klant_opties_edit.index(rij["klant"]) if rij["klant"] in klant_opties_edit else 0
        klant_keuze_edit = st.selectbox("Klant", klant_opties_edit, index=klant_idx, key=f"klant_sb_edit_{bewerkregel}")
        if klant_keuze_edit == NIEUW_KLANT:
            klant_waarde_edit = st.text_input("Nieuwe klantnaam", key=f"klant_input_edit_{bewerkregel}")
        else:
            klant_waarde_edit = klant_keuze_edit
    with col2:
        project_idx = project_opties_edit.index(rij["project"]) if rij["project"] in project_opties_edit else 0
        project_keuze_edit = st.selectbox("Projectomschrijving", project_opties_edit, index=project_idx, key=f"project_sb_edit_{bewerkregel}")
        if project_keuze_edit == NIEUW_PROJECT:
            project_waarde_edit = st.text_input("Nieuw project", key=f"project_input_edit_{bewerkregel}")
        else:
            project_waarde_edit = project_keuze_edit

    with st.form("bewerk_formulier", clear_on_submit=False):
        datum_edit = st.date_input("Datum", value=pd.to_datetime(rij["datum"]).date())
        uren_edit = st.number_input("Uren", min_value=0.0, value=float(rij["uren"]), step=0.5, format="%.1f")
        uurtarief_edit = st.number_input("Uurtarief (€)", min_value=0.0, value=float(rij["uurtarief"]), step=1.0, format="%.2f")
        btn_col1, btn_col2 = st.columns(2)
        opslaan_edit = btn_col1.form_submit_button("Opslaan wijzigingen", use_container_width=True)
        annuleer = btn_col2.form_submit_button("Annuleren", use_container_width=True)

    if annuleer:
        st.session_state.bewerkregel = None
        st.rerun()

    if opslaan_edit:
        klant_edit = (klant_waarde_edit or "").strip()
        omschrijving_edit = (project_waarde_edit or "").strip()
        if not klant_edit:
            st.error("Vul een klantnaam in.")
        elif not omschrijving_edit:
            st.error("Vul een project in.")
        elif uren_edit <= 0:
            st.error("Uren moet groter zijn dan 0.")
        else:
            bewerk_rij(bewerkregel, {
                "klant": klant_edit,
                "project": omschrijving_edit,
                "datum": datum_edit.strftime("%Y-%m-%d"),
                "uren": uren_edit,
                "uurtarief": uurtarief_edit,
            })
            st.session_state.bewerkregel = None
            st.success("Wijzigingen opgeslagen.")
            st.rerun()

else:
    st.markdown("### Nieuwe regel invoeren")
    suggesties = laad_suggesties()
    klant_opties = [NIEUW_KLANT] + suggesties["klanten"]
    project_opties = [NIEUW_PROJECT] + suggesties["projecten"]

    col1, col2 = st.columns(2)
    with col1:
        klant_keuze = st.selectbox("Klant", klant_opties, key=f"klant_sb_nieuw_{save_cnt}")
        if klant_keuze == NIEUW_KLANT:
            klant_waarde = st.text_input("Nieuwe klantnaam", key=f"klant_input_nieuw_{save_cnt}")
        else:
            klant_waarde = klant_keuze
    with col2:
        project_keuze = st.selectbox("Projectomschrijving", project_opties, key=f"project_sb_nieuw_{save_cnt}")
        if project_keuze == NIEUW_PROJECT:
            project_waarde = st.text_input("Nieuw project", key=f"project_input_nieuw_{save_cnt}")
        else:
            project_waarde = project_keuze

    with st.form("uren_formulier", clear_on_submit=True):
        datum = st.date_input("Datum", value=date.today())
        uren = st.number_input("Uren", min_value=0.0, step=0.5, format="%.1f")
        uurtarief = st.number_input("Uurtarief (€)", min_value=0.0, step=1.0, format="%.2f")
        opslaan = st.form_submit_button("Opslaan")

    if opslaan:
        klant = (klant_waarde or "").strip()
        omschrijving = (project_waarde or "").strip()
        if not klant:
            st.error("Vul een klantnaam in of kies er een uit de lijst.")
        elif not omschrijving:
            st.error("Vul een project in of kies er een uit de lijst.")
        elif uren <= 0:
            st.error("Uren moet groter zijn dan 0.")
        else:
            sla_op({
                "klant": klant,
                "project": omschrijving,
                "datum": datum.strftime("%Y-%m-%d"),
                "uren": uren,
                "uurtarief": uurtarief,
            })
            st.session_state["save_cnt"] = save_cnt + 1
            st.success(f"Opgeslagen: {uren}u voor {klant}")
            st.rerun()

# ── Overzicht ──────────────────────────────────────────────────────────────────
st.markdown("<hr style='margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
st.markdown("### Overzicht")
df = laad_data()

if df.empty:
    st.info("Nog geen uren geregistreerd.")
else:
    df["uren"] = pd.to_numeric(df["uren"])
    df["uurtarief"] = pd.to_numeric(df["uurtarief"])
    df["totaalbedrag"] = df["uren"] * df["uurtarief"]

    for klant, klant_df in df.groupby("klant"):
        klant_uren_totaal = klant_df["uren"].sum()
        klant_bedrag_totaal = klant_df["totaalbedrag"].sum()

        st.markdown(f"<div class='uren-sectie-label'>{klant}</div>", unsafe_allow_html=True)

        for project, proj_df in klant_df.groupby("project"):
            proj_uren = proj_df["uren"].sum()
            proj_bedrag = proj_df["totaalbedrag"].sum()

            for _, row in proj_df.iterrows():
                rij_id = row["id"]
                datum_str = pd.to_datetime(row["datum"]).strftime("%d %B %Y").lstrip("0")
                bedrag = row["totaalbedrag"]

                kaart_col, btn_col = st.columns([11, 2])
                with kaart_col:
                    st.markdown(
                        f"""<div class='uren-kaart'>
                            <div class='uren-kaart-title'>
                                {datum_str}
                                <span class='uren-badge'>€ {bedrag:.2f}</span>
                            </div>
                            <div class='uren-kaart-sub'>{project}</div>
                            <div class='uren-kaart-meta'>{row['uren']:.1f} uur &nbsp;·&nbsp; € {row['uurtarief']:.2f}/uur</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with btn_col:
                    st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                    if st.button("✏️", key=f"edit_{rij_id}", help="Bewerken", use_container_width=True):
                        st.session_state.bewerkregel = rij_id
                        st.rerun()
                    if st.button("🗑️", key=f"del_{rij_id}", help="Verwijderen", use_container_width=True):
                        verwijder_rij(rij_id)
                        if st.session_state.get("bewerkregel") == rij_id:
                            st.session_state.bewerkregel = None
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='subtotaal-rij'>Subtotaal <em>{project}</em>: "
                f"<strong>{proj_uren:.1f} uur</strong> &nbsp;|&nbsp; "
                f"<strong>€ {proj_bedrag:.2f}</strong></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<div class='totaal-rij'>Totaal {klant}: "
            f"<strong>{klant_uren_totaal:.1f} uur</strong> &nbsp;|&nbsp; "
            f"<strong>€ {klant_bedrag_totaal:.2f}</strong></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom: 1.5rem'></div>", unsafe_allow_html=True)
