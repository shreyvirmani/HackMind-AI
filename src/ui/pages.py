import streamlit as st

from src.controllers.research_controller import research_controller
from src.controllers.planner_controller import planner_controller
from src.exceptions.llm_exceptions import InvalidResponseError
from src.exceptions.llm_exceptions import ModelUnavailableError
from src.ui.components import metric_card
from src.exporters.pdf_exporter import export_pdf
from src.controllers.judge_controller import judge_controller

def planner_page():

    st.subheader("💡 Describe Your Hackathon Idea")

    idea = st.text_area(
    "Hackathon Idea",
    placeholder="Example: An AI platform that helps students find teammates during hackathons...",
    height=180,
    label_visibility="collapsed",
)

    if "roadmap" not in st.session_state:
        st.session_state["roadmap"] = None

    if "research" not in st.session_state:
        st.session_state["research"] = None

    if "judge" not in st.session_state:
        st.session_state["judge"] = None


    if st.button("🚀 Generate Roadmap"):

        if not idea.strip():

            st.warning("Please enter your idea.")

            return

        with st.spinner("Generating roadmap..."):

            try:
                roadmap = planner_controller.generate_plan(idea)
                st.session_state["roadmap"] = roadmap

            except InvalidResponseError  as e:
                st.error(str(e))
                return
            
            st.success(
                "✅ AI roadmap generated successfully."
            ) 

    if st.session_state.roadmap is not None:

        roadmap = st.session_state.roadmap   

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

        with st.container(border=True):

            st.markdown(
                f"<h2 style='text-align:center;'>🚀 {roadmap.project_title}</h2>",
                unsafe_allow_html=True,
            )

            st.markdown(
                "<p style='text-align:center;color:gray;'>✨ AI-generated project blueprint</p>",
                unsafe_allow_html=True,
            )

            st.info(roadmap.solution)

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

        st.divider()

        pdf = export_pdf(roadmap)

        st.download_button(
            label="📄 Download Roadmap PDF",
            data=pdf,
            file_name=f"{roadmap.project_title}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        if st.button("🔍 Enhance with AI Research", use_container_width=True):

            with st.spinner("Researching project..."):

                try:
                    report = research_controller.generate_research(
                        st.session_state["roadmap"].model_dump_json(indent=2)
                    )

                    st.session_state["research"] = report

                except ModelUnavailableError as e:
                    st.warning(str(e))

            st.session_state["research"] = report

        if st.session_state["research"]:
            
            research = st.session_state["research"]

            st.divider()

            st.header("🔍 AI Research Report")

            competitors_tab, api_tab, risks_tab, tips_tab = st.tabs(
                [
                    "🏆 Competitors",
                    "🔌 APIs",
                    "⚠️ Risks",
                    "🚀 Tips",
                ]
            )

            # ================= COMPETITORS =================

            with competitors_tab:

                for competitor in research.competitors:

                    with st.container(border=True):

                        st.markdown(f"### 🏆 {competitor.name}")

                        st.write(competitor.description)

            # ================= APIs =================

            with api_tab:

                for api in research.recommended_apis:

                    with st.container(border=True):

                        st.markdown(f"### 🔌 {api.name}")

                        st.write(api.purpose)

            # ================= RISKS =================

            with risks_tab:

                for risk in research.implementation_risks:

                    with st.expander(
                        f"⚠️ {risk.title}",
                        expanded=False,
                    ):

                        st.write(risk.mitigation)

            # ================= TIPS =================

            with tips_tab:

                for tip in research.optimization_tips:

                    st.success(tip)

        if st.button(
            "🏆 Evaluate Project",
            use_container_width=True,
        ):

            with st.spinner("Evaluating project..."):

                report = judge_controller.evaluate_project(
                    st.session_state["roadmap"].model_dump_json(indent=2)
                )

                st.session_state["judge"] = report

        if st.session_state["judge"]:

            report = st.session_state["judge"]

            st.divider()

            st.header("🏆 AI Project Evaluation")

            col1, col2 = st.columns(2)

            with col1:
                metric_card(
                    "Overall Score",
                    f"{report.overall_score}/100",
                    "🏆",
                )

            with col2:

                metric_card(
                    "Evaluation Areas",
                    len(report.scores),
                    "📊",
                )

            st.divider() 

            scores_tab, strengths_tab, improvements_tab = st.tabs(
                [
                    "📊 Scores",
                    "💪 Strengths",
                    "🚀 Improvements",
                ]
            )

            with scores_tab:

                for score in report.scores:

                    with st.container(border=True):

                        st.markdown(f"### {score.category}")

                        st.progress(score.score / 10)

                        st.write(f"**Score:** {score.score}/10")

                        st.caption(score.feedback)

            with strengths_tab:

                st.subheader("✅ Strengths")

                for item in report.strengths:

                    st.success(item)

                st.subheader("⚠️ Weaknesses")

                for item in report.weaknesses:

                    st.warning(item)

            with improvements_tab:

                st.subheader("🚀 Suggestions")

                for item in report.improvements:

                    st.info(item)

                st.divider()

                st.subheader("Overall Feedback")

                st.write(report.overall_feedback)