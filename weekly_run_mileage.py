import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

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
            # Check for overlap: start < other.end and end > other.start
            if (current['startDate'] < existing['endDate']) and (current['endDate'] > existing['startDate']):
                if current['distance'] > existing['distance']:
                    filtered_workouts[i] = current  # Replace with longer distance
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

def export_weekly_mileage(file_path, output_csv=None):
    workouts = parse_health_export_xml(file_path)
    weekly_df = aggregate_weekly_mileage(workouts)
    if output_csv:
        weekly_df.to_csv(output_csv, index=False)
        print(f"Exported weekly mileage to: {output_csv}")
    return weekly_df
