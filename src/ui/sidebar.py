import streamlit as st


def render_sidebar():

    with st.sidebar:

        # ==========================================
        # LOGO
        # ==========================================
        
        st.markdown("# 🚀 HackMind AI")

        st.caption("Multi-Agent Hackathon Planning Assistant")

        st.success("🟢 Version 1.0 ")

        st.metric(
            label="🤖 AI Agents",
            value="4",
            border=True,
        )
        st.markdown("""
        <style>
        [data-testid="stMetric"] {
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.divider()

        # ==========================================
        # AGENTS
        # ==========================================

        st.subheader("🤖 AI Agents")

        st.markdown(
            """
🧠 **Planner** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ✅ Ready

🔍 **Research** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ✅ Ready

🏆 **Judge** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ✅ Ready

🎤 **Pitch Deck** &nbsp;&nbsp; ✅ Ready
"""
        )

        st.divider()

        # ==========================================
        # EXPORTS
        # ==========================================

        st.subheader("📦 Export Options")

        st.markdown(
            """
📄 **Roadmap PDF**

📊 **PowerPoint (.pptx)**
"""
        )

        st.divider()

        # ==========================================
        # TECH STACK
        # ==========================================

        st.subheader("⚡ Built With")

        col1, col2 = st.columns(2)

        with col1:

            st.caption("🐍 Python")

            st.caption("🎈 Streamlit")

        with col2:

            st.caption("✨ Gemini")

            st.caption("📦 Pydantic")

        st.divider()

        # ==========================================
        # APP FEATURES
        # ==========================================

        st.subheader("✨ Features")

        st.caption("✔ AI Project Roadmap")

        st.caption("✔ Competitor Research")

        st.caption("✔ Judge Evaluation")

        st.caption("✔ Pitch Deck Generator")

        st.caption("✔ PDF & PPT Export")

        st.divider()

        # ==========================================
        # INFO
        # ==========================================

        st.info(
            """
Generate complete hackathon projects in minutes.

Plan • Research • Judge • Pitch
"""
        )

        st.divider()

        st.caption(
            """


                     🚀 HackMind AI v1.0

                Built with Python • Streamlit • Gemini AI

                     © 2026 Shrey Virmani
            """
        )

        st.divider()

        st.markdown("### 🌐 Connect")

        st.link_button(
            "⭐ GitHub ",
            "https://github.com/shreyvirmani",
            use_container_width=True,
        )

        st.link_button(
            "💼 LinkedIn",
            "https://www.linkedin.com/in/shrey-virmani-1a352a325/",
            use_container_width=True,
        )
        