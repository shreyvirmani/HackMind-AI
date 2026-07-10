import streamlit as st

from src.ui.styles import load_css
from src.ui.sidebar import render_sidebar
from src.ui.components import title
from src.ui.pages import planner_page


st.set_page_config(
    page_title="HackMind AI",
    page_icon="🚀",
    layout="wide",
)

load_css()

render_sidebar()

title()

planner_page()
