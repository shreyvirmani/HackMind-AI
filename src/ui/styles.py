import streamlit as st

def load_css():

    st.markdown(
        """
<style>

.main {
    padding-top: 1rem;
}

.stButton>button {
    width:100%;
    border-radius:12px;
    height:50px;
    font-size:18px;
    font-weight:bold;
}

.stTextArea textarea {
    font-size:16px;
}

h1{
    text-align:center;
}

</style>
""",
        unsafe_allow_html=True,
    )