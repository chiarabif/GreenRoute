import streamlit as st 
st.title("GreenRoute")
st.write("Pharmaceutical Synthesis Comparator")

molecule= st.selectbox("Choose a molecule", ["Ibuprofène", "Artemisinin", "Sitagliptine", "Sertraline"])

st.write("You chose: {molecule}")