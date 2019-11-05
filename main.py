import network
import utime
import json
from umqtt.robust import MQTTClient
from light import MQTTLight

with open("config.json", "r") as f:
    config = json.loads(f.read())

PIN = config["pin"] # Pin used to send data
PIXELS = config["pixels"] # Number of pixels connected
NETWORK_SSID = config["network_ssid"] # SSID of ap to connect to
NETWORK_PSK = config["network_psk"] # PSK for ap
CONNECT_TIMEOUT = config["connect_timeout"] # Timeout for wifi connection
DISABLE_AP = config["disable_ap"] # Flag to diable AP mode
HOST = config["host"] # IP address of MQTT host
CLIENT_NAME = config["client_name"] # Client name for MQTT, must be unique
STATE_TOPIC = config["state_topic"] # Topic to send ON/OFF state to
BRIGHTNESS_STATE_TOPIC = config["brightness_state_topic"] # Topic to send brightness state to
COLOR_STATE_TOPIC = config["color_state_topic"] # Topic to send color state to
COMMAND_TOPIC = config["command_topic"] # Topic to receive ON/OFF commands
BRIGHTNESS_TOPIC = config["brightness_topic"] # Topic to receive brightness commands
COLOR_TOPIC = config["color_topic"] # Topic to receive color commands
UPDATE_TOPIC = config["update_topic"] # Topic to receive requests to update light state

del config

# Set starting to true to avoid getting caught in a loop on startup
starting = True

# Initialise MQTT Client and Light before callback definition
client = MQTTClient(CLIENT_NAME, HOST)
neo = MQTTLight(client, PIN, PIXELS, STATE_TOPIC, BRIGHTNESS_STATE_TOPIC, COLOR_STATE_TOPIC)

def wifi_connect(network_ssid, network_psk, connect_timeout):
    '''
    Connect to configured wifi and disable AP if requested
    network_ssid: Network SSID (str)
    network_psk: Network PSK (str)
    connect_timeout: Connection timeout in ms (int)
    '''
    print("Checking WiFi")
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    if DISABLE_AP and ap_if.active():
        print("Disabling access point")
        ap_if.active(False)
    elif not DISABLE_AP:
        ap_if.active(True)

    if not sta_if.active():
        print("Activating station interface")
        sta_if.active(True)

    if not sta_if.isconnected():
        print("Connecting to Wifi", network_ssid)
        sta_if.connect(network_ssid, network_psk)
        then = utime.ticks_ms()
        while not sta_if.isconnected() and utime.ticks_ms() - then < connect_timeout:
            pass
        if sta_if.isconnected():
            print("Successfully connected to", network_ssid)
        else:
            print("Could not connect to WiFi, check network and config")
    else:
        print("Connected to", network_ssid)

def subcb(topic, msg):
    '''
    MQTT callback to set light and update Home Assistant
    '''
    global starting
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    # Respond to an ON/OFF command
    if topic == COMMAND_TOPIC:
        if msg == "ON":
            if neo.states["state"] != "ON":
                print("Turning On")
            neo.on()
        elif msg == "OFF":
            if neo.states["state"] != "OFF":
                print("Turning Off")
            neo.off()
    
    # Respond to brightness command
    elif topic == BRIGHTNESS_TOPIC:
        print("Setting brightness to:", msg)
        neo.set_brightness(int(msg))
    
    # Respond to color command
    elif topic == COLOR_TOPIC:
        print("Setting color to:", msg)
        color = [int(x) for x in msg.split(",")]
        neo.set_color(color)

    # Set Neopixel to last known state on startup
    elif starting:
        if topic == BRIGHTNESS_STATE_TOPIC:
            print("Old brightness:", msg)
            neo.states["brightness"] = int(msg)
        if topic == STATE_TOPIC:
            print("Old state:", msg)
            neo.states["state"] = msg
        if topic == COLOR_STATE_TOPIC:
            print("Old color:", msg)
            neo.states["color"] = [int(x) for x in msg.split(",")]
            neo.set_color(update=False)
            starting = False

    # Update state on request
    elif topic == UPDATE_TOPIC:
        neo.update()

wifi_connect(NETWORK_SSID, NETWORK_PSK, CONNECT_TIMEOUT)

client.set_callback(subcb)
client.connect()

client.subscribe(COMMAND_TOPIC)
client.subscribe(BRIGHTNESS_TOPIC)
client.subscribe(COLOR_TOPIC)
client.subscribe(STATE_TOPIC)
client.subscribe(BRIGHTNESS_STATE_TOPIC)
client.subscribe(COLOR_STATE_TOPIC)

while True:
    client.wait_msg()