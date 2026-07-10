import streamlit as st

def render_sidebar():

    with st.sidebar:

        st.title("🚀 HackMind AI")

        st.markdown("---")

        st.markdown(
            """
### Current Agent

🧠 Planner Agent

---

### Status

🟢 Gemini Connected

🟢 Cache Enabled

🟢 Rate Limiter Active

---

Version

0.1
"""
        )