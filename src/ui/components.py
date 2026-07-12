import streamlit as st

def title():

    st.title("🚀 HackMind AI")

    st.caption(
        "Multi-Agent Hackathon Planning Assistant"
    )


def metric_card(title: str, value, icon: str):
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="font-size:32px;">{icon}</div>
                <div style="font-size:30px;font-weight:bold;">{value}</div>
                <div style="color:gray;">{title}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )