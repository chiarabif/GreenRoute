import streamlit as st

st.set_page_config(page_title="GreenRoute💊", page_icon="💊", layout="wide")

st.markdown("""
<style>
h1 {
    text-align: center;
}

div[data-testid="stMarkdownContainer"] p {
    text-align: center;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

st.title("GreenRoute")
st.write("Pharmaceutical Synthesis Comparator")
st.divider()

molecules = ["Ibuprofen", "Artemisinin", "Sitagliptin", "Sertralin"]

formulas = {
    "Ibuprofen": "C₁₃H₁₈O₂",
    "Artemisinin": "C₁₅H₂₂O₅",
    "Sitagliptin": "C₁₆H₁₅F₆N₅O",
    "Sertralin": "C₁₇H₁₇Cl₂N",
}

st.markdown("""
<style>
div.stButton > button {
    width: 260px;
    height: 160px;
    margin: 6px auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    white-space: pre-line;
    font-size: 18px;
    padding: 0.8rem;
    line-height: 1.4;
}

div.stButton > button::first-line {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown("### Choose a molecule")

outer = st.columns([1, 2.2, 2.2, 1], gap="small")

for i, mol in enumerate(molecules):
    with outer[(i % 2) + 1]:
        label = f"{mol}\n{formulas[mol]}"
        if st.button(label, key=mol, use_container_width=False):
            st.session_state.selected = mol

if "selected" in st.session_state:
    st.divider()
    st.success(f"You selected: **{st.session_state.selected}**")