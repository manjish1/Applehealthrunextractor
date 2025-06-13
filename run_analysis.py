from weekly_run_mileage import export_weekly_mileage

# Replace with the correct path if your export.xml is elsewhere
df = export_weekly_mileage("export.xml", output_csv="weekly_mileage.csv")

print(df)
