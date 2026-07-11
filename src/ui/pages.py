import streamlit as st

from src.controllers.planner_controller import planner_controller
from src.exceptions.llm_exceptions import InvalidResponseError
from src.ui.components import metric_card

def planner_page():

    st.subheader("💡 Describe Your Hackathon Idea")

    idea = st.text_area(
    "Hackathon Idea",
    placeholder="Example: An AI platform that helps students find teammates during hackathons...",
    height=180,
    label_visibility="collapsed",
)

    if st.button("🚀 Generate Roadmap"):

        if not idea.strip():

            st.warning("Please enter your idea.")

            return

        with st.spinner("Generating roadmap..."):

            try:
                roadmap = planner_controller.generate_plan(idea)

            except InvalidResponseError  as e:
                st.error(str(e))
                return
            
                st.success(
                    "✅ AI roadmap generated successfully."
                )    

                feature_count = len(roadmap.key_features)

                team_count = len(roadmap.team_roles)

                phase_count = len(roadmap.development_timeline)

                tech_count = (
                    len(roadmap.tech_stack.frontend)
                    + len(roadmap.tech_stack.backend)
                    + len(roadmap.tech_stack.ai_ml)
                    + len(roadmap.tech_stack.database)
                    + len(roadmap.tech_stack.deployment)
                )

                st.markdown(
                    f"""
                    <div style="
                        padding:32px;
                        border-radius:20px;
                        background:linear-gradient(135deg,#2563eb,#7c3aed);
                        color:white;
                        margin-bottom:25px;
                    ">
                        <h1 style="margin:0;">
                            🚀 {roadmap.project_title}
                        </h1>

                        <p style="
                            font-size:18px;
                            margin-top:15px;
                            line-height:1.7;
                            color:#f3f4f6;
                        ">
                            {roadmap.solution}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("## 📊 Project Overview")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    metric_card(
                        "Features",
                        feature_count,
                        "✨",
                    )

                with col2:
                    metric_card(
                        "Team Members",
                        team_count,
                        "👥",
                    )

                with col3:
                    metric_card(
                        "Timeline Phases",
                        phase_count,
                        "📅",
                    )

                with col4:
                    metric_card(
                        "Technologies",
                        tech_count,
                        "⚙️",
                    )

                st.divider()

            overview_tab, tech_tab, timeline_tab, team_tab, future_tab = st.tabs(
                [
                    "📋 Overview",
                    "⚙️ Tech Stack",
                    "📅 Timeline",
                    "👥 Team",
                    "🚀 Future Scope",
                ]
            )

            # ================= OVERVIEW =================

            with overview_tab:

                st.subheader("📌 Problem Statement")
                st.write(roadmap.problem_statement)

                st.subheader("💡 Solution")
                st.write(roadmap.solution)

                st.subheader("✨ Key Features")

                for feature in roadmap.key_features:

                    st.success(feature)

            # ================= TECH STACK =================

            with tech_tab:

                tech = roadmap.tech_stack

                c1, c2 = st.columns(2)

                with c1:

                    with st.container(border=True):
                        st.markdown("### 🌐 Frontend")

                        for item in tech.frontend:
                            st.write("•", item)

                    with st.container(border=True):
                        st.markdown("### ⚙️ Backend")

                        for item in tech.backend:
                            st.write("•", item)

                    with st.container(border=True):
                        st.markdown("### 🗄 Database")

                        for item in tech.database:
                            st.write("•", item)

                with c2:

                    with st.container(border=True):
                        st.markdown("### 🤖 AI / ML")

                        for item in tech.ai_ml:
                            st.write("•", item)

                    with st.container(border=True):
                        st.markdown("### ☁️ Deployment")

                        for item in tech.deployment:
                            st.write("•", item)

                st.divider()

                with st.container(border=True):

                    st.subheader("🏗️ System Architecture")

                    st.write(roadmap.system_architecture)

            # ================= TIMELINE =================

            with timeline_tab:

                for phase in roadmap.development_timeline:

                    with st.expander(
                        f"🚩 {phase.phase}",
                        expanded=False
                        ):

                        for task in phase.tasks:

                            st.markdown(f"✅ {task}")

            # ================= TEAM =================

            with team_tab:

                cols = st.columns(2)

                for index, member in enumerate(roadmap.team_roles):

                    with cols[index % 2]:

                        with st.container(border=True):

                            st.markdown(f"### 👨‍💻 {member.role}")

                            st.caption(member.responsibilities)

            # ================= FUTURE =================

            with future_tab:

                with st.container(border=True):

                    st.subheader("🚀 Future Scope")

                    st.write(roadmap.future_scope)