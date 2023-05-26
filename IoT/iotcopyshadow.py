#!/bin/python

###################################################
### READ ALL OF THIS COMMENT SECTION!!!!!     #####
###################################################
#
# This is an attempt to make a STRAIGHT UP MQTT/IoT 
# device shadow caching routine.
# Functionality:
#  1. grab current shadow directly from cloud
#  2. subscribe to updates
#  3. Loop for update detected, grab full version again
#
# This code needs to run equally well inside a greengrass component,
# OR on straight command line
#
# This does not require being inside a greengrass component,
# but it does currently require having access to
#   /greengrass/v2/config/effectiveConfig.yaml
# along with the privKey files for the thing, etc.
# 
# This means if you want to run it outside greengrass,
# you may have to run it with    sudo
#
# By default, it gets the "default" deviceshadow
# But this is easily changable, by modifying the
# SHADOWTOPIC variable, to something like
#
### SHADOWTOPIC = f"$aws/things/{thing_name}/shadow/name/flippy"
# (but you have to do it in the code lower down!! )

 
# We steal lots of code from the aws-iot python SDK sample,
# pubsub.py
# We might consider making a common library for this junk
#  (Initial AWS MQTT client)
# Hard to believe there isnt one already?!?

import os
import time
import yaml

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# There exists
### from awsiot import iotshadow
# but it turns out not to be any easier to use, and is underdocumented

DEVICESHADOWCACHE = "/greengrass/v2/aws.deviceshadow"


#############################################################################


# Callback when connection is accidentally lost
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. Error: {}".format(error))

# Callback when an interrupted connection is re-established
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))
    if (return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present):
        print("Session did not persist Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread
        # Evaluate result with a callback instead
        resubscribe_future.add_done_callback(on_resubscribe_complete)


# Callback to resubscribe to previously subscribed topics upon lost session
def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))
    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


def requestdata():
  mqtt_connection.publish(
    topic=SHADOWTOPIC + '/get',
    payload="",
    qos=mqtt.QoS.AT_LEAST_ONCE)


def savedeviceshadow(data):
    tmpfile= DEVICESHADOWCACHE + str(os.getpid())
    with open(tmpfile, "w") as file:
      file.write(data)
    os.chmod(tmpfile,  0o644)
    os.rename(tmpfile, DEVICESHADOWCACHE)


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    if topic.endswith("get/accepted"):
        print(payload.decode('utf-8'))
        savedeviceshadow(payload.decode('utf-8'))
    elif topic.endswith("update/accepted"):
        print("DEBUG: updated detected. requesting re-download")
        requestdata()
    elif topic.endswith("get/rejected"):
        print("DEBUG: received get/rejected message")
    else:
        print("Unrecognized topic received: " + topic)



######################################################################
########################## Main Line #################################

file_name = '/greengrass/v2/config/effectiveConfig.yaml'
with open(file_name, 'r') as f:
  configdata = yaml.safe_load(f)

thing_name    = configdata["system"]["thingName"]
cert_path    = configdata["system"]["certificateFilePath"]
key_path     = configdata["system"]["privateKeyPath"]
root_ca_path = configdata["system"]["rootCaPath"]
endpoint     = configdata["services"]["aws.greengrass.Nucleus"]["configuration"]["iotDataEndpoint"]


if not thing_name:
    print("DEBUG: no thing_name set. Harcoding to demo-device")
    thing_name="demo-device"

SHADOWTOPIC = f"$aws/things/{thing_name}/shadow"
print("DEBUG: shadow topic is " + SHADOWTOPIC)
print("DEBUG: endpoint is " + endpoint)



# boilerplate for setting up client connections
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=endpoint,
    cert_filepath=cert_path,
    pri_key_filepath=key_path,
    client_bootstrap=client_bootstrap,
    ca_filepath=root_ca_path,
    on_connection_interrupted=on_connection_interrupted,
    on_connection_resumed=on_connection_resumed,
    client_id=thing_name,
    clean_session=True,
    keep_alive_secs=6
)


# Connect to the AWS IoT endpoint
print("DEBUG1...")
print("connect result=")
print (mqtt_connection.connect().result())

print("DEBUG2...")

def subscribe_topic(message_topic):
  print("Subscribing to topic '{}'...".format(message_topic))
  subscribe_future, packet_id = mqtt_connection.subscribe(
    topic=message_topic,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_message_received)

  subscribe_result = subscribe_future.result()
  print("Subscribed with {}".format(str(subscribe_result['qos'])))


subscribe_topic(SHADOWTOPIC + '/get/accepted')
subscribe_topic(SHADOWTOPIC + '/get/rejected')
subscribe_topic(SHADOWTOPIC + '/update/accepted')

requestdata()

# Wait for the response to be received
##while not publish_future.done():
##    time.sleep(10)

while True:
#    send()
    time.sleep(5)


