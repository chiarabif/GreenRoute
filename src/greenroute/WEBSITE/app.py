import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="GreenRoute", page_icon="🌱", layout="wide")

# -------------------------
# PATHS
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[2]
LOGO_PATH = BASE_DIR / "greenroute-logo.png"
RESULTS_PATH = PROJECT_ROOT / "data" / "results" / "calculated_green_metrics.csv"

# -------------------------
# PAGE STYLE
# -------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    div.stButton > button {
        width: 380px;
        height: 210px;
        margin: 18px auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        white-space: pre-line;
        font-size: 22px;
        font-weight: 500;
        padding: 1rem;
        line-height: 1.5;
        border-radius: 18px;
        border: 1.5px solid #DCEEDC;
        background-color: #FFFFFF;
        box-shadow: 0 6px 18px rgba(46, 125, 50, 0.08);
        transition: all 0.2s ease;
        color: #2E2E2E;
    }

    div.stButton > button:hover {
        border-color: #2E7D32;
        background-color: #F4FAF4;
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(46, 125, 50, 0.18);
    }

    div.stButton > button:active {
        transform: translateY(0px);
        background-color: #E8F5E9;
    }

    div.stButton > button::first-line {
        font-weight: 700;
        font-size: 26px;
        color: #2E7D32;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-top: -8px;
        margin-bottom: 8px;
    }

    .section-title {
        text-align: center;
        font-weight: 600;
        font-size: 22px;
        margin-top: 0.3rem;
        margin-bottom: 0.7rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# LOAD RESULTS
# -------------------------
@st.cache_data
def load_results(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path)

    if "drug_name" in df.columns:
        df["drug_name"] = df["drug_name"].replace({"Sertralin": "Sertraline"})

    return df


results_df = load_results(RESULTS_PATH)

# -------------------------
# HEADER
# -------------------------
left, center, right = st.columns([2.4, 2, 2.4])
with center:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=400)
    else:
        st.title("GreenRoute 🌱")

st.markdown(
    "<p class='subtitle'>Pharmaceutical Synthesis Comparator</p>",
    unsafe_allow_html=True
)
st.divider()

# -------------------------
# MOLECULE DATA
# -------------------------
molecules = ["Ibuprofen", "Artemisinin", "Sitagliptin", "Sertraline"]

formulas = {
    "Ibuprofen": "C₁₃H₁₈O₂",
    "Artemisinin": "C₁₅H₂₂O₅",
    "Sitagliptin": "C₁₆H₁₅F₆N₅O",
    "Sertraline": "C₁₇H₁₇Cl₂N",
}

# -------------------------
# MOLECULE SELECTOR
# -------------------------
st.markdown("<div class='section-title'>Choose a molecule</div>", unsafe_allow_html=True)

outer = st.columns([1, 3, 1, 3, 1])

for i, mol in enumerate(molecules):
    with outer[1 if i % 2 == 0 else 3]:
        label = f"{mol}\n{formulas[mol]}"
        if st.button(label, key=mol):
            st.session_state.selected = mol

# -------------------------
# DISPLAY RESULTS
# -------------------------
selected = st.session_state.get("selected", None)

if selected:
    st.divider()
    st.success(f"You selected: **{selected}**")

    if results_df.empty:
        st.warning("No results file found yet. Run the metrics pipeline first.")
        st.stop()

    mol_df = results_df[results_df["drug_name"].str.lower() == selected.lower()].copy()

    if mol_df.empty:
        st.info("No computed pathways available yet for this molecule.")
        st.stop()

    # -------------------------
    # TOP SUMMARY
    # -------------------------
    best_ae = mol_df["atom_economy_percent"].max() if "atom_economy_percent" in mol_df.columns else None
    best_pmi = mol_df["pmi"].min() if "pmi" in mol_df.columns else None
    best_ef = mol_df["e_factor"].min() if "e_factor" in mol_df.columns else None
    best_yield = (
        mol_df["overall_yield_percent_from_summary"].max()
        if "overall_yield_percent_from_summary" in mol_df.columns else None
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best atom economy", f"{best_ae:.2f}%" if pd.notna(best_ae) else "—")
    c2.metric("Lowest PMI", f"{best_pmi:.2f}" if pd.notna(best_pmi) else "—")
    c3.metric("Lowest E-factor", f"{best_ef:.2f}" if pd.notna(best_ef) else "—")
    c4.metric("Best overall yield", f"{best_yield:.2f}%" if pd.notna(best_yield) else "—")

    st.caption("Higher atom economy and yield are better. Lower PMI and E-factor are better.")

    st.divider()

    # -------------------------
    # COMPARISON TABLE
    # -------------------------
    st.markdown("<div class='section-title'>Pathway comparison</div>", unsafe_allow_html=True)

    display_cols = [
        "route_name",
        "atom_economy_percent",
        "pmi",
        "e_factor",
        "overall_yield_percent_from_summary",
        "number_of_steps",
        "average_hazard_score",
        "overall_solvent_profile",
    ]

    display_cols = [c for c in display_cols if c in mol_df.columns]
    table_df = mol_df[display_cols].copy()

    rename_map = {
        "route_name": "Pathway",
        "atom_economy_percent": "Atom economy (%)",
        "pmi": "PMI",
        "e_factor": "E-factor",
        "overall_yield_percent_from_summary": "Overall yield (%)",
        "number_of_steps": "Steps",
        "average_hazard_score": "Hazard score",
        "overall_solvent_profile": "Solvent profile",
    }
    table_df = table_df.rename(columns=rename_map)

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    st.divider()

    # -------------------------
    # DETAILED ROUTE VIEW
    # -------------------------
    st.markdown("<div class='section-title'>Inspect one pathway</div>", unsafe_allow_html=True)

    route_names = mol_df["route_name"].dropna().tolist()
    selected_route_name = st.selectbox("Select a pathway", route_names)

    route_row = mol_df[mol_df["route_name"] == selected_route_name].iloc[0]

    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric(
            "Atom economy",
            f"{route_row['atom_economy_percent']:.2f}%"
            if pd.notna(route_row.get("atom_economy_percent")) else "—"
        )
        st.metric(
            "PMI",
            f"{route_row['pmi']:.2f}"
            if pd.notna(route_row.get("pmi")) else "—"
        )

    with d2:
        st.metric(
            "E-factor",
            f"{route_row['e_factor']:.2f}"
            if pd.notna(route_row.get("e_factor")) else "—"
        )
        st.metric(
            "Overall yield",
            f"{route_row['overall_yield_percent_from_summary']:.2f}%"
            if pd.notna(route_row.get("overall_yield_percent_from_summary")) else "—"
        )

    with d3:
        st.metric(
            "Steps",
            f"{int(route_row['number_of_steps'])}"
            if pd.notna(route_row.get("number_of_steps")) else "—"
        )
        st.metric(
            "Hazard score",
            f"{route_row['average_hazard_score']:.2f}"
            if pd.notna(route_row.get("average_hazard_score")) else "—"
        )

    st.markdown("#### Solvent profile")
    st.write(route_row.get("overall_solvent_profile", "—"))

    st.markdown("#### Route name")
    st.write(route_row.get("route_name", "—"))

    with st.expander("Show raw data for this pathway"):
        st.json(route_row.to_dict())