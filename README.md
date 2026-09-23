# saas-analytics

A comprehensive, end-to-end business intelligence and data analytics project modeling a subscription-based Software-as-a-Service (SaaS) company. This repository features data generation pipelines, advanced relational database analysis (MySQL & SQLite), Jupyter notebook exploration, and an automated, formula-driven executive KPI dashboard in Excel.

## Business Questions Answered

* **Revenue Growth Optimization:** What are our actual Month-over-Month (MoM) metrics for Monthly Recurring Revenue (MRR) and Annual Recurring Revenue (ARR)?
* **Customer Retention Lift:** What do the customer churn dynamics and subscription lifecycles look like when tracked across monthly acquisition cohorts?
* **Unit Economics Performance:** What is the precise financial health ratio between our Customer Lifetime Value (CLV) and Customer Acquisition Cost (CAC)?
* **Plan Tier Valuation:** Which subscription pricing tiers (Basic, Pro, Enterprise) drive the highest transactional volumes vs. total platform revenue?
* **Account Health Analysis:** How can we programmatically segment corporate subscribers to isolate at-risk accounts before they contract or churn?

## Technical Toolkit & Stack

* **Data Engineering & Simulation:** A custom `generate_data.py` script creating mock transactional, subscription, and user session logs.
* **Relational Database Analytics:** Complex MySQL and SQLite architectures (`analysis_queries_mysql.sql`) executing metrics like cohort retention grids, rolling MRR windows, and run-rate aggregates.
* **Exploratory Data Analysis:** A `SaaS_Analysis.ipynb` workbook leveraging `pandas` and `matplotlib` to isolate customer lifecycles and product trends.
* **Automated Dashboard Generation:** Python logic (`openpyxl`) engineering a structured executive dashboard (`SaaS_Dashboard.xlsx`) built completely with dynamic, cross-referencing spreadsheet formulas.

## Project Structure

```text
├── charts/                 
├── data/                   
├── exports/                
├── notebook/
│   └── SaaS_Analysis.ipynb 
├── sql/
│   ├── saas_mysql_dump.sql        
│   └── analysis_queries_mysql.sql 
├── Python/
│   ├── generate_data.py           
│   ├── build_database.py          
│   └── build_excel.py             
├── SaaS_Dashboard.xlsx     
└── README.md               
```

## How to Run It

### 📊 Option 1: Excel Dashboard
Simply download and double-click the `SaaS_Dashboard.xlsx` file. Navigate to the **Dashboard** tab to interact with pre-calculated, live KPIs, charts, and financial indicators.

### ⚙️ Option 2: SQL Analytics (MySQL / MySQL Workbench)
1. Launch MySQL Workbench and create a workspace database connection.
2. Open and run `saas_mysql_dump.sql` to generate the system tables and seed records.
3. Open `analysis_queries_mysql.sql` to execute advanced financial calculations (MRR, Cohorts, CLV).

### 🐍 Option 3: Python Data Pipeline (Jupyter)
1. Download or clone this project and move inside the root folder.
2. Install the necessary data stack dependencies:
   ```bash
   pip install pandas matplotlib openpyxl jupyter
   ```
3. Run the interactive workspace:
   ```bash
   jupyter notebook
   ```
4. Open `SaaS_Analysis.ipynb` and execute the blocks to examine the pipeline directly.


