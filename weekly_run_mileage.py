import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

def parse_health_export_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    all_workouts = root.findall('Workout')
    print(f"Total workouts found: {len(all_workouts)}")

    potential_workouts = []

    for workout in all_workouts:
        if workout.attrib.get('workoutActivityType') == 'HKWorkoutActivityTypeRunning':
            start = workout.attrib.get('startDate')
            end = workout.attrib.get('endDate')
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
            except Exception:
                print(f"Skipping malformed date: {start} or {end}")
                continue

            distance_mi = None
            for stat in workout.findall('WorkoutStatistics'):
                if stat.attrib.get('type') == 'HKQuantityTypeIdentifierDistanceWalkingRunning':
                    distance = stat.attrib.get('sum')
                    unit = stat.attrib.get('unit')
                    if distance and unit:
                        try:
                            distance_mi = float(distance)
                            if unit == 'km':
                                distance_mi *= 0.621371
                            elif unit != 'mi':
                                print(f"Unknown distance unit '{unit}' skipped.")
                                distance_mi = None
                        except ValueError:
                            print(f"Malformed distance value: {distance}")
                    break

            if distance_mi is not None:
                potential_workouts.append({
                    'startDate': start_dt,
                    'endDate': end_dt,
                    'distance': distance_mi
                })

    # Sort workouts by start time
    potential_workouts.sort(key=lambda x: x['startDate'])
    filtered_workouts = []

    for current in potential_workouts:
        keep = True
        for i, existing in enumerate(filtered_workouts):
            if (current['startDate'] < existing['endDate']) and (current['endDate'] > existing['startDate']):
                if current['distance'] > existing['distance']:
                    filtered_workouts[i] = current
                keep = False
                break
        if keep:
            filtered_workouts.append(current)

    print(f"Running workouts after overlap filtering: {len(filtered_workouts)}")
    if filtered_workouts:
        print("Sample running workouts:")
        for w in filtered_workouts[:5]:
            print(f"  {w['startDate'].date()} {w['startDate'].time()} - {w['distance']:.2f} mi")

    return filtered_workouts

def get_week_start(date):
    return date - timedelta(days=date.weekday())

def aggregate_weekly_mileage(run_workouts):
    mileage_by_week = defaultdict(float)
    for workout in run_workouts:
        week_start = get_week_start(workout['startDate']).date()
        mileage_by_week[week_start] += workout['distance']
    sorted_weeks = sorted(mileage_by_week.items())
    df = pd.DataFrame(sorted_weeks, columns=['Week Start', 'Total Mileage'])
    return df

def export_weekly_mileage(file_path, output_csv=None, output_chart=None, output_raw_csv=None):
    workouts = parse_health_export_xml(file_path)
    weekly_df = aggregate_weekly_mileage(workouts)

    if output_csv:
        weekly_df.to_csv(output_csv, index=False)
        print(f"Exported weekly mileage to: {output_csv}")

    if output_raw_csv:
        raw_df = pd.DataFrame(workouts)
        raw_df = raw_df.rename(columns={'startDate': 'Start Date', 'endDate': 'End Date', 'distance': 'Distance (mi)'})
        raw_df.to_csv(output_raw_csv, index=False)
        print(f"Exported raw run data to: {output_raw_csv}")

    if output_chart:
        plt.figure(figsize=(16, 6))
        bars = plt.bar(weekly_df["Week Start"], weekly_df["Total Mileage"], width=5)
        for bar in bars:
            height = bar.get_height()
            plt.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
        plt.title("WEEKLY MILEAGE", fontsize=16, weight='bold')
        plt.ylabel("Miles")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_chart, dpi=150)
        plt.close()
        print(f"Chart saved to: {output_chart}")

    return weekly_df
