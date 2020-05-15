####################################################################################
#  ______    __              __             ______                     _
# /_  __/__ / /__ __ _  ___ / /_______ __  / __/ /________ ___ ___ _  (_)__  ___ _
#  / / / -_) / -_)  ' \/ -_) __/ __/ // / _\ \/ __/ __/ -_) _ `/  ' \/ / _ \/ _ `/
# /_/  \__/_/\__/_/_/_/\__/\__/_/  \_, / /___/\__/_/  \__/\_,_/_/_/_/_/_//_/\_, /
#                                 /___/                                    /___/
####################################################################################
#  Name:        idrac9TelemetrySTreaming-basic.py
#  Description: Script for pulling iDRAC9 sensor data via Redfish SSE 
#               and inserting that data to an InfluxDB database
#  Version:     01
#  Author:      Jonas Werner
#  URL:         http://jonamiki.com
####################################################################################


import json
import requests
import os
import glob
import time
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Set environment variables
idrac           = "192.168.0.120" # If certificate is used an FQDN is required rather than the IP
idracUser       = "root"
idracPass       = "calvin"


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
                print("%s" % entry)
