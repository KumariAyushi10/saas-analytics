import random
import numpy as np
import pandas as pd
from datetime import date, timedelta
from faker import Faker

random.seed(42)
np.random.seed(42)
fake = Faker()
Faker.seed(42)

N_CUSTOMERS = 600
START_MONTH = date(2024, 1, 1)
N_MONTHS = 24  

PLANS = {
    "Starter":    {"price": 29,  "weight": 0.45},
    "Growth":     {"price": 99,  "weight": 0.35},
    "Enterprise": {"price": 299, "weight": 0.20},
}
INDUSTRIES = ["E-commerce", "FinTech", "Healthcare", "EdTech", "Marketing",
              "Real Estate", "Manufacturing", "Media", "Logistics", "SaaS/Tech"]
COUNTRIES = ["USA", "United Kingdom", "India", "Canada", "Germany",
             "Australia", "France", "Brazil", "Singapore", "Netherlands"]
CHANNELS = ["Organic Search", "Paid Ads", "Referral", "Content Marketing", "Outbound Sales", "Partner"]

def month_add(d: date, n: int) -> date:
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)

months = [month_add(START_MONTH, i) for i in range(N_MONTHS)]


customers = []
for i in range(1, N_CUSTOMERS + 1):
    signup_month_idx = int(np.random.beta(1.6, 2.2) * (N_MONTHS - 1))  
    signup_date = months[signup_month_idx]
    plan = random.choices(list(PLANS.keys()), weights=[p["weight"] for p in PLANS.values()])[0]
    customers.append({
        "customer_id": f"CUST{i:04d}",
        "company_name": fake.company(),
        "industry": random.choice(INDUSTRIES),
        "country": random.choice(COUNTRIES),
        "employee_size": random.choice([1, 5, 10, 25, 50, 100, 250, 500, 1000]),
        "acquisition_channel": random.choice(CHANNELS),
        "signup_date": signup_date.isoformat(),
        "initial_plan": plan,
    })
customers_df = pd.DataFrame(customers)


BASE_HAZARD = {"Starter": 0.045, "Growth": 0.028, "Enterprise": 0.014}

subscriptions = []
usage_rows = []
payments = []
sub_counter = 1
pay_counter = 1

for c in customers:
    cust_id = c["customer_id"]
    signup_idx = months.index(date.fromisoformat(c["signup_date"]))
    plan = c["initial_plan"]
    plan_price = PLANS[plan]["price"]
    active = True
    churn_month_idx = None

    for m_idx in range(signup_idx, N_MONTHS):
        if not active:
            break
        cur_month = months[m_idx]
        tenure = m_idx - signup_idx

        
        if tenure == 6 and plan != "Enterprise" and random.random() < 0.18:
            plan = "Growth" if plan == "Starter" else "Enterprise"
            plan_price = PLANS[plan]["price"]

        
        base_logins = {"Starter": 8, "Growth": 20, "Enterprise": 45}[plan]
        engagement_noise = np.random.normal(1.0, 0.35)
        logins = max(0, int(base_logins * engagement_noise))
        active_seats = max(1, int(c["employee_size"] * 0.15 * np.random.uniform(0.5, 1.3)))
        support_tickets = np.random.poisson(0.6 if plan == "Enterprise" else 0.3)
        nps = int(np.clip(np.random.normal(40 if logins > base_logins*0.6 else 10, 25), -100, 100))

        usage_rows.append({
            "customer_id": cust_id,
            "month": cur_month.isoformat(),
            "logins": logins,
            "active_seats": active_seats,
            "support_tickets": support_tickets,
            "nps_score": nps,
            "plan_at_time": plan,
        })

        
        payments.append({
            "payment_id": f"PAY{pay_counter:06d}",
            "customer_id": cust_id,
            "month": cur_month.isoformat(),
            "amount": plan_price,
            "status": "paid" if random.random() > 0.02 else "failed",
        })
        pay_counter += 1

        
        hazard = BASE_HAZARD[plan]
        if logins < base_logins * 0.4:
            hazard *= 2.2
        if nps < 0:
            hazard *= 1.6
        hazard *= max(0.6, 1 - tenure * 0.01)  

        if tenure >= 1 and random.random() < hazard:
            active = False
            churn_month_idx = m_idx

    end_month = months[churn_month_idx] if churn_month_idx is not None else None
    subscriptions.append({
        "subscription_id": f"SUB{sub_counter:05d}",
        "customer_id": cust_id,
        "plan": plan,
        "mrr": plan_price,
        "start_date": c["signup_date"],
        "end_date": end_month.isoformat() if end_month else None,
        "status": "churned" if end_month else "active",
    })
    sub_counter += 1

subscriptions_df = pd.DataFrame(subscriptions)
usage_df = pd.DataFrame(usage_rows)
payments_df = pd.DataFrame(payments)

customers_df.to_csv("data/customers.csv", index=False)
subscriptions_df.to_csv("data/subscriptions.csv", index=False)
usage_df.to_csv("data/usage.csv", index=False)
payments_df.to_csv("data/payments.csv", index=False)

print("customers:", len(customers_df))
print("subscriptions:", len(subscriptions_df))
print("usage rows:", len(usage_df))
print("payments:", len(payments_df))
print("churned customers:", (subscriptions_df.status == "churned").sum())
