import json
import os
import streamlit as st
import pandas as pd
from datetime import date
from streamlit_searchbox import st_searchbox

CSV_PAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uren.csv")
SUGGESTIES_PAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suggesties.json")
KOLOMMEN = ["klant", "projectomschrijving", "datum", "uren", "uurtarief"]

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


def laad_data() -> pd.DataFrame:
    if os.path.exists(CSV_PAD):
        return pd.read_csv(CSV_PAD)
    return pd.DataFrame(columns=KOLOMMEN)


def laad_suggesties() -> dict:
    if os.path.exists(SUGGESTIES_PAD):
        with open(SUGGESTIES_PAD, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"klanten": [], "projecten": []}


def sla_suggesties_op(klant: str, project: str) -> None:
    suggesties = laad_suggesties()
    if klant and klant not in suggesties["klanten"]:
        suggesties["klanten"].append(klant)
        suggesties["klanten"].sort()
    if project and project not in suggesties["projecten"]:
        suggesties["projecten"].append(project)
        suggesties["projecten"].sort()
    with open(SUGGESTIES_PAD, "w", encoding="utf-8") as f:
        json.dump(suggesties, f, ensure_ascii=False, indent=2)


def sla_op(rij: dict) -> None:
    df = laad_data()
    df = pd.concat([df, pd.DataFrame([rij])], ignore_index=True)
    df.to_csv(CSV_PAD, index=False)


def verwijder_rij(idx: int) -> None:
    df = laad_data()
    df = df.drop(index=idx).reset_index(drop=True)
    df.to_csv(CSV_PAD, index=False)


def zoek_klanten(term: str) -> list:
    klanten = laad_suggesties()["klanten"]
    if not term:
        return klanten
    return [k for k in klanten if term.lower() in k.lower()]


def zoek_projecten(term: str) -> list:
    projecten = laad_suggesties()["projecten"]
    if not term:
        return projecten
    return [p for p in projecten if term.lower() in p.lower()]


# ── Pagina-config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Urenregistratie", page_icon="⏱️", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)
st.title("Urenregistratie")

suggesties = laad_suggesties()
bewerkregel = st.session_state.get("bewerkregel")
# Teller om searchboxes te resetten na opslaan (nieuw sleutel → nieuw widget)
save_cnt = st.session_state.get("save_cnt", 0)

# ── Formulier: nieuw of bewerken ───────────────────────────────────────────────
if bewerkregel is not None:
    df_all = laad_data()
    if bewerkregel >= len(df_all):
        st.session_state.bewerkregel = None
        st.rerun()
    rij = df_all.iloc[bewerkregel]

    st.markdown("### Regel bewerken")
    col1, col2 = st.columns(2)
    with col1:
        # Unieke sleutel per rij zodat default correct wordt geladen
        klant_waarde_edit = st_searchbox(
            zoek_klanten,
            key=f"klant_sb_edit_{bewerkregel}",
            placeholder="Zoek of typ een klant...",
            label="Klant",
            default=rij["klant"],
            default_use_searchterm=True,
        )
    with col2:
        project_waarde_edit = st_searchbox(
            zoek_projecten,
            key=f"project_sb_edit_{bewerkregel}",
            placeholder="Zoek of typ een omschrijving...",
            label="Projectomschrijving",
            default=rij["projectomschrijving"],
            default_use_searchterm=True,
        )

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
            st.error("Vul een projectomschrijving in.")
        elif uren_edit <= 0:
            st.error("Uren moet groter zijn dan 0.")
        else:
            df_all.at[bewerkregel, "klant"] = klant_edit
            df_all.at[bewerkregel, "projectomschrijving"] = omschrijving_edit
            df_all.at[bewerkregel, "datum"] = datum_edit.strftime("%Y-%m-%d")
            df_all.at[bewerkregel, "uren"] = uren_edit
            df_all.at[bewerkregel, "uurtarief"] = uurtarief_edit
            df_all.to_csv(CSV_PAD, index=False)
            sla_suggesties_op(klant_edit, omschrijving_edit)
            st.session_state.bewerkregel = None
            st.success("Wijzigingen opgeslagen.")
            st.rerun()

else:
    st.markdown("### Nieuwe regel invoeren")
    col1, col2 = st.columns(2)
    with col1:
        # save_cnt in de sleutel zorgt voor een leeg veld na elke opslag
        klant_waarde = st_searchbox(
            zoek_klanten,
            key=f"klant_sb_nieuw_{save_cnt}",
            placeholder="Zoek of typ een klant...",
            label="Klant",
            default_use_searchterm=True,
        )
    with col2:
        project_waarde = st_searchbox(
            zoek_projecten,
            key=f"project_sb_nieuw_{save_cnt}",
            placeholder="Zoek of typ een omschrijving...",
            label="Projectomschrijving",
            default_use_searchterm=True,
        )

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
            st.error("Vul een projectomschrijving in of kies er een uit de lijst.")
        elif uren <= 0:
            st.error("Uren moet groter zijn dan 0.")
        else:
            sla_op({
                "klant": klant,
                "projectomschrijving": omschrijving,
                "datum": datum.strftime("%Y-%m-%d"),
                "uren": uren,
                "uurtarief": uurtarief,
            })
            sla_suggesties_op(klant, omschrijving)
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

        for project, proj_df in klant_df.groupby("projectomschrijving"):
            proj_uren = proj_df["uren"].sum()
            proj_bedrag = proj_df["totaalbedrag"].sum()

            for idx, row in proj_df.iterrows():
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
                    if st.button("✏️", key=f"edit_{idx}", help="Bewerken", use_container_width=True):
                        st.session_state.bewerkregel = idx
                        st.rerun()
                    if st.button("🗑️", key=f"del_{idx}", help="Verwijderen", use_container_width=True):
                        verwijder_rij(idx)
                        if st.session_state.get("bewerkregel") == idx:
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
