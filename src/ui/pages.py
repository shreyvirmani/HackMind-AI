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

        st.markdown("---")

        st.markdown(roadmap)
        