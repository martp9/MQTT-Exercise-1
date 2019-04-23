#################################################################
#
# Code by P. Marti BFH 21.04.2019
# Ecercise MQTT FS 2019
#
#################################################################
import time
from umqttsimple import MQTTClient
from machine import Pin, I2C
import BMP280 
import esp
import machine
esp.osdebug(None)
import gc
gc.collect()

# MQTT Server Information 
SERVER ='m24.cloudmqtt.com' #TODO
CLIENT_ID='ESP32'           #TODO
PORT=15254                  #TODO
TOPIC_PUB=b'temp_humidity'  #aka tag publish
TOPIC_SUB=b'led1'           #aka tag subscribe
# User login if needed
USERNAME = 'YOUR_USER_NAME'
PASSWORD = 'YOUR_PASSWORD'

# Update parameter 
last_sensor_reading = 0
# Publish update interval in seconds
readings_interval = 5

# Create library object using our bus I2C port
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
#1 Create led object using pin class
led=Pin(2,Pin.OUT)

#Read data from BME280 sensor
def read_ds_sensor():
  try:
    bmp = BMP280.BMP280(i2c=i2c)
    t = bmp.getTemp()
    p = bmp.getPress()
    if isinstance(t, float) and isinstance(p, int):
      # Formate a message for the MQTT broker (publish)
      msg = (b'{0:3.1f},{1:3.1f}'.format(t,p))
      print(msg)
      return msg
    else:
      print('invalid sensor value')
  except OSError:
    print ('failed to read sensor')
    machine.reset()

#Read LED state    
def sub_cb(topic, msg):
  print((topic, msg))
  if msg == b'on':
    led.value(1)
  elif msg == b'off':
    led.value(0)

# try to connect to the MQTT Broker    
def connect_and_subscribe():
  global CLIENT_ID, SERVER, PORT, USERNAME, PASSWORD, TOPIC_PUB
  client=MQTTClient(CLIENT_ID, SERVER,PORT , USERNAME, PASSWORD)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(TOPIC_SUB)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (SERVER, TOPIC_SUB))
  return client

# Restart the connection
def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(5)
  machine.reset()
  
# Try to connect to the MQTT server
try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

# Main Routine
while True:
  try:
    # Check for new message from the MQTT broker (subscribe) 
    client.check_msg()
    if (time.time() - last_sensor_reading) > readings_interval:
      msg = read_ds_sensor()
      client.publish(TOPIC_PUB, msg)
      last_sensor_reading = time.time()
  except OSError as e:
    restart_and_reconnect()





