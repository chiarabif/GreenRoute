import streamlit as st
from pathlib import Path

st.set_page_config(page_title="GreenRoute", page_icon="🌱", layout="wide")

# Image path that works no matter where you run Streamlit from
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "greenroute-logo.png"

# --- Centered logo ---
left, center, right = st.columns([2.4, 2, 2.4])

with center:
    st.image(str(LOGO_PATH), width=400)

# --- Subtitle (centered) ---
st.markdown(
    "<p style='text-align:center; font-size:18px;'>Pharmaceutical Synthesis Comparator</p>",
    unsafe_allow_html=True
)

st.divider()


# --- Data ---
molecules = ["Ibuprofen", "Artemisinin", "Sitagliptin", "Sertralin"]

formulas = {
    "Ibuprofen": "C₁₃H₁₈O₂",
    "Artemisinin": "C₁₅H₂₂O₅",
    "Sitagliptin": "C₁₆H₁₅F₆N₅O",
    "Sertralin": "C₁₇H₁₇Cl₂N",
}

# --- Button style ---
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 380px;
        height: 240px;
        margin: 24px auto;
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

        /* subtle green border */
        border: 1.5px solid #DCEEDC;

        background-color: #FFFFFF;

        /* soft green shadow */
        box-shadow: 0 6px 18px rgba(46, 125, 50, 0.08);

        transition: all 0.2s ease;
    }

    /* hover effect */
    div.stButton > button:hover {
        border-color: #2E7D32;
        background-color: #F4FAF4;
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(46, 125, 50, 0.18);
    }

    /* click effect */
    div.stButton > button:active {
        transform: translateY(0px);
        background-color: #E8F5E9;
    }

    /* molecule name (first line) */
    div.stButton > button::first-line {
        font-weight: 700;
        font-size: 26px;
        color: #2E7D32;  /* green title */
    }

    /* optional: soften formula color */
    div.stButton > button {
        color: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)




# Centered grid
outer = st.columns([1, 3, 1, 3, 1])

for i, mol in enumerate(molecules):
    with outer[1 if i % 2 == 0 else 3]:
        label = f"{mol}\n{formulas[mol]}"
        if st.button(label, key=mol):
            st.session_state.selected = mol

# --- Output ---
if "selected" in st.session_state:
    st.divider()
    st.success(f"You selected: **{st.session_state.selected}**")