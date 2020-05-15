# idrac9-telemetry-streaming
Script for pulling Redfish SSE telemetry stream from 14G server and saving into an InfluxDB

# Environment
Environment variables for the InfluxDB are set prior to running the script. The script can also be modified to hold these varilables directly. 

# Example of setting required variables:
- export influxDBHost="10.6.28.31"
- export influxDBPort="8086"
- export influxDBUser="root"
- export influxDBPass="pass"
- export influxDBName="telemetry"
