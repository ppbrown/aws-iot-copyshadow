# Utility to download  a copy of DeviceShadow

This is the variant that uses pure AWS IoT code to download
the default DeviceShadow info, as a JSON format file.
It will then save it to a designated file
( /greengrass/v2/aws.deviceshadow )

Any time there is an update, it will refresh the copied file.

You can call it directly, with

    sudo python3 iot.py

However, you have the option of running it as a local greengrass component
instead. You can do that with

    make localdeploy

It should be easily possible to make it a standard S3 loaded
component, but you currently have to do that yourself

