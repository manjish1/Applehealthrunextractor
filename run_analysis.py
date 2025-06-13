from weekly_run_mileage import export_weekly_mileage

# Export weekly mileage and chart
df = export_weekly_mileage(
    "export.xml",
    output_csv="weekly_mileage.csv",
    output_chart="weekly_mileage_chart.png",
    output_raw_csv="raw_runs.csv"
)

