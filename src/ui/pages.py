import json
import streamlit as st

from src.controllers.planner_controller import planner_controller


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

            roadmap = planner_controller.generate_plan(idea)

        try:
            roadmap = json.loads(roadmap)

        except json.JSONDecodeError:
            st.error("AI returned an invalid response.")
            st.code(roadmap)
            return

        st.divider()

        st.title(roadmap["project_title"])

        st.subheader("📌 Problem Statement")
        st.write(roadmap["problem_statement"])

        st.subheader("💡 Solution")
        st.write(roadmap["solution"])

        st.subheader("✨ Key Features")

        for feature in roadmap["key_features"]:
            st.markdown(f"- {feature}")

        st.subheader("⚙️ Tech Stack")

        tech = roadmap["tech_stack"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Frontend")
            for item in tech["frontend"]:
                st.write("•", item)

            st.markdown("### Backend")
            for item in tech["backend"]:
                st.write("•", item)

        with col2:
            st.markdown("### AI / ML")
            for item in tech["ai_ml"]:
                st.write("•", item)

            st.markdown("### Database")
            for item in tech["database"]:
                st.write("•", item)

        st.markdown("### Deployment")

        for item in tech["deployment"]:
            st.write("•", item)

        st.subheader("📅 Development Timeline")

        for phase in roadmap["development_timeline"]:

            with st.expander(phase["phase"]):

                for task in phase["tasks"]:

                    st.markdown(f"- {task}")

        st.subheader("👨‍💻 Team Roles")

        for role in roadmap["team_roles"]:

            with st.expander(role["role"]):

                st.write(role["responsibilities"])

        st.subheader("🚀 Future Scope")

        st.write(roadmap["future_scope"])