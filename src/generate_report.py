import datetime as dt
import sys
import os
import matplotlib.pyplot as plt

from get_data import get_data

date_start = dt.date.fromisoformat(sys.argv[1])
date_end = dt.date.fromisoformat(sys.argv[2])

# Create date range from given dates
dates = []
i = date_start
while i <= date_end:
    dates.append(i)
    i += dt.timedelta(days=1)

print("Gathering data. This may take a while.")

df = get_data(dates)

# Below are all the report variables needed

week_number = dt.date.strftime(date_start, "%U")
date_start = dt.date.strftime(date_start, "%B %d, %Y")
date_end = dt.date.strftime(date_end, "%B %d, %Y")
max_avg_C = df['temp_max_C'].mean().round(1)
max_avg_F = df['temp_max_F'].mean().round(1)

hottest = df.groupby("volunteer_name").max(numeric_only=True).sort_values(
    "temp_max_C", ascending=False)[0:4]

v_hottest_1 = hottest.iloc[0].name
v_hottest_1_Tc = hottest.iloc[0]['temp_max_C'].round(1)
v_hottest_1_Tf = hottest.iloc[0]['temp_max_F'].round(1)

v_hottest_2 = hottest.iloc[1].name
v_hottest_2_Tc = hottest.iloc[1]['temp_max_C'].round(1)
v_hottest_2_Tf = hottest.iloc[1]['temp_max_F'].round(1)

v_hottest_3 = hottest.iloc[2].name
v_hottest_3_Tc = hottest.iloc[2]['temp_max_C'].round(1)
v_hottest_3_Tf = hottest.iloc[2]['temp_max_F'].round(1)

v_hottest_4 = hottest.iloc[3].name
v_hottest_4_Tc = hottest.iloc[3]['temp_max_C'].round(1)
v_hottest_4_Tf = hottest.iloc[3]['temp_max_F'].round(1)

coldest = df.groupby("volunteer_name").min(
    numeric_only=True).sort_values("temp_min_C")[0:4]

v_coldest_1 = coldest.iloc[0].name
v_coldest_1_Tc = coldest.iloc[0]['temp_min_C'].round(1)
v_coldest_1_Tf = coldest.iloc[0]['temp_min_F'].round(1)

v_coldest_2 = coldest.iloc[1].name
v_coldest_2_Tc = coldest.iloc[1]['temp_min_C'].round(1)
v_coldest_2_Tf = coldest.iloc[1]['temp_min_F'].round(1)

v_coldest_3 = coldest.iloc[2].name
v_coldest_3_Tc = coldest.iloc[2]['temp_min_C'].round(1)
v_coldest_3_Tf = coldest.iloc[2]['temp_min_F'].round(1)

v_coldest_4 = coldest.iloc[3].name
v_coldest_4_Tc = coldest.iloc[3]['temp_min_C'].round(1)
v_coldest_4_Tf = coldest.iloc[3]['temp_min_F'].round(1)

rainiest = df.groupby("volunteer_name").sum(numeric_only=True)[
    "precipitation_mm"].sort_values(ascending=False)

v_rainiest = rainiest.index[0]
v_rainiest_mm = rainiest[v_rainiest]

replacements = {
    "date_start": str(date_start),
    "date_end": str(date_end),
    "max_avg_C": str(max_avg_C),
    "max_avg_F": str(max_avg_F),
    "v_hottest_1": str(v_hottest_1),
    "v_hottest_1_Tc": str(v_hottest_1_Tc),
    "v_hottest_1_Tf": str(v_hottest_1_Tf),
    "v_hottest_2": str(v_hottest_2),
    "v_hottest_2_Tc": str(v_hottest_2_Tc),
    "v_hottest_2_Tf": str(v_hottest_2_Tf),
    "v_hottest_3": str(v_hottest_3),
    "v_hottest_3_Tc": str(v_hottest_3_Tc),
    "v_hottest_3_Tf": str(v_hottest_3_Tf),
    "v_hottest_4": str(v_hottest_4),
    "v_hottest_4_Tc": str(v_hottest_4_Tc),
    "v_hottest_4_Tf": str(v_hottest_4_Tf),
    "v_coldest_1": str(v_coldest_1),
    "v_coldest_1_Tc": str(v_coldest_1_Tc),
    "v_coldest_1_Tf": str(v_coldest_1_Tf),
    "v_coldest_2": str(v_coldest_2),
    "v_coldest_2_Tc": str(v_coldest_2_Tc),
    "v_coldest_2_Tf": str(v_coldest_2_Tf),
    "v_coldest_3": str(v_coldest_3),
    "v_coldest_3_Tc": str(v_coldest_3_Tc),
    "v_coldest_3_Tf": str(v_coldest_3_Tf),
    "v_coldest_4": str(v_coldest_4),
    "v_coldest_4_Tc": str(v_coldest_4_Tc),
    "v_coldest_4_Tf": str(v_coldest_4_Tf),
    "v_rainiest": str(v_rainiest),
    "v_rainiest_mm": str(v_rainiest_mm)
}

# Generate report using template

with open("reports/REPORT_TEMPLATE.md", "r", encoding="utf-8") as f:
    content = f.read()

for key, value in replacements.items():
    content = content.replace(f"{{{{{key}}}}}", value)

folder_name = f"Report W{week_number}"

os.mkdir(f"reports/{folder_name}")

with open(f"reports/{folder_name}/report.md", "x") as f:
    f.write(content)

print(f"Report saved in reports/{folder_name}.")
print("Generating plot...")

# Generate plot

plt.style.use('seaborn-v0_8-poster')

t = df.groupby("volunteer_name").mean(numeric_only=True).index
F = df.groupby("volunteer_name").mean(numeric_only=True)["temp_max_F"]
C = df.groupby("volunteer_name").mean(numeric_only=True)["temp_max_C"]
F_avg = sum(F)/len(F)

fig, ax1 = plt.subplots()
ax1.set_ylabel('Temperature [F]')
markerline, stemlines, baseline = ax1.stem(t, F, bottom=F_avg)
markerline.set_markerfacecolor("black")
markerline.set_markersize(8)
ax1.tick_params(axis='y')
ax1.tick_params(axis='x', labelrotation=90, direction="out", length=10, pad=5)
ax1.grid(axis="y", which='both')
ax1.grid(axis="x", linestyle="--")
ax1.set_title("Average Maximum Temperatures Across the Week")
plt.tight_layout()

# Save plot to report folder

plt.savefig(f"reports/{folder_name}/report.png")

print(f"Done. Plot saved in reports/{folder_name}.")
