# WyzeSensePy
WyzeSensePy is a python script trying to implement the communication protocol between WyzeCamera and WyzeSense USB dongle. This script is meant for prototyping purpose to demostrate an alternative way of using WyzeSense sensor kit on platforms other than Wyze cameras.

The script is verified working on Rapsberry Pi3. You will need to install python on raspberry pi if it hasn't be installed. Currently, the Wyze dongle is showing up as a raw HID device, only accessible by root account. As a result, you will need to run this script as root. Alternatively, you can "chmod 666 /dev/hidraw0" so regular user account can read/write to it.

This is still a work-in-progress project, as I'm still working on decoding the event alarm data.

