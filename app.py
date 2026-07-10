import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone

st.set_page_config(
    page_title="beTFM",
    page_icon="🔵",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #081120;
        color: white;
    }

    h1, h2, h3, p, label {
        color: white;
    }

    .stDataFrame {
        background-color: #0f1f38;
    }

    .card {
        background-color: #0f1f38;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #1e3a5f;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

API_BASE = "https://api.the-odds-api.com/v4"


def get_api_key():
    try:
        return st.secrets["ODDS_API_KEY"]
    except Exception:
        return ""


@st.cache_data(ttl=1800)
def get_sports(api_key):
    url = f"{API_BASE}/sports/"
    params = {
        "apiKey": api_key
    }

    response = requests.get(url, params=params, timeout=20)

    if response.status_code != 200:
        return []

    return response.json()


@st.cache_data(ttl=300)
def get_odds(api_key, sport_key, regions):
    url = f"{API_BASE}/sports/{sport_key}/odds"

    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": "h2h,totals",
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }

    response = requests.get(url, params=params, timeout=25)

    if response.status_code != 200:
        return []

    return response.json()


def parse_datetime(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def format_datetime_br(value):
    dt = parse_datetime(value)

