"""Example of using WyzeSense USB bridge.

**Usage:** ::
  sample.py [options]

**Options:**

    -d, --debug     output debug log messages to stderr
    -v, --verbose   print and log more information
    --device PATH   USB device path [default: /dev/hidraw0]

**Examples:** ::

  sample.py --device /dev/hidraw0   # Using WyzeSense USB bridge /dev/hidraw0

"""
from __future__ import print_function

import os
import re
import sys
import logging
import errno

from . import gateway as wyzesense

def on_event(ws, event):
    print("Event: %s" % event)

def main(args):
    if args['--debug']:
        loglevel = logging.DEBUG - (1 if args['--verbose'] else 0)
        logging.getLogger("wyzesense").setLevel(loglevel)
        logging.getLogger().setLevel(loglevel)

    device = args['--device']
    print("Openning wyzesense gateway [%r]" % device)
    try:
        ws = wyzesense.Open(device, on_event)
    except IOError:
        print("No device found on path %r" % device)
        return 1
    
    def List(unused_args):
        result = ws.List()
        print("%d sensor paired:" % len(result))
        for mac in result:
            print("\tSensor: %s" % mac)

    def Pair(unused_args):
        result = ws.Scan()
        if result:
            print("Sensor found: mac=%s, type=%d, version=%d" % result)
        else:
            print("No sensor found!")

    def Unpair(mac_list):
        for mac in mac_list:
            if len(mac) != 8:
                print("Invalid mac address, must be 8 characters: %s", mac)
                continue

            print("Un-pairing sensor %s:" % mac)
            if ws.Delete(mac):
                print("Sensor %s removed" % mac)
            else:
                print("Failed to remove sensor %s" % mac)

    def HandleCmd():
        cmd_handlers = {
            'L': ('L to list', List),
            'P': ('P to pair', Pair),
            'U': ('U to unpair', Unpair),
            'X': ('X to exit', None),
        }

        for v in cmd_handlers.values():
            print(v[0])

        cmd_and_args = raw_input("Action:").strip().upper().split()
        if len(cmd_and_args) == 0:
            return True
        
        cmd = cmd_and_args[0]
        if cmd not in cmd_handlers:
            return True

        handler = cmd_handlers[cmd]
        if not handler[1]:
            return False
        
        handler[1](cmd_and_args[1:])
        return True

    try:
        while HandleCmd():
            pass
    finally:
        ws.Stop()

    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(relativeCreated)d ms [%(name)s] %(message)s')

    try:
        from docopt import docopt
    except ImportError:
        sys.exit("the 'docopt' module is needed to execute this program")

    # remove restructured text formatting before input to docopt
    usage = re.sub(r'(?<=\n)\*\*(\w+:)\*\*.*\n', r'\1', __doc__)
    sys.exit(main(docopt(usage)))
