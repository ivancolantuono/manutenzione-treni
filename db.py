import os
from supabase import create_client
import streamlit as st

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

@st.cache_data(ttl=60)
def get_operatori():
    res = supabase.table("operatori").select("*").execute()
    return res.data or []

@st.cache_data(ttl=60)
def get_planning():
    res = supabase.table("planning").select("*").execute()
    return res.data or []