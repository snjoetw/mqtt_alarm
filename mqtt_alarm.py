#!/usr/bin/python

import RPi.GPIO as GPIO
import logging
import paho.mqtt.publish as publish
from time import sleep
from systemd.journal import JournalHandler

log = logging.getLogger('mqtt_alarm')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

MQTT_HOST = "10.0.0.20"
MQTT_TOPIC_PREFIX = "home/alarm/"
MQTT_CLIENT_ID = ""
MQTT_PAYLOADS = {
  0: "off",
  1: "on",
}

# Dictionary of GPIO PIN to mqtt topic
PIN_MAP = {
  7: "front_door",
  11: "garage_entry_door",
  12: "laundry_room_window",
  13: "kitchen_window",
  16: "family_room_window",
  18: "living_room_window",
  22: "office_window",
  29: "workout_room_window",
  32: "dressing_room_window",
  35: "upstairs_hallway_motion",
}

GPIO.setmode(GPIO.BOARD)

def state_change_hadler(channel):
  state = GPIO.input(channel)

  if state:
    log.info("Rising edge detected on {}".format(channel))
  else:
    log.info("Falling edge detected on {}".format(channel))

  publish_event(channel, state)

def publish_event(pin, state):
  topic = MQTT_TOPIC_PREFIX + PIN_MAP[pin]
  payload = MQTT_PAYLOADS[state]

  publish.single(topic, payload, hostname=MQTT_HOST, retain=True, qos=1)

  log.info("Published event, topic={}, payload={}, hostname={}".format(topic, payload, MQTT_HOST))

for pin, name in PIN_MAP.items():
  GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.add_event_detect(pin, GPIO.BOTH, callback=state_change_hadler, bouncetime=100)

  state = GPIO.input(pin)

  log.info("Mapped pin {:0>2d} to {}".format(pin, name))
  log.info("... state {}".format(state))

  publish_event(pin, state)

try:
  while True:
    sleep(60)
except KeyboardInterrupt:
  log.info("Stopping...")
finally:
  GPIO.cleanup()
