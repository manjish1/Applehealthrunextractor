# Applehealthrunextractor
This repo extracts run workouts from Apple health xml export file. You can calculate your weekly milage or do other analysis on it.

## How to use
- Go to Health app on your iPhone and export all health data.
- Unzip the downloaded file and copy the export.xml file to the folder for this repo
- Go to terminal and run this python file.
- It will create a csv file which has the start date of the week (Monday) and the total milage you ran from Monday to Sunday.

## Features
- Let's say you start a run from your watch and also Nike Run Club app at the same time, you do not want to skew the chart by counting it twice. Added a new feature which will remove the duplicate runs that are within 3 minutes start of each other. 
  
