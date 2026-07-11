import streamlit as st

def title():

    st.title("🚀 HackMind AI")

    st.caption(
        "Multi-Agent Hackathon Planning Assistant"
    )


def metric_card(title: str, value: str, icon: str):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,#1f2937,#111827);
            border:1px solid #374151;
            border-radius:18px;
            padding:22px;
            text-align:center;
            box-shadow:0 8px 24px rgba(0,0,0,.25);
            height:145px;
        ">
            <div style="font-size:34px;">{icon}</div>

            <div style="
                font-size:34px;
                font-weight:700;
                color:white;
                margin-top:8px;
            ">
                {value}
            </div>

            <div style="
                color:#9ca3af;
                font-size:15px;
                margin-top:6px;
            ">
                {title}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )
