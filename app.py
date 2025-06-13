import streamlit as st
import pandas as pd
import sqlite3
import os

DB_PATH = "alerts.db"
CSV_PATH = "alerts.csv"

# Step 1: Ensure database exists by creating it from CSV
try:
    if not os.path.exists(DB_PATH):
        if not os.path.exists(CSV_PATH):
            st.error("❌ Error: 'alerts.csv' is missing. Please add it to the project folder.")
            st.stop()

        df_csv = pd.read_csv(CSV_PATH)
        conn = sqlite3.connect(DB_PATH)
        df_csv.to_sql("alerts", conn, index=False, if_exists="replace")
        conn.close()
except Exception as e:
    st.error(f"❌ Failed to create alerts.db: {e}")
    st.stop()

# Step 2: Connect to DB and fetch distinct values
conn = sqlite3.connect(DB_PATH)

try:
    state_list_query = pd.read_sql("SELECT DISTINCT state_name FROM alerts", conn)['state_name']
    severity_list_query = pd.read_sql("SELECT DISTINCT severity FROM alerts", conn)['severity']
except Exception as e:
    st.error(f"❌ Error reading data from alerts.db: {e}")
    st.stop()

# Step 3: UI
st.title("📊 Alert Monitoring Dashboard")
st.markdown("Filter alerts by state, severity, and date range.")

# Sidebar filters
st.sidebar.title("Filter Alerts")
state_filter = st.sidebar.multiselect("Select State(s)", state_list_query)
severity_filter = st.sidebar.multiselect("Select Severity", severity_list_query)
date_range = st.sidebar.date_input("Effective Date Range", [])

# Step 4: Build filtered query
query = "SELECT * FROM alerts WHERE 1=1"
if state_filter:
    query += f" AND state_name IN ({','.join([f'\"{x}\"' for x in state_filter])})"
if severity_filter:
    query += f" AND severity IN ({','.join([f'\"{x}\"' for x in severity_filter])})"
if len(date_range) == 2:
    query += f" AND DATE(effectiveTime) BETWEEN '{date_range[0]}' AND '{date_range[1]}'"

# Step 5: Load filtered data
try:
    df = pd.read_sql(query, conn)
except Exception as e:
    st.error(f"❌ Failed to query database: {e}")
    st.stop()

st.dataframe(df)

# Step 6: Download option
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Filtered Data", csv, "filtered_alerts.csv", "text/csv")

# Step 7: Summary
st.markdown("### 📈 Alert Summary")
st.write("Total Alerts:", len(df))
if not df.empty and "severity" in df.columns:
    st.bar_chart(df['severity'].value_counts())
else:
    st.warning("No data to display in chart.")
