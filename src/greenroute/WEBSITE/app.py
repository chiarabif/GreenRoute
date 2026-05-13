import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from textwrap import dedent

st.set_page_config(page_title="GreenRoute", page_icon="🌱", layout="wide")

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[2]
LOGO_PATH = BASE_DIR / "greenroute-logo.png"
RESULTS_PATH = PROJECT_ROOT / "data" / "results" / "calculated_green_metrics.csv"
SMILES_IMAGE_DIR = PROJECT_ROOT / "SRC" / "greenroute" / "SMILES"
REACTION_IMAGE_DIR = PROJECT_ROOT / "SRC" / "greenroute" / "REACTIONS"

# Page style
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1300px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-top: -8px;
        margin-bottom: 8px;
    }

    .section-title {
        text-align: center;
        font-weight: 700;
        font-size: 28px;
        margin-top: 1.2rem;
        margin-bottom: 1.5rem;
    }

    .molecule-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8E2;
        border-radius: 24px;
        padding: 30px 32px 26px 32px;
        min-height: 300px;
        box-shadow: 0 8px 24px rgba(46, 125, 50, 0.08);
        transition: all 0.2s ease;
        margin-bottom: 14px;
    }

    .molecule-card:hover {
        border-color: #4A7040;
        box-shadow: 0 12px 30px rgba(46, 125, 50, 0.16);
        transform: translateY(-3px);
    }

    .molecule-title {
        font-size: 31px;
        font-weight: 750;
        color: #20232A;
        margin-bottom: 4px;
    }

    .molecule-formula {
        font-size: 18px;
        color: #6A6A6A;
        font-weight: 650;
        letter-spacing: 0.8px;
        margin-bottom: 22px;
    }

    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 24px;
    }

    .tag {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 999px;
        font-size: 15px;
        font-weight: 600;
        line-height: 1;
    }

    .tag-green {
        background: #E4EDE0;
        color: #4A7040;
    }

    .tag-muted {
        background: #F0EEE8;
        color: #6D6659;
    }

    .metric-label {
        font-size: 18px;
        color: #3D3D3D;
        margin-bottom: 9px;
    }

    .progress-track {
        width: 100%;
        height: 12px;
        background: #F0EEE8;
        border-radius: 999px;
        overflow: hidden;
    }

    .progress-fill-green {
        height: 100%;
        background: #7FAD6A;
        border-radius: 999px;
    }

    .progress-fill-orange {
        height: 100%;
        background: #E39A27;
        border-radius: 999px;
    }

    .progress-value {
        text-align: right;
        font-size: 17px;
        color: #6A6A6A;
        font-weight: 650;
        margin-top: 7px;
    }

    div.stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 16px;
        border: 1.5px solid #D4E2CE;
        background-color: #F3F7F1;
        color: #4A7040;
        font-size: 17px;
        font-weight: 700;
        margin-top: 6px;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #4A7040;
        background-color: #E8F0E4;
        color: #385530;
        box-shadow: 0 6px 16px rgba(46, 125, 50, 0.14);
    }

    .image-caption {
        text-align: center;
        color: #6A6A6A;
        font-size: 14px;
        margin-top: -8px;
        margin-bottom: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load results
@st.cache_data
def load_results(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(csv_path)

    if "drug_name" in df.columns:
        df["drug_name"] = df["drug_name"].replace({"Sertralin": "Sertraline"})

    return df


results_df = load_results(RESULTS_PATH)

# Header
_, center, _ = st.columns([2.4, 2, 2.4])

with center:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=2000)
    else:
        st.title("GreenRoute 🌱")

st.markdown(
    "<p class='subtitle'>Pharmaceutical Synthesis Comparator</p>",
    unsafe_allow_html=True,
)

st.divider()

# Molecule data
formulas = {
    "Ibuprofen": "C₁₃H₁₈O₂",
    "Artemisinin": "C₁₅H₂₂O₅",
    "Sitagliptin": "C₁₆H₁₅F₆N₅O",
    "Sertraline": "C₁₇H₁₇Cl₂N",
}

# Molecule image files
molecule_image_files = {
    "Ibuprofen": "ibuprofen.png",
    "Artemisinin": "artemisinin.png",
    "Sitagliptin": "sitagliptin.png",
    "Sertraline": "sertraline.png",
}


def get_molecule_image_path(molecule: str):
    image_name = molecule_image_files.get(molecule)

    if image_name is None:
        return None

    image_path = SMILES_IMAGE_DIR / image_name

    if image_path.exists():
        return image_path

    return None


# Reaction scheme files
def get_reaction_scheme_path(route_name: str):
    route_name_lower = str(route_name).lower()

    route_image_map = {
        "boots": "ibuprofen_boots.png",
        "bhc": "ibuprofen_bhc.png",
        "hoechst": "ibuprofen_bhc.png",
        "celanese": "ibuprofen_bhc.png",
        "flow": "ibuprofen_flow.png",
        "continuous-flow": "ibuprofen_flow.png",
        "continuous flow": "ibuprofen_flow.png",
        "jolliffe": "ibuprofen_flow.png",
        "jollife": "ibuprofen_flow.png",
        "gerogiorgis": "ibuprofen_flow.png",
        "gerogiorg": "ibuprofen_flow.png",

        "pfizer": "sertraline_pfizer.png",
        "marx": "sertraline_marx.png",

        "2nd": "sitagliptin_merck_2nd_gen.png",
        "second": "sitagliptin_merck_2nd_gen.png",
        "3rd": "sitagliptin_merck_3rd_gen.png",
        "third": "sitagliptin_merck_3rd_gen.png",

        "cook": "artemisinin_cook.png",
        "yadav": "artemisinin_yadav.png",
        "roche": "artemisinin_roche_schmid.png",
        "schmid": "artemisinin_roche_schmid.png",
        "sanofi": "artemisinin_sanofi.png",
    }

    for keyword, filename in route_image_map.items():
        if keyword in route_name_lower:
            image_path = REACTION_IMAGE_DIR / filename

            if image_path.exists():
                return image_path

    return None


# Card data
def get_molecule_summary(molecule: str) -> dict:
    if results_df.empty or "drug_name" not in results_df.columns:
        return {
            "pathways": None,
            "best_atom_economy": None,
        }

    mol_df = results_df[
        results_df["drug_name"].astype(str).str.lower() == molecule.lower()
    ]

    if mol_df.empty:
        return {
            "pathways": 0,
            "best_atom_economy": None,
        }

    if "route_name" in mol_df.columns:
        pathways = mol_df["route_name"].dropna().nunique()
    else:
        pathways = len(mol_df)

    if "display_atom_economy_percent" in mol_df.columns:
        best_atom_economy = mol_df["display_atom_economy_percent"].max()
    else:
        best_atom_economy = None

    return {
        "pathways": pathways,
        "best_atom_economy": best_atom_economy,
    }


def render_tags(summary: dict) -> str:
    tags = []

    if summary["pathways"] is None:
        tags.append('<span class="tag tag-muted">No results file</span>')
    elif summary["pathways"] == 0:
        tags.append('<span class="tag tag-muted">No pathways available</span>')
    elif summary["pathways"] == 1:
        tags.append('<span class="tag tag-green">1 pathway</span>')
    else:
        tags.append(f'<span class="tag tag-green">{summary["pathways"]} pathways</span>')

    return '<div class="tag-row">' + "".join(tags) + '</div>'


def render_molecule_card(molecule: str) -> str:
    summary = get_molecule_summary(molecule)
    best_atom_economy = summary["best_atom_economy"]

    if best_atom_economy is not None and pd.notna(best_atom_economy):
        metric_value = float(best_atom_economy)
        progress_width = max(0, min(metric_value, 100))
        value_text = f"{metric_value:.0f}%"
        bar_class = "progress-fill-green" if metric_value >= 70 else "progress-fill-orange"
    else:
        progress_width = 0
        value_text = "—"
        bar_class = "progress-fill-orange"

    html = f"""
<div class="molecule-card">
    <div class="molecule-title">{molecule}</div>
    <div class="molecule-formula">{formulas[molecule]}</div>
    {render_tags(summary)}
    <div class="metric-label">Best atom economy</div>
    <div class="progress-track">
        <div class="{bar_class}" style="width:{progress_width}%;"></div>
    </div>
    <div class="progress-value">{value_text}</div>
</div>
"""
    return dedent(html).strip()


# Molecule selection
st.markdown("<div class='section-title'>Choose a molecule</div>", unsafe_allow_html=True)

row1 = st.columns(2, gap="large")
row2 = st.columns(2, gap="large")

card_layout = [
    ("Ibuprofen", row1[0]),
    ("Sitagliptin", row1[1]),
    ("Artemisinin", row2[0]),
    ("Sertraline", row2[1]),
]

for molecule, column in card_layout:
    with column:
        st.markdown(render_molecule_card(molecule), unsafe_allow_html=True)

        if st.button(f"Select {molecule}", key=f"select_{molecule}"):
            st.session_state.selected = molecule

# Selected molecule
selected = st.session_state.get("selected", None)

if selected:
    st.divider()
    st.markdown(
        f"""<div style="background-color:#EEF5E9; color:#4A7040; border-radius:8px; padding:12px 18px; font-weight:600; font-size:16px; margin-bottom:8px;">
        You selected: {selected}</div>""",
        unsafe_allow_html=True,
    )

    molecule_image_path = get_molecule_image_path(selected)

    if molecule_image_path is not None:
        st.markdown("### Molecular structure")

        _, image_center, _ = st.columns([1.4, 2.2, 1.4])

        with image_center:
            st.image(str(molecule_image_path), use_container_width=True)

        st.markdown(
            f"<p class='image-caption'>{selected} molecular structure</p>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No molecular structure image available yet.")

    if results_df.empty:
        st.warning("No results file found yet. Run the metrics pipeline first.")
        st.stop()

    if "drug_name" not in results_df.columns:
        st.error("The results file does not contain a 'drug_name' column.")
        st.stop()

    mol_df = results_df[
        results_df["drug_name"].astype(str).str.lower() == selected.lower()
    ].copy()

    if mol_df.empty:
        st.info("No computed pathways available yet for this molecule.")
        st.stop()

    # Best pathway rows
    best_ae_row = (
        mol_df.loc[mol_df["display_atom_economy_percent"].idxmax()]
        if "display_atom_economy_percent" in mol_df.columns
        and mol_df["display_atom_economy_percent"].notna().any()
        else None
    )

    best_pmi_row = (
        mol_df.loc[mol_df["display_pmi"].idxmin()]
        if "display_pmi" in mol_df.columns
        and mol_df["display_pmi"].notna().any()
        else None
    )

    best_ef_row = (
        mol_df.loc[mol_df["display_e_factor"].idxmin()]
        if "display_e_factor" in mol_df.columns
        and mol_df["display_e_factor"].notna().any()
        else None
    )

    best_yield_row = (
        mol_df.loc[mol_df["display_overall_yield_percent"].idxmax()]
        if "display_overall_yield_percent" in mol_df.columns
        and mol_df["display_overall_yield_percent"].notna().any()
        else None
    )

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Best atom economy",
        f"{best_ae_row['display_atom_economy_percent']:.2f}%" if best_ae_row is not None else "—",
    )
    if best_ae_row is not None:
        c1.caption(best_ae_row["route_name"])

    c2.metric(
        "Lowest PMI",
        f"{best_pmi_row['display_pmi']:.2f}" if best_pmi_row is not None else "—",
    )
    if best_pmi_row is not None:
        c2.caption(best_pmi_row["route_name"])

    c3.metric(
        "Lowest E-factor",
        f"{best_ef_row['display_e_factor']:.2f}" if best_ef_row is not None else "—",
    )
    if best_ef_row is not None:
        c3.caption(best_ef_row["route_name"])

    c4.metric(
        "Best overall yield",
        f"{best_yield_row['display_overall_yield_percent']:.2f}%"
        if best_yield_row is not None
        else "—",
    )
    if best_yield_row is not None:
        c4.caption(best_yield_row["route_name"])

    st.caption("Higher atom economy and yield are better. Lower PMI and E-factor are better.")

    st.divider()

    # Comparison table
    st.markdown("<div class='section-title'>Pathway comparison</div>", unsafe_allow_html=True)

    display_cols = [
        "route_name",
        "display_atom_economy_percent",
        "display_pmi",
        "display_e_factor",
        "display_overall_yield_percent",
        "display_number_of_steps",
        "average_hazard_score",
        "overall_solvent_profile",
    ]

    display_cols = [col for col in display_cols if col in mol_df.columns]
    table_df = mol_df[display_cols].copy()

    rename_map = {
        "route_name": "Pathway",
        "display_atom_economy_percent": "Atom economy (%)",
        "display_pmi": "PMI",
        "display_e_factor": "E-factor",
        "display_overall_yield_percent": "Overall yield (%)",
        "display_number_of_steps": "Steps",
        "average_hazard_score": "Hazard score",
        "overall_solvent_profile": "Solvent profile",
    }

    table_df = table_df.rename(columns=rename_map)

    numeric_cols = [
        "Atom economy (%)",
        "PMI",
        "E-factor",
        "Overall yield (%)",
        "Steps",
        "Hazard score",
    ]

    for col in numeric_cols:
        if col in table_df.columns:
            table_df[col] = pd.to_numeric(table_df[col], errors="coerce")

    def highlight_best_worst(series, higher_is_better=True):
        styles = [""] * len(series)
        valid = series.dropna()

        if valid.empty:
            return styles

        best_value = valid.max() if higher_is_better else valid.min()
        worst_value = valid.min() if higher_is_better else valid.max()

        for i, value in enumerate(series):
            if pd.isna(value):
                styles[i] = "background-color: #F5F5F5; color: #9E9E9E;"
            elif value == best_value:
                styles[i] = "background-color: #E4EDE0; color: #2D4A22; font-weight: 700;"
            elif value == worst_value and best_value != worst_value:
                styles[i] = "background-color: #FFF3E0; color: #E65100; font-weight: 600;"
            else:
                styles[i] = ""

        return styles

    styled_table = table_df.style.format(
        {
            "Atom economy (%)": "{:.2f}",
            "PMI": "{:.2f}",
            "E-factor": "{:.2f}",
            "Overall yield (%)": "{:.2f}",
            "Steps": "{:.0f}",
            "Hazard score": "{:.2f}",
        },
        na_rep="—",
    )

    if "Atom economy (%)" in table_df.columns:
        styled_table = styled_table.apply(
            highlight_best_worst,
            subset=["Atom economy (%)"],
            higher_is_better=True,
        )

    if "PMI" in table_df.columns:
        styled_table = styled_table.apply(
            highlight_best_worst,
            subset=["PMI"],
            higher_is_better=False,
        )

    if "E-factor" in table_df.columns:
        styled_table = styled_table.apply(
            highlight_best_worst,
            subset=["E-factor"],
            higher_is_better=False,
        )

    if "Overall yield (%)" in table_df.columns:
        styled_table = styled_table.apply(
            highlight_best_worst,
            subset=["Overall yield (%)"],
            higher_is_better=True,
        )

    if "Steps" in table_df.columns:
        styled_table = styled_table.apply(
            highlight_best_worst,
            subset=["Steps"],
            higher_is_better=False,
        )

    if "Hazard score" in table_df.columns:
        styled_table = styled_table.apply(
            highlight_best_worst,
            subset=["Hazard score"],
            higher_is_better=False,
        )

    st.dataframe(styled_table, use_container_width=True, hide_index=True)

    st.caption("Green = better value for that metric. Orange = less favorable value. Grey = unavailable value.")

    # Spider chart
    radar_metrics = {
        "Atom economy (%)": True,
        "Overall yield (%)": True,
        "PMI": False,
        "E-factor": False,
        "Steps": False,
        "Hazard score": False,
    }

    radar_cols = [m for m in radar_metrics if m in table_df.columns]

    if len(radar_cols) >= 3:
        raw_df = table_df[["Pathway"] + radar_cols].copy()
        for col in radar_cols:
            raw_df[col] = pd.to_numeric(raw_df[col], errors="coerce")

        RADAR_MIN = 0.15
        norm_df = raw_df.copy()
        for col in radar_cols:
            col_vals = raw_df[col]
            col_min, col_max = col_vals.min(), col_vals.max()
            if col_max == col_min:
                norm_df[col] = 1.0
            elif radar_metrics[col]:
                norm_df[col] = RADAR_MIN + (1 - RADAR_MIN) * (col_vals - col_min) / (col_max - col_min)
            else:
                norm_df[col] = RADAR_MIN + (1 - RADAR_MIN) * (1 - (col_vals - col_min) / (col_max - col_min))

        categories = radar_cols + [radar_cols[0]]
        dark_colors = ["#2E7D32", "#1565C0", "#E65100", "#6A1B9A", "#B71C1C", "#00695C"]
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#00BCD4"]

        fig = go.Figure()

        for idx, (i, norm_row) in enumerate(norm_df.iterrows()):
            raw_row = raw_df.loc[i]
            norm_vals = [norm_row[c] if pd.notna(norm_row[c]) else None for c in radar_cols]
            raw_vals = [raw_row[c] for c in radar_cols]
            norm_vals_closed = norm_vals + [norm_vals[0]]

            hover_lines = [
                f"{c}: <b>{rv:.2f}</b>" if pd.notna(rv) else f"{c}: <b>N/A</b>"
                for c, rv in zip(radar_cols, raw_vals)
            ]
            hover_text = "<br>".join(hover_lines)
            dark_color = dark_colors[idx % len(dark_colors)]

            fig.add_trace(go.Scatterpolar(
                r=norm_vals_closed,
                theta=categories,
                fill="none",
                name=norm_row["Pathway"],
                mode="lines+markers",
                line=dict(color=dark_color, width=2.5),
                marker=dict(size=6, color=dark_color),
                hovertemplate=f"<b>{norm_row['Pathway']}</b><br>{hover_text}<extra></extra>",
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False),
                angularaxis=dict(tickfont=dict(size=12)),
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            margin=dict(t=60, b=100, l=80, r=80),
            height=520,
        )

        st.markdown("<div class='section-title'>Pathway radar chart</div>", unsafe_allow_html=True)
        st.caption("Hover over a point to see the actual values. The shape is scaled so all routes stay visible — outer edge = relatively better.")
        st.plotly_chart(fig, use_container_width=True, key="radar_chart")

    st.divider()

    # Route inspection
    st.markdown("<div class='section-title'>Inspect one pathway</div>", unsafe_allow_html=True)

    if "route_name" not in mol_df.columns:
        st.warning("No route names found in the results file.")
        st.stop()

    route_names = mol_df["route_name"].dropna().tolist()
    selected_route_name = st.selectbox("Select a pathway", route_names)

    route_row = mol_df[mol_df["route_name"] == selected_route_name].iloc[0]

    reaction_scheme_path = get_reaction_scheme_path(selected_route_name)

    if reaction_scheme_path is not None:
        st.markdown("### Reaction scheme")

        _, scheme_center, _ = st.columns([1.2, 2, 1.2])

        with scheme_center:
            st.image(str(reaction_scheme_path), use_container_width=True)

    else:
        st.info("No reaction scheme image available for this pathway yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    pmi_status = str(route_row.get("pmi_calc_status", "")).strip().lower()
    if pmi_status != "ok":
        st.markdown(
            """<div style="background-color:#EEF5E9; color:#4A7040; border-radius:8px; padding:12px 18px; font-size:15px; margin-bottom:8px;">
            Values shown for this pathway are taken from literature as detailed step-by-step data was unavailable for direct calculation.</div>""",
            unsafe_allow_html=True,
        )

    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric(
            "Atom economy",
            f"{route_row['display_atom_economy_percent']:.2f}%"
            if "display_atom_economy_percent" in route_row and pd.notna(route_row.get("display_atom_economy_percent"))
            else "—",
        )

        st.metric(
            "PMI",
            f"{route_row['display_pmi']:.2f}"
            if "display_pmi" in route_row and pd.notna(route_row.get("display_pmi"))
            else "—",
        )

    with d2:
        st.metric(
            "E-factor",
            f"{route_row['display_e_factor']:.2f}"
            if "display_e_factor" in route_row and pd.notna(route_row.get("display_e_factor"))
            else "—",
        )

        st.metric(
            "Overall yield",
            f"{route_row['display_overall_yield_percent']:.2f}%"
            if "display_overall_yield_percent" in route_row
            and pd.notna(route_row.get("display_overall_yield_percent"))
            else "—",
        )

    with d3:
        st.metric(
            "Steps",
            f"{int(route_row['display_number_of_steps'])}"
            if "display_number_of_steps" in route_row and pd.notna(route_row.get("display_number_of_steps"))
            else "—",
        )

        st.metric(
            "Hazard score",
            f"{route_row['average_hazard_score']:.2f}"
            if "average_hazard_score" in route_row and pd.notna(route_row.get("average_hazard_score"))
            else "—",
        )

    # Solvent impact
    solvent_profile = route_row.get("overall_solvent_profile", "—")

    if pd.isna(solvent_profile):
        solvent_profile = "Unavailable"

    profile_lower = str(solvent_profile).lower()

    if "recommended" in profile_lower:
        display_profile = "Highly recoverable"
        badge_color = "#E4EDE0"
        text_color = "#2D4A22"
    elif "hazardous" in profile_lower:
        display_profile = "Hazardous solvents"
        badge_color = "#FFEBEE"
        text_color = "#B71C1C"
    elif "problematic" in profile_lower:
        display_profile = "Polluting / difficult to recover"
        badge_color = "#FFEBEE"
        text_color = "#B71C1C"
    elif "moderate" in profile_lower or "mixed" in profile_lower:
        display_profile = "Moderate environmental impact"
        badge_color = "#FFF3E0"
        text_color = "#E65100"
    else:
        display_profile = "Unavailable"
        badge_color = "#F0F0F0"
        text_color = "#666666"

    st.markdown(
        f"""
        <div style="margin-top: 20px;">
            <div style="font-size: 18px; font-weight: 700; margin-bottom: 8px;">
                Solvent impact
            </div>
            <span style="
                display: inline-block;
                padding: 8px 16px;
                border-radius: 999px;
                background-color: {badge_color};
                color: {text_color};
                font-weight: 700;
            ">
                {display_profile}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Show raw data for this pathway"):
        st.json(route_row.to_dict())