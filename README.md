# TE-Prometheus

## Project Overview
There is only one python file for this project - main-py.py
The objective is to read the measurements from desired tests running in Thousand Eyes, and export them to Prometheus in a format that it understands.

### What this project does not do
This project does not show how the output file that contains all the measurements fetched at a given time, is exposed to prometheus on HTTP

### What this project does, in simple terms
There are two sections in this code - 
1. Fetching Data from Thousand Eyes
2. Exporting this Data to Prometheus Format

#### Fetching Data from Thousand Eyes
1. Read all the tests in Thousand Eyes
2. Filter the tests based on some criteria. In this project, the criteria is to look at the test name and look for "GIS" as first three characters.
3. Store the test IDs of these filtered tests
4. Get the measurements of each test based on the test ID stored from Step-3
5. Store all the measurements in a python dictionary. Later save this in a pickle file (just for troubleshooting purpose).

#### Exporting this Data to Prometheus Format
We chose "Guage" metric type for our use case. (Explore other metric types from https://prometheus.io/docs/concepts/metric_types/
1. Define the labels we want to use for each measurement.
2. Add data to the labels for each measurement. This is not the measurement data. This is meta data that helps you in designing good queries.
3. Add measurement data to each measurement.
4. Export this in a format that Prometheus understands.
5. Save this exported huge text string (that's what it really is) to a file

### Logging
This code also implements a simple python logger that logs all the export times to a simple file - main-py.log

Let me know if any part is unclear in this code.
