####################################################################################
#  ______    __              __             ______                     _
# /_  __/__ / /__ __ _  ___ / /_______ __  / __/ /________ ___ ___ _  (_)__  ___ _
#  / / / -_) / -_)  ' \/ -_) __/ __/ // / _\ \/ __/ __/ -_) _ `/  ' \/ / _ \/ _ `/
# /_/  \__/_/\__/_/_/_/\__/\__/_/  \_, / /___/\__/_/  \__/\_,_/_/_/_/_/_//_/\_, /
#                                 /___/                                    /___/
####################################################################################
#  Name:        idrac9TelemetrySTreaming.py
#  Description: Script for pulling iDRAC9 sensor data via Redfish SSE 
#               and inserting that data to an InfluxDB database
#  Version:     07
#  Author:      Jonas Werner
#  URL:         http://jonamiki.com
####################################################################################


import json
import requests
import os
import glob
import time
from datetime import datetime
from influxdb import InfluxDBClient
from requests.auth import HTTPBasicAuth

# Set environment variables
idrac           = "192.168.0.120" # If certificate is used an FQDN is required rather than the IP
idracUser       = "root"
idracPass       = "calvin"
influxDBHost    = os.environ['influxDBHost']
influxDBPort    = os.environ['influxDBPort']
influxDBUser    = os.environ['influxDBUser']
influxDBPass    = os.environ['influxDBPass']
influxDBName    = os.environ['influxDBName']
device          = "mitaR740"    # Description of the telemetry data source
location        = "Mita CSC"    # Description of the location the device is located in



def influxDBconnect():
    influxDBConnection = InfluxDBClient(influxDBHost, influxDBPort, influxDBUser, influxDBPass, influxDBName)
    return influxDBConnection


def influxDBwrite(device, location, sensorName, sensorValue):
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    measurementData = [
        {
            "measurement": device,
            "tags": {
                "device": device,
                "location": location
            },
            "time": timestamp,
            "fields": {
                sensorName: sensorValue
            }
        }
    ]
    influxDBConnection.write_points(measurementData, time_precision='ms')


influxDBConnection = influxDBconnect()


r = requests.get('https://%s/redfish/v1/SSE?$filter=EventFormatType eq MetricReport' %
                    idrac,
                    # verify  = '/home/jonas/telemetry/python/certs/cert.pem', # Use if SSL cert for iDRAC is available
                    verify=False,
                    stream=True,
                    auth=(idracUser, idracPass))




for line in r.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        if '{' in decoded_line:
            decoded_line = decoded_line.strip('data: ')
            metrics = json.loads(decoded_line)
            cpuOneCore = 0
            cpuTwoCore = 0

            seqNum      = metrics['ReportSequence']
            readings    = metrics['MetricValues']

            print("Report sequence number: %s ##########################################" % seqNum)

            for entry in readings:
                # print("%s" % entry)
                label = entry['Oem']['Dell']['Label']
                value = entry['MetricValue']

                if "CPU1" in label:
                    label = "CPU1_Core%s" % cpuOneCore
                    cpuOneCore += 1
                if "CPU2" in label:
                    label = "CPU2_Core%s" % cpuTwoCore
                    cpuTwoCore += 1

                print("%s: %s" % (label, value))

                influxDBwrite(device, location, label, value)

