#!/bin/python

# This is a greengrass integrated component, that uses greengrass client
# libraries, to download a copy of the deviceshadow.
#
import os

from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2

# Where to write the data, theoretically
DEVICESHADOWCACHE = "/greengrass/v2/aws.deviceshadow"

THINGNAME = os.getenv("AWS_IOT_THING_NAME")

CLIENTOBJ = GreengrassCoreIPCClientV2()

def on_message_received(topic, payload):
    print('DEBUG: should in theory re-get shadow information now')
    # You can perform further processing or actions based on the received message
    # eg: check for cases with topic.endswith("get/accepted"), and so on
    # but we could simply just re-call create_deviceshadow_cache()

def savedeviceshadow(data):
    tmpfile= DEVICESHADOWCACHE + str(os.getpid())
    with open(tmpfile, "w") as file:
      file.write(data)
    os.chmod(tmpfile,  0o644)
    os.rename(tmpfile, DEVICESHADOWCACHE)

def create_deviceshadow_cache():
    print("DEBUG: thingname is " + THINGNAME)
#    shadow_response = CLIENTOBJ.get_thing_shadow(thing_name=THINGNAME,shadow_name="flippy")
    shadow_response = CLIENTOBJ.get_thing_shadow(thing_name=THINGNAME,shadow_name="")
    shadowdata = shadow_response.payload.decode('utf-8')
    print("DEBUG: Printing shadow info: " + shadowdata)
    savedeviceshadow(shadowdata)


def subscribe_to_mqtt_topic():
    topicname = '$aws/things/' + THINGNAME + '/shadow/update/accepted'
    ## CLIENTOBJ.subscribe_to_topic(topic=topicname, stream_handler=on_message_received)
    # This SHOULD WORK?!?!
    print("DEBUG: I cant get subscribe_to_topic working")
    exit(1)


create_deviceshadow_cache()
subscribe_to_mqtt_topic()

while True:
    time.sleep(5)
