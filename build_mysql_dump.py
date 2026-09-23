"""
Builds saas_mysql_dump.sql — a MySQL-compatible script that creates the
`saas` database, creates the 4 tables, and inserts all the rows.
Run this once inside MySQL Workbench to set up the database.
"""
import pandas as pd

customers = pd.read_csv("data/customers.csv")
subscriptions = pd.read_csv("data/subscriptions.csv")
usage = pd.read_csv("data/usage.csv")
payments = pd.read_csv("data/payments.csv")

BATCH = 500  # rows per INSERT statement, keeps statements a reasonable size

def sql_str(v):
    if pd.isna(v):
        return "NULL"
    return "'" + str(v).replace("\\", "\\\\").replace("'", "''") + "'"

def sql_val(v):
    if pd.isna(v):
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return sql_str(v)

def df_to_inserts(df, table, columns, out):
    cols_sql = ", ".join(f"`{c}`" for c in columns)
    rows = df[columns].values.tolist()
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        values_sql = []
        for row in chunk:
            vals = ", ".join(sql_val(v) for v in row)
            values_sql.append(f"({vals})")
        out.write(f"INSERT INTO `{table}` ({cols_sql}) VALUES\n")
        out.write(",\n".join(values_sql))
        out.write(";\n\n")

with open("saas_mysql_dump.sql", "w") as out:
    out.write("-- ============================================================\n")
    out.write("-- SaaS demo database - MySQL version\n")
    out.write("-- Run this whole script in MySQL Workbench (File > Run SQL Script,\n")
    out.write("-- or select-all + Execute) to create and populate the database.\n")
    out.write("-- ============================================================\n\n")

    out.write("DROP DATABASE IF EXISTS saas;\n")
    out.write("CREATE DATABASE saas;\n")
    out.write("USE saas;\n\n")

    out.write("""CREATE TABLE customers (
    customer_id          VARCHAR(10) PRIMARY KEY,
    company_name         VARCHAR(255) NOT NULL,
    industry              VARCHAR(50),
    country               VARCHAR(50),
    employee_size         INT,
    acquisition_channel   VARCHAR(50),
    signup_date           DATE,
    initial_plan          VARCHAR(20)
);\n\n""")

    out.write("""CREATE TABLE subscriptions (
    subscription_id  VARCHAR(10) PRIMARY KEY,
    customer_id      VARCHAR(10),
    plan             VARCHAR(20),
    mrr              DECIMAL(10,2),
    start_date       DATE,
    end_date         DATE NULL,
    status           VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);\n\n""")

    out.write("""CREATE TABLE `usage_data` (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    customer_id       VARCHAR(10),
    month             DATE,
    logins            INT,
    active_seats      INT,
    support_tickets   INT,
    nps_score         INT,
    plan_at_time      VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);\n\n""")

    out.write("""CREATE TABLE payments (
    payment_id    VARCHAR(10) PRIMARY KEY,
    customer_id   VARCHAR(10),
    month         DATE,
    amount        DECIMAL(10,2),
    status        VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);\n\n""")

    out.write("-- ---------------- data ----------------\n\n")

    out.write("-- customers\n")
    df_to_inserts(customers, "customers",
                  ["customer_id", "company_name", "industry", "country",
                   "employee_size", "acquisition_channel", "signup_date", "initial_plan"], out)

    out.write("-- subscriptions\n")
    df_to_inserts(subscriptions, "subscriptions",
                  ["subscription_id", "customer_id", "plan", "mrr",
                   "start_date", "end_date", "status"], out)

    out.write("-- usage\n")
    df_to_inserts(usage, "usage_data",
                  ["customer_id", "month", "logins", "active_seats",
                   "support_tickets", "nps_score", "plan_at_time"], out)

    out.write("-- payments\n")
    df_to_inserts(payments, "payments",
                  ["payment_id", "customer_id", "month", "amount", "status"], out)

    out.write("CREATE INDEX idx_sub_cust ON subscriptions(customer_id);\n")
    out.write("CREATE INDEX idx_usage_cust ON `usage_data`(customer_id);\n")
    out.write("CREATE INDEX idx_pay_cust ON payments(customer_id);\n")

print("Wrote saas_mysql_dump.sql")
