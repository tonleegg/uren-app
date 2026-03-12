import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pycountry
from datetime import date, datetime
from supabase import create_client

KOLOMMEN = ["klant", "project", "datum", "uren", "tarief", "land"]
LANDEN = sorted([c.name for c in pycountry.countries])
STANDAARD_LAND = "Netherlands"

CSS = """
<style>
/* ── Achtergrond & basiskleur ── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #ffffff !important;
}
[data-testid="stHeader"] { background-color: #ffffff !important; box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important; }
section[data-testid="stSidebar"] { background-color: #f4f6f7 !important; border-right: 1px solid #d5d8dc !important; }

/* ── Titels ── */
h1 { color: #1a5276 !important; font-size: 1.6rem !important; font-weight: 700 !important; }
h2 { color: #1a5276 !important; font-weight: 600 !important; }
h3 { color: #1a5276 !important; font-size: 0.85rem !important;
     font-weight: 700 !important; letter-spacing: 0.04em !important;
     text-transform: uppercase !important; margin-bottom: 2px !important; }
p, label, .stMarkdown p { color: #2c3e50 !important; }

/* ── Formuliercontainer ── */
[data-testid="stForm"] {
    background-color: #f8f9fa !important;
    border: 1px solid #d5d8dc !important;
    border-top: 3px solid #1a5276 !important;
    border-radius: 8px !important;
    padding: 1.2rem 1.4rem !important;
}

/* ── Invoervelden ── */
.stTextInput input, .stNumberInput input, .stDateInput input {
    background-color: #ffffff !important;
    color: #2c3e50 !important;
    border: 1px solid #aab7b8 !important;
    border-radius: 6px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
    border-color: #1a5276 !important;
    box-shadow: 0 0 0 2px rgba(26,82,118,0.12) !important;
}
.stTextInput label, .stNumberInput label, .stDateInput label,
.stSelectbox label { color: #7f8c8d !important; font-size: 0.82rem !important; font-weight: 600 !important; }

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border-color: #aab7b8 !important;
    border-radius: 6px !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div { color: #2c3e50 !important; }
[data-baseweb="popover"] { background-color: #ffffff !important; border-color: #aab7b8 !important; box-shadow: 0 4px 12px rgba(0,0,0,0.10) !important; }
[data-baseweb="menu"] { background-color: #ffffff !important; }
[role="option"] { background-color: #ffffff !important; color: #2c3e50 !important; }
[role="option"]:hover { background-color: #eaf0fb !important; color: #1a5276 !important; }

/* ── Sidebar tekst & knoppen ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p { color: #2c3e50 !important; }

/* ── Knoppen (icoon-knoppen in overzicht) ── */
.stButton > button {
    background-color: #ffffff !important;
    color: #7f8c8d !important;
    border: 1px solid #d5d8dc !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    padding: 4px 10px !important;
    transition: border-color 0.15s, background-color 0.15s, color 0.15s !important;
}
.stButton > button:hover {
    background-color: #eaf0fb !important;
    border-color: #1a5276 !important;
    color: #1a5276 !important;
}

/* ── Formulierknoppen ── */
.stFormSubmitButton > button {
    background-color: #1a5276 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 8px !important;
    transition: background-color 0.15s !important;
}
.stFormSubmitButton > button:hover { background-color: #154360 !important; }

/* ── Berichten ── */
[data-testid="stAlert"] { border-radius: 6px !important; }

/* ── Scheidingslijn ── */
hr { border-color: #d5d8dc !important; opacity: 1 !important; margin: 6px 0 !important; }

/* ── Uren-kaart (overzicht) ── */
.uren-sectie-label {
    color: #1a5276;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding-bottom: 6px;
    border-bottom: 2px solid #1a5276;
    margin-bottom: 0;
}
.uren-kaart {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 6px;
    border-left: 3px solid #1a5276;
    border: 1px solid #d5d8dc;
    border-left: 3px solid #1a5276;
}
.uren-kaart-title {
    font-weight: 700;
    font-size: 1rem;
    color: #1a5276;
    margin-bottom: 2px;
}
.uren-kaart-sub {
    color: #2c3e50;
    font-size: 0.85rem;
    margin-bottom: 4px;
}
.uren-kaart-meta {
    color: #7f8c8d;
    font-size: 0.82rem;
}
.uren-badge {
    display: inline-block;
    background-color: #1a5276;
    color: #ffffff;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.82rem;
    font-weight: 600;
    float: right;
    margin-top: -2px;
}
.subtotaal-rij {
    text-align: right;
    color: #7f8c8d;
    font-size: 0.82rem;
    padding: 4px 0 8px 0;
}
.totaal-rij {
    text-align: right;
    color: #1a5276;
    font-size: 0.9rem;
    font-weight: 700;
    border-top: 1px solid #d5d8dc;
    padding-top: 6px;
    margin-top: 4px;
}

/* ── Logo-container ── */
[data-testid="stImage"] {
    overflow: visible !important;
    max-width: none !important;
    padding-right: 1rem !important;
}
[data-testid="stImage"] img {
    max-width: none !important;
    overflow: visible !important;
}

/* ── Focus-trap (vangt Tab op na laatste invoerveld) ── */
.focus-trap {
    position: absolute;
    width: 1px;
    height: 1px;
    margin: -1px;
    padding: 0;
    border: 0;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
}
</style>
"""

FOCUS_TRAP = '<div class="focus-trap"><input type="text" tabindex="0" aria-hidden="true"></div>'

TAB_NAAR_OPSLAAN_JS = """
<script>
(function () {
    function setup() {
        var doc = window.parent.document;
        var numInputs = doc.querySelectorAll('[data-testid="stNumberInput"] input');
        if (!numInputs.length) { setTimeout(setup, 200); return; }
        var tariefInput = numInputs[numInputs.length - 1];
        tariefInput.addEventListener('keydown', function (e) {
            if (e.key === 'Tab' && !e.shiftKey) {
                var submitBtn = doc.querySelector('[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]');
                if (!submitBtn) submitBtn = doc.querySelector('[data-testid="stFormSubmitButton"] button');
                if (submitBtn) { e.preventDefault(); submitBtn.focus(); }
            }
        });
    }
    setup();
})();
</script>
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

LOGO_PAD = "daauw kl.png"

if not st.session_state.get("ingelogd"):
    try:
        st.image(LOGO_PAD, width=240, use_container_width=False)
    except Exception:
        pass
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
    try:
        st.image(LOGO_PAD, width=240, use_container_width=False)
    except Exception:
        pass
    st.markdown(f"Ingelogd als **{st.session_state['gebruiker_naam']}**")
    if st.button("Uitloggen"):
        get_client().auth.sign_out()
        st.session_state["ingelogd"] = False
        st.session_state["gebruiker_naam"] = None
        st.session_state["gebruiker_email"] = None
        st.rerun()

try:
    st.image(LOGO_PAD, width=240, use_container_width=False)
except Exception:
    pass
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

    with st.form("bewerk_formulier", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            klant_idx = klant_opties_edit.index(rij["klant"]) if rij["klant"] in klant_opties_edit else 0
            klant_keuze_edit = st.selectbox("Klant", klant_opties_edit, index=klant_idx, key=f"klant_sb_edit_{bewerkregel}")
            klant_nieuw_edit = st.text_input("Nieuwe klantnaam", key=f"klant_input_edit_{bewerkregel}", placeholder="Alleen invullen bij 'Nieuwe klant toevoegen'")
        with col2:
            project_idx = project_opties_edit.index(rij["project"]) if rij["project"] in project_opties_edit else 0
            project_keuze_edit = st.selectbox("Project", project_opties_edit, index=project_idx, key=f"project_sb_edit_{bewerkregel}")
            project_nieuw_edit = st.text_input("Nieuw project", key=f"project_input_edit_{bewerkregel}", placeholder="Alleen invullen bij 'Nieuw project toevoegen'")
        datum_edit = st.date_input("Datum", value=pd.to_datetime(rij["datum"]).date())
        uren_edit = st.number_input("Uren", min_value=0.0, value=float(rij["uren"]), step=0.5, format="%.1f")
        tarief_edit = st.number_input("Uurtarief (€)", min_value=0.0, value=float(rij["tarief"]), step=1.0, format="%.2f")
        huidig_land = rij["land"] if "land" in rij and rij["land"] in LANDEN else STANDAARD_LAND
        land_edit = st.selectbox("Land", LANDEN, index=LANDEN.index(huidig_land), key=f"land_edit_{bewerkregel}")
        st.markdown(FOCUS_TRAP, unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        opslaan_edit = btn_col1.form_submit_button("Opslaan wijzigingen", type="primary", use_container_width=True)
        annuleer = btn_col2.form_submit_button("Annuleren", use_container_width=True)

    if annuleer:
        st.session_state.bewerkregel = None
        st.rerun()

    if opslaan_edit:
        klant_edit = (klant_nieuw_edit if klant_keuze_edit == NIEUW_KLANT else klant_keuze_edit).strip()
        omschrijving_edit = (project_nieuw_edit if project_keuze_edit == NIEUW_PROJECT else project_keuze_edit).strip()
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
                "tarief": tarief_edit,
                "land": land_edit,
            })
            st.session_state.bewerkregel = None
            st.success("Wijzigingen opgeslagen.")
            st.rerun()

    components.html(TAB_NAAR_OPSLAAN_JS, height=0)

else:
    st.markdown("### Nieuwe regel invoeren")
    suggesties = laad_suggesties()
    klant_opties = [NIEUW_KLANT] + suggesties["klanten"]
    project_opties = [NIEUW_PROJECT] + suggesties["projecten"]

    with st.form("uren_formulier", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            klant_keuze = st.selectbox("Klant", klant_opties, key=f"klant_sb_nieuw_{save_cnt}")
            klant_nieuw = st.text_input("Nieuwe klantnaam", key=f"klant_input_nieuw_{save_cnt}", placeholder="Alleen invullen bij 'Nieuwe klant toevoegen'")
        with col2:
            project_keuze = st.selectbox("Project", project_opties, key=f"project_sb_nieuw_{save_cnt}")
            project_nieuw = st.text_input("Nieuw project", key=f"project_input_nieuw_{save_cnt}", placeholder="Alleen invullen bij 'Nieuw project toevoegen'")
        datum = st.date_input("Datum", value=date.today())
        uren = st.number_input("Uren", min_value=0.0, step=0.5, format="%.1f")
        tarief = st.number_input("Uurtarief (€)", min_value=0.0, step=1.0, format="%.2f")
        land = st.selectbox("Land", LANDEN, index=LANDEN.index(STANDAARD_LAND), key=f"land_nieuw_{save_cnt}")
        st.markdown(FOCUS_TRAP, unsafe_allow_html=True)
        opslaan = st.form_submit_button("Opslaan", type="primary", use_container_width=True)

    if opslaan:
        klant = (klant_nieuw if klant_keuze == NIEUW_KLANT else klant_keuze).strip()
        omschrijving = (project_nieuw if project_keuze == NIEUW_PROJECT else project_keuze).strip()
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
                "tarief": tarief,
                "land": land,
            })
            st.session_state["save_cnt"] = save_cnt + 1
            st.success(f"Opgeslagen: {uren}u voor {klant}")
            st.rerun()

    components.html(TAB_NAAR_OPSLAAN_JS, height=0)

# ── Overzicht ──────────────────────────────────────────────────────────────────
st.markdown("<hr style='margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
st.markdown("### Overzicht")
df = laad_data()

if df.empty:
    st.info("Nog geen uren geregistreerd.")
else:
    df["uren"] = pd.to_numeric(df["uren"])
    df["tarief"] = pd.to_numeric(df["tarief"])
    df["totaalbedrag"] = df["uren"] * df["tarief"]

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
                            <div class='uren-kaart-meta'>{row['uren']:.1f} uur &nbsp;·&nbsp; € {row['tarief']:.2f}/uur</div>
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
