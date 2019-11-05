# Micropython-HASS-Neopixel-MQTT-Light
Implementation of a Home Assistant compliant MQTT Light with Neopixels and MicroPython

This code has been tested on a NodeMCU esp8266 board, it will likely run on other WiFi enabled MicroPython boards.

## MicroPython Setup

Edit `config.json` to match your setup, each config variable is explained below

```
pin: GPIO Pin connected to DIN on Neopixels
pixels: Number of Neopixels connected
network_ssid: SSID of WiFi network to connect to
network_psk: Password of WiFi network
connect_timeout: Timeout to wait for network connection
host: IP Address of MQTT server to connect to
client_name: Unique name for Neopixel controller for MQTT
state_topic: MQTT state topic
brightness_state_topic: MQTT Brightness State topic
color_state_topic: MQTT Color state topic
brightness_topic: MQTT Brightness command topic
color_topic: MQTT Color command topic
command_topic: MQTT State command topic
update_topic: MQTT Update topic
```

Copy `config.json` `main.py` and `light.py` to your MicroPython board.

## Home Assistant Setup

Example MQTT light setup, add to `configuration.yaml`:

```
light:
  - platform: mqtt
    name: "Friendly name for light"
    state_topic: "room/rgblight1"
    command_topic: "room/rgblight1/switch"
    brightness_state_topic: "room/rgblight1/brightness"
    brightness_command_topic: "room/rgblight1/brightness/set"
    rgb_state_topic: "room/rgblight1/color"
    rgb_command_topic: "room/rgblight1/color/set"
```

Ensure that the topic names match exactly between `config.json` and Home Assistant, in particular `topic/subtopic/` and `topic/subtopic` are different topics.
