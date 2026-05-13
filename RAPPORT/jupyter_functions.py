import plotly.graph_objects as go
import pandas as pd

import os
from PIL import Image
import matplotlib.pyplot as plt

SMILES_DIR = os.path.join("..", "src", "greenroute", "SMILES")

def show_smiles_grid(molecules=("ibuprofen", "artemisinin", "sertraline", "sitagliptin")):
    fig, axes = plt.subplots(1, len(molecules), figsize=(20, 5))
    for ax, name in zip(axes, molecules):
        img_path = os.path.join(SMILES_DIR, f"{name}.png")
        if os.path.exists(img_path):
            ax.imshow(Image.open(img_path))
            ax.set_title(name, fontsize=14)
        else:
            ax.text(0.5, 0.5, "Missing", ha="center")
        ax.axis("off")
    plt.tight_layout()
    plt.show()

RESULTS_PATH = "../data/results/calculated_green_metrics.csv"

RENAME_MAP = {
    "route_name": "Pathway",
    "display_atom_economy_percent": "Atom economy (%)",
    "display_pmi": "PMI",
    "display_e_factor": "E-factor",
    "display_overall_yield_percent": "Overall yield (%)",
    "display_number_of_steps": "Steps",
    "average_hazard_score": "Hazard score",
}

HIGHER_IS_BETTER = {
    "Atom economy (%)": True,
    "PMI": False,
    "E-factor": False,
    "Overall yield (%)": True,
    "Steps": False,
    "Hazard score": False,
}

def load_results():
    df = pd.read_csv(RESULTS_PATH)
    if "drug_name" in df.columns:
        df["drug_name"] = df["drug_name"].replace({"Sertralin": "Sertraline"})
    return df

def get_mol_df(results_df, molecule):
    return results_df[
        results_df["drug_name"].astype(str).str.lower() == molecule.lower()
    ].copy()

def show_comparison_table(mol_df):
    display_cols = [c for c in RENAME_MAP if c in mol_df.columns]
    table_df = mol_df[display_cols].rename(columns=RENAME_MAP)

    numeric_cols = [c for c in HIGHER_IS_BETTER if c in table_df.columns]
    for col in numeric_cols:
        table_df[col] = pd.to_numeric(table_df[col], errors="coerce")

    return table_df

def show_radar_chart(table_df):
    radar_metrics = {
        "Atom economy (%)": True,
        "Overall yield (%)": True,
        "PMI": False,
        "E-factor": False,
        "Steps": False,
        "Hazard score": False,
    }

    radar_cols = [m for m in radar_metrics if m in table_df.columns]
    raw_df = table_df[["Pathway"] + radar_cols].copy()
    for col in radar_cols:
        raw_df[col] = pd.to_numeric(raw_df[col], errors="coerce")

    RADAR_MIN = 0.15
    norm_df = raw_df.copy()
    for col in radar_cols:
        vals = raw_df[col]
        vmin, vmax = vals.min(), vals.max()
        if vmax == vmin:
            norm_df[col] = 1.0
        elif radar_metrics[col]:
            norm_df[col] = RADAR_MIN + (1 - RADAR_MIN) * (vals - vmin) / (vmax - vmin)
        else:
            norm_df[col] = RADAR_MIN + (1 - RADAR_MIN) * (1 - (vals - vmin) / (vmax - vmin))

    categories = radar_cols + [radar_cols[0]]
    dark_colors = ["#2E7D32", "#1565C0", "#E65100", "#6A1B9A"]
    fig = go.Figure()

    for idx, (_, row) in enumerate(norm_df.iterrows()):
        raw_row = raw_df[raw_df["Pathway"] == row["Pathway"]].iloc[0]
        values = [row[c] for c in radar_cols] + [row[radar_cols[0]]]
        hover_lines = [
            f"{c}: <b>{raw_row[c]:.2f}</b>" if pd.notna(raw_row[c]) else f"{c}: N/A"
            for c in radar_cols
        ]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill="none",
            name=row["Pathway"],
            mode="lines+markers",
            line=dict(color=dark_colors[idx % len(dark_colors)], width=2.5),
            marker=dict(size=6, color=dark_colors[idx % len(dark_colors)]),
            hovertemplate="<b>" + row["Pathway"] + "</b><br>" + "<br>".join(hover_lines) + "<extra></extra>",
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
    return fig


REACTIONS_DIR = os.path.join("..", "src", "greenroute", "REACTIONS")

ROUTE_IMAGE_MAP = {
    "boots": "ibuprofen_boots.png",
    "bhc": "ibuprofen_bhc.png",
    "hoechst": "ibuprofen_bhc.png",
    "flow": "ibuprofen_flow.png",
    "pfizer": "sertraline_pfizer.png",
    "marx": "sertraline_marx.png",
    "2nd": "sitagliptin_merck_2nd_gen.png",
    "3rd": "sitagliptin_merck_3rd_gen.png",
    "cook": "artemisinin_cook.png",
    "yadav": "artemisinin_yadav.png",
    "roche": "artemisinin_roche_schmid.png",
    "sanofi": "artemisinin_sanofi.png",
}

def show_route_inspection(mol_df, route_index=0):
    route_name = mol_df["route_name"].dropna().tolist()[route_index]
    route_row = mol_df[mol_df["route_name"] == route_name].iloc[0]

    print(f"Inspecting route: {route_name}\n")

    for keyword, filename in ROUTE_IMAGE_MAP.items():
        if keyword in route_name.lower():
            img_path = os.path.join(REACTIONS_DIR, filename)
            if os.path.exists(img_path):
                plt.figure(figsize=(12, 6))
                plt.imshow(Image.open(img_path))
                plt.axis("off")
                plt.title(f"Reaction scheme: {route_name}", fontsize=14)
                plt.show()
            break

    if str(route_row.get("pmi_calc_status", "")).strip().lower() != "ok":
        print("⚠️  Values taken from literature — step-by-step data unavailable for direct calculation.\n")

    metrics = {
        "Atom economy (%)": ("display_atom_economy_percent", "{:.2f}%"),
        "PMI":               ("display_pmi",                  "{:.2f}"),
        "E-factor":          ("display_e_factor",             "{:.2f}"),
        "Overall yield (%)": ("display_overall_yield_percent","{:.2f}%"),
        "Steps":             ("display_number_of_steps",      "{:.0f}"),
        "Hazard score":      ("average_hazard_score",         "{:.2f}"),
    }
    for label, (col, fmt) in metrics.items():
        val = route_row.get(col)
        print(f"{label}: {fmt.format(float(val)) if pd.notna(val) else '—'}")

    profile = str(route_row.get("overall_solvent_profile", "")).lower()
    if "recommended" in profile:
        label, color = "Highly recoverable", "\033[92m"
    elif "hazardous" in profile or "problematic" in profile:
        label, color = "Hazardous / difficult to recover", "\033[91m"
    elif "moderate" in profile or "mixed" in profile:
        label, color = "Moderate environmental impact", "\033[93m"
    else:
        label, color = "Unavailable", "\033[90m"
    print(f"\nSolvent impact: {color}{label}\033[0m")