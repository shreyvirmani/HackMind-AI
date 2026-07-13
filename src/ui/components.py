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

def hero():

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:30px 20px 40px 20px;
        ">

        <h1 style="
            font-size:48px;
            margin-bottom:8px;
        ">
        🚀 HackMind AI
        </h1>

        <p style="
            font-size:24px;
            color:#9ca3af;
            margin-bottom:10px;
        ">
        Turn Hackathon Ideas into Winning Projects
        </p>

        <p style="
            font-size:18px;
            color:#6b7280;
        ">
        Plan • Research • Judge • Pitch — All powered by AI
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


