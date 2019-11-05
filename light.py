import machine
import neopixel

class MQTTLight:
    '''
    Opject to control neopixels and update state on Home Assistant through MQTTT
    mqtt_client: MQTT client to send updates to (MQTTClient)
    pin: GPIO pin to send Neopixel data (int)
    pixels: Number of Neopixels connected (int)
    state_topic: MQTT topic to send state updates to (str)
    brightness_topic; MQTT topic to send brightness updates to (str)
    color_topic: MQTT topic to send color updates to (str)
    '''
    def __init__(self, mqtt_client, pin, pixels, state_topic, brightness_topic, color_topic):
        self.np = neopixel.NeoPixel(machine.Pin(pin), pixels)
        self.mqtt = mqtt_client
        self.pixels = pixels
        self.state_topic = state_topic
        self.brightness_topic = brightness_topic
        self.color_topic = color_topic
        self.states = {
                "brightness": 0,
                "state": "OFF",
                "color": [255,255,255]
            }
        self.off()
    
    def set_color(self, color=None, update=True):
        '''
        Set neopixel colors

        color: Color to set to (tuple)
        update: Flag to determine whether to send updates (bool)
        '''
        if color is not None:
            self.states["color"] = color
        if self.states["state"] == "ON":
            for i in range(self.pixels):
                self.np[i] = self.scale(self.states["color"])
            self.np.write()
        else:
            self.off(update=update)
        if update:
            self.update()
    
    def scale(self, color):
        '''
        Scale colors by brightness, quadratic scaling for low brightnesses
        color: Color to scale (tuple)
        '''
        color_scaled = []
        for i in range(len(color)):
            color_scaled.append(int(color[i] * (self.states["brightness"] / 255) ** 2))
        return tuple(color_scaled)
    
    def set_brightness(self, brightness):
        '''
        Set Neopixel brightness
        brightness: Brightness to set to from 0-255 inclusive (int)
        '''
        self.states["brightness"] = brightness
        self.set_color()
    
    def off(self, update=True):
        '''
        Turns off Neopixels
        update: Flag to determine whether to send updates (bool)
        '''
        self.states["state"] = "OFF"
        for i in range(self.pixels):
            self.np[i] = (0, 0, 0)
        self.np.write()
        if update:
            self.update()
    
    def on(self):
        '''
        Turns on Neopixels to last known settings
        '''
        self.states["state"] = "ON"
        self.set_color()
    
    def update(self):
        '''
        Updates Neopixel state via MQTT
        '''
        try:
            self.mqtt.publish(self.state_topic, self.states["state"], retain=True)
            self.mqtt.publish(self.brightness_topic, str(self.states["brightness"]), retain=True)
            self.mqtt.publish(self.color_topic, str(self.states["color"])[1:-1], retain=True)
        except AttributeError:
            print("MQTT not connected")
