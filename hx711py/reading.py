#!/usr/bin/env python3
import subprocess
import sys
import errno
import os
import json
import time

import RPi.GPIO as GPIO
from hx711 import HX711

class Reading:
    """Class for retrieving readings from devices."""

    def __init__(self, reference_unit=None):
        self.hx = HX711(5, 6)
        self.hx.set_reading_format("MSB", "MSB")
        if reference_unit:
            self.hx.set_reference_unit(float(reference_unit))
            print("HX Reference unit is ", self.hx.REFERENCE_UNIT)
        self.hx.reset()
        self.hx.tare()

        print("Tare done! Add weight now...")

    def get_readings(self):
        """Write the readings for the current context."""

        sensor_id = os.getenv('SENSOR_ID', '')
        UUID = os.environ.get('RESIN_DEVICE_UUID')[:7] # First seven chars of device UUID
        
        reading = {}
        try:
            val = self.hx.get_weight(5)
            
            if sensor_id:
                reading.update({"sensor_id": sensor_id}) 
            reading.update({"short_uuid": UUID})
            reading.update({"weight": val})

            self.hx.power_down()
            self.hx.power_up()

        except (KeyboardInterrupt, SystemExit):
            self.clean_and_exit()
        return reading


    def clean_and_exit(self):
        print("Cleaning...")

        GPIO.cleanup()
            
        print("Bye!")
        sys.exit()
