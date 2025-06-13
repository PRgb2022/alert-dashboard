import streamlit as st
import pandas as pd
import sqlite3
import os

DB_PATH = "alerts.db"
CSV_PATH = "alerts.csv"

# Create DB from CSV if DB is missing
if not os.path.exists(DB_PATH):
    df_csv = pd.read_csv(CSV_PATH)
    conn = sqlite3.connect(DB_PATH)
    df_csv.to_sql("alerts", conn, index=False, if_exists="replace")
    conn.close()

# Connect to DB
conn = sqlite3.connect(DB_PATH)

# Sidebar filters
st.sidebar.title("Filter Alerts")
state_filter = st.sidebar.multiselect(
    "Select State(s)",
    pd.read_sql("SELECT DISTINCT state_name FROM alerts", conn)['state_name']
)
severity_filter = st.sidebar.multiselect(
    "Select Severity",
    pd.read_sql("SELECT DISTINCT severity FROM alerts", conn)['severity']
)
date_range = st.sidebar.date_input("Effective Date Range", [])

# Build query
query = "SELECT * FROM alerts WHERE 1=1"
if state_filter:
    state_list = "', '".join(state_filter)
    query += f" AND state_name IN ('{state_list}')"
if severity_filter:
    sev_list = "', '".join(severity_filter)
    query += f" AND severity IN ('{sev_list}')"
if len(date_range) == 2:
    query += f" AND DATE(effectiveTime) BETWEEN '{date_range[0]}' AND '{date_range[1]}'"

df = pd.read_sql(query, conn)

st.title("📊 Alert Monitoring Dashboard")
st.dataframe(df)

# Download button
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Filtered Data", csv, "filtered_alerts.csv", "text/csv")

# Summary
st.markdown("### 🔍 Summary")
st.write("Total Alerts:", len(df))
st.bar_chart(df['severity'].value_counts())
