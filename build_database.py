"""Loads the generated CSVs into a single SQLite database: saas.db"""
import sqlite3
import pandas as pd

conn = sqlite3.connect("saas.db")

customers = pd.read_csv("data/customers.csv")
subscriptions = pd.read_csv("data/subscriptions.csv")
usage = pd.read_csv("data/usage.csv")
payments = pd.read_csv("data/payments.csv")

customers.to_sql("customers", conn, if_exists="replace", index=False)
subscriptions.to_sql("subscriptions", conn, if_exists="replace", index=False)
usage.to_sql("usage", conn, if_exists="replace", index=False)
payments.to_sql("payments", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_sub_cust ON subscriptions(customer_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_cust ON usage(customer_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_pay_cust ON payments(customer_id)")
conn.commit()

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables created:", tables)
conn.close()
