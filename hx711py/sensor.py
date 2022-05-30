#!/usr/bin/env python3
import sys
import errno
import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import paho.mqtt.client as mqtt
import socket
import threading
import requests

from reading import Reading


def mqtt_detect():
    
    # Use the supervisor api to get services
    # See https://www.balena.io/docs/reference/supervisor/supervisor-api/
    
    address = os.getenv('BALENA_SUPERVISOR_ADDRESS', '')
    api_key = os.getenv('BALENA_SUPERVISOR_API_KEY', '')
    app_name = os.getenv('BALENA_APP_NAME', '')

    url = "{0}/v2/applications/state?apikey={1}".format(address, api_key)

    try:
        r = requests.get(url).json()
    except Exception as e:
        print("Error looking for MQTT service: {0}".format(str(e)))
        return False
    else:
        services = r[app_name]['services'].keys()

        if "mqtt" in services:
            return True
        else:
            return False
    

class balenaSense():
    
    def __init__(self):
        self.sensor = Reading()
        #self.sensor = Reading(125)

    def sample(self):
        return self.sensor.get_readings()

# Simple webserver
def background_web(server_socket):
    balenasense = balenaSense()
    while True:
        # Wait for client connections
        client_connection, client_address = server_socket.accept()

        # Get the client request
        request = client_connection.recv(1024).decode()
        print(request)

        # Send HTTP response
        response = 'HTTP/1.0 200 OK\n\n'+ json.dumps(balenasense.sample())
        client_connection.sendall(response.encode())
        client_connection.close()



if __name__ == "__main__":

    mqtt_address = os.getenv('MQTT_ADDRESS', 'none')
    use_httpserver = os.getenv('ALWAYS_USE_HTTPSERVER', 0)
    publish_interval = os.getenv('MQTT_PUB_INTERVAL', '0.5')
    publish_topic = os.getenv('MQTT_PUB_TOPIC', 'sensors')
    
    try:
        interval = float(publish_interval)
    except Exception as e:
        print("Error converting MQTT_PUB_INTERVAL: Must be integer or float! Using default.")
        interval = 0.5
        
    if use_httpserver == "1":
        enable_httpserver = "True"
    else:
        enable_httpserver = "False"
    

    if mqtt_detect() and mqtt_address == "none":
        mqtt_address = "mqtt"

    if mqtt_address != "none":
        print("Starting mqtt client, publishing to {0}:1883".format(mqtt_address))
        print("Using MQTT publish interval: {0} sec(s)".format(interval))
        client = mqtt.Client()
        try:
            client.connect(mqtt_address, 1883, 60)
        except Exception as e:
            print("Error connecting to mqtt. ({0})".format(str(e)))
            mqtt_address = "none"
            enable_httpserver = "True"
        else:
            client.loop_start()
            balenasense = balenaSense()
    else:
        enable_httpserver = "True"

    if enable_httpserver == "True":
        SERVER_HOST = '0.0.0.0'
        SERVER_PORT = 7575

        # Create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(1)
        print("HTTP server listening on port {0}...".format(SERVER_PORT))

        t = threading.Thread(target=background_web, args=(server_socket,))
        t.start()
    
    
    #while True:
    #    balenasense = balenaSense()
    #    while True:
    #        print(balenasense.sample())
    #        time.sleep(interval)
    
    while True:
        if mqtt_address != "none":
            client.publish(publish_topic, json.dumps(balenasense.sample()))
        time.sleep(interval)
