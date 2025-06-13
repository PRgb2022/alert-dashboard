import pandas as pd
import sqlite3

df = pd.read_csv("alerts.csv")
conn = sqlite3.connect("alerts.db")
df.to_sql("alerts", conn, if_exists="replace", index=False)
conn.close()
