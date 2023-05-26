# Utility to download  a copy of DeviceShadow


## Short summary:

On startup, grab and save a copy of the default DeviceShadow info,
as a JSON format file.
Then subscribe to the update topic. Any time there is an update,
refresh the copied file.

There are two versions of code. One is in the Greengrass directory,
and the other is in the IoT directory.
You probably want the IoT version.

## Make a shadow first!!

Note that this code does NOT create a deviceshadow. Before using it, you need
to create one, or it will error out. 
One way of doing this is through the GUI.
Go to IoT -> All Devices -> Things
Click on your device, then go to the Device Shadows tab.
Then just click the "Create Shadow" button, and select
 Unnamed (classic) Shadow


## Greengrass directory version

This version of the code uses the AWS Greengrass client related libraries,
and thus will not work unless it has a properly functional Greengrass
instance running on the same machine. It also expects to run
as a "local" component. 
(See the make target for "localdeploy")
Convert it to run from S3 yourself


## IoT directory version

The code in the IoT directory can be run as a completely standalone
AWS IoT client. For development convenience, it does expect to find its
configuration in greengrass style, but it does NOT need a running
greengrass instance to fuction. You can call it directly, with

    sudo python3 iot.py

However, you have the option of running it as a local greengrass component
instead. You can do that with

    make localdeploy

Again, it should be easily possible to make it a standard S3 loaded
component, but you currently have to do that yourself

## Recap of why greengrass == bad

Using ShadowManager gives us the "benefit" of an AWS module that
takes care of auto-syncing the cloud shadow to the local device.
It also gives us the ability to keep "local shadows" that may or
may not be synced to the cloud.

The problems are:

1. We dont need local-only shadows, so theres a lot of complexity we dont need
2. We are forced to keep accessing the shadow info through the 
  HORRIBLE greengrass APIs
3. The additional required configuration and setup is a nightmare.
   THREE LAYERS OF REQUIRED ADDITIONAL CONFIG, to get through
    Greengrass access controls.. just to make ONE call!

So.. hard pass on ShadowManager
