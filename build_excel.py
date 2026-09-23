import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.utils import get_column_letter

FONT_NAME = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(name=FONT_NAME, bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(name=FONT_NAME, bold=True, size=16, color="1F4E78")
SUBTITLE_FONT = Font(name=FONT_NAME, italic=True, size=10, color="595959")
KPI_LABEL_FONT = Font(name=FONT_NAME, size=10, color="595959")
KPI_VALUE_FONT = Font(name=FONT_NAME, bold=True, size=20, color="1F4E78")
BODY_FONT = Font(name=FONT_NAME, size=10)
thin = Side(style="thin", color="D9D9D9")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()


def style_header_row(ws, row=1, ncols=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")


def autosize(ws, ncols, width=16):
    for c in range(1, ncols + 1):
        ws.column_dimensions[get_column_letter(c)].width = width


def write_df(ws, df, start_row=1, start_col=1):
    for j, col in enumerate(df.columns):
        ws.cell(row=start_row, column=start_col + j, value=col)
    for i, row in enumerate(df.itertuples(index=False)):
        for j, val in enumerate(row):
            ws.cell(row=start_row + 1 + i, column=start_col + j, value=val)
    style_header_row(ws, row=start_row, ncols=len(df.columns))
    for r in range(start_row + 1, start_row + 1 + len(df)):
        for c in range(start_col, start_col + len(df.columns)):
            ws.cell(row=r, column=c).border = BORDER
            ws.cell(row=r, column=c).font = BODY_FONT
    return start_row + 1 + len(df)  # next free row



mrr_df = pd.read_csv("exports/mrr_by_month.csv")
churn_df = pd.read_csv("exports/churn_by_month.csv")
plan_df = pd.read_csv("exports/plan_summary.csv")
channel_df = pd.read_csv("exports/channel_revenue.csv")
ltv_df = pd.read_csv("exports/ltv_by_plan.csv")
risk_df = pd.read_csv("exports/at_risk_customers.csv")

ws_mrr = wb.active
ws_mrr.title = "MRR_by_Month"
last_row = write_df(ws_mrr, mrr_df[["month", "mrr"]])
autosize(ws_mrr, 3)

ws_mrr.cell(row=1, column=3, value="mom_growth_pct")
style_header_row(ws_mrr, row=1, ncols=3)
for r in range(2, last_row):
    if r == 2:
        ws_mrr.cell(row=r, column=3, value=None)
    else:
        ws_mrr.cell(row=r, column=3, value=f"=IFERROR((B{r}-B{r-1})/B{r-1},\"\")")
    ws_mrr.cell(row=r, column=2).number_format = "$#,##0"
    ws_mrr.cell(row=r, column=3).number_format = "0.0%"
    ws_mrr.cell(row=r, column=3).border = BORDER
    ws_mrr.cell(row=r, column=3).font = BODY_FONT

ws_churn = wb.create_sheet("Churn_by_Month")
last_row = write_df(ws_churn, churn_df)
autosize(ws_churn, 4)
for r in range(2, last_row):
    ws_churn.cell(row=r, column=4).number_format = "0.00\"%\""

ws_plan = wb.create_sheet("Plan_Summary")
last_row = write_df(ws_plan, plan_df)
autosize(ws_plan, 4)
for r in range(2, last_row):
    ws_plan.cell(row=r, column=4).number_format = "$#,##0.00"

ws_channel = wb.create_sheet("Channel_Revenue")
last_row = write_df(ws_channel, channel_df)
autosize(ws_channel, 2, width=22)
for r in range(2, last_row):
    ws_channel.cell(row=r, column=2).number_format = "$#,##0"

ws_ltv = wb.create_sheet("LTV_by_Plan")
last_row = write_df(ws_ltv, ltv_df)
autosize(ws_ltv, 6)
for r in range(2, last_row):
    ws_ltv.cell(row=r, column=4).number_format = "0.0%"
    ws_ltv.cell(row=r, column=5).number_format = "$#,##0.00"
    ws_ltv.cell(row=r, column=6).number_format = "$#,##0.00"

ws_risk = wb.create_sheet("At_Risk_Customers")
last_row = write_df(ws_risk, risk_df)
autosize(ws_risk, 6, width=18)
for r in range(2, last_row):
    ws_risk.cell(row=r, column=4).number_format = "$#,##0"


ws = wb.create_sheet("Dashboard", 0)
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 3
for col, w in zip("BCDEFGH", [22, 22, 22, 22, 22, 22, 22]):
    ws.column_dimensions[col].width = w

ws["B2"] = "SaaS Business Dashboard"
ws["B2"].font = TITLE_FONT
ws["B3"] = "Synthetic dataset · Jan 2024 - Dec 2025 · Source: notebook exports + SQL queries"
ws["B3"].font = SUBTITLE_FONT

n_mrr_rows = len(mrr_df)
last_mrr_row = 1 + n_mrr_rows  
n_churn_rows = len(churn_df)
last_churn_row = 1 + n_churn_rows

kpis = [
    ("Current MRR", f"=MRR_by_Month!B{last_mrr_row}", "$#,##0"),
    ("Active Customers", f"=Churn_by_Month!B{last_churn_row}", "#,##0"),
    ("Avg Monthly Churn Rate", f"=AVERAGE(Churn_by_Month!D2:D{last_churn_row})", "0.00\"%\""),
    ("Total Customers (Plan_Summary)", f"=SUM(Plan_Summary!B2:B{1+len(plan_df)})", "#,##0"),
]

start_col = 2
row_label, row_value = 5, 6
for i, (label, formula, numfmt) in enumerate(kpis):
    col = start_col + i * 2
    cell_label = ws.cell(row=row_label, column=col, value=label)
    cell_label.font = KPI_LABEL_FONT
    ws.merge_cells(start_row=row_label, start_column=col, end_row=row_label, end_column=col + 1)
    cell_val = ws.cell(row=row_value, column=col, value=formula)
    cell_val.font = KPI_VALUE_FONT
    cell_val.number_format = numfmt
    ws.merge_cells(start_row=row_value, start_column=col, end_row=row_value, end_column=col + 1)

ws["B9"] = "MRR Trend"
ws["B9"].font = Font(name=FONT_NAME, bold=True, size=12, color="1F4E78")
chart1 = LineChart()
chart1.title = None
chart1.y_axis.title = "MRR ($)"
chart1.x_axis.title = "Month"
data = Reference(ws_mrr, min_col=2, min_row=1, max_row=last_mrr_row)
cats = Reference(ws_mrr, min_col=1, min_row=2, max_row=last_mrr_row)
chart1.add_data(data, titles_from_data=True)
chart1.set_categories(cats)
chart1.height, chart1.width = 8, 16
ws.add_chart(chart1, "B10")

ws["J9"] = "Churn Rate Trend (%)"
ws["J9"].font = Font(name=FONT_NAME, bold=True, size=12, color="1F4E78")
chart2 = LineChart()
chart2.y_axis.title = "Churn rate (%)"
chart2.x_axis.title = "Month"
data2 = Reference(ws_churn, min_col=4, min_row=1, max_row=last_churn_row)
cats2 = Reference(ws_churn, min_col=1, min_row=2, max_row=last_churn_row)
chart2.add_data(data2, titles_from_data=True)
chart2.set_categories(cats2)
chart2.height, chart2.width = 8, 16
ws.add_chart(chart2, "J10")

ws["B28"] = "Active MRR by Plan"
ws["B28"].font = Font(name=FONT_NAME, bold=True, size=12, color="1F4E78")
chart3 = BarChart()
chart3.type = "col"
chart3.y_axis.title = "Avg MRR ($)"
data3 = Reference(ws_plan, min_col=4, min_row=1, max_row=1 + len(plan_df))
cats3 = Reference(ws_plan, min_col=1, min_row=2, max_row=1 + len(plan_df))
chart3.add_data(data3, titles_from_data=True)
chart3.set_categories(cats3)
chart3.height, chart3.width = 8, 16
ws.add_chart(chart3, "B29")

ws["J28"] = "Revenue by Acquisition Channel"
ws["J28"].font = Font(name=FONT_NAME, bold=True, size=12, color="1F4E78")
chart4 = BarChart()
chart4.type = "col"
chart4.y_axis.title = "Revenue ($)"
data4 = Reference(ws_channel, min_col=2, min_row=1, max_row=1 + len(channel_df))
cats4 = Reference(ws_channel, min_col=1, min_row=2, max_row=1 + len(channel_df))
chart4.add_data(data4, titles_from_data=True)
chart4.set_categories(cats4)
chart4.height, chart4.width = 8, 16
ws.add_chart(chart4, "J29")

note = ws.cell(row=48, column=2, value=(
    "Note: all figures are computed live from the data on the other tabs "
    "(MRR_by_Month, Churn_by_Month, Plan_Summary, Channel_Revenue, LTV_by_Plan, "
    "At_Risk_Customers). Edit those tabs and the KPIs/charts above recalculate."
))
note.font = Font(name=FONT_NAME, italic=True, size=9, color="808080")
ws.merge_cells(start_row=48, start_column=2, end_row=48, end_column=9)

wb.save("SaaS_Dashboard.xlsx")
print("Saved SaaS_Dashboard.xlsx")
