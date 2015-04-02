"""This is a Macbook-safe version of the Event_Import_Json.py script.
The Eventlet behavior within the 'batch_update' function is built for
high bandwidth dev boxes, and can *drop* events when run with limited
memory or over a less-than-stellar connection.

Specifically, this script includes a pool.waitall() function to 
effectively disable eventlet's batching behavior. It's slower, but 
will reliably send every event in the import file.
"""

import json
import base64
import time
import urllib
from time import strftime
import eventlet
from eventlet.green import urllib2

class EventImporter(object):
    def __init__(self, token, api_key):
        self.token = token
        self.api_key = api_key
    
    def update(self, eventList):
        url = "http://api.mixpanel.com/import/?"
        batch = []
        for event in eventList:
            assert(event['properties'].has_key("time")), "Must specify a backdated time"
            assert(event['properties'].has_key("distinct_id")), "Must specify a distinct ID"
            event['properties']['time'] = str(int(event['properties']['time']) - (time_offset * 3600)) #transforms timestamp to UTC
            if "token" not in event['properties']:
                event['properties']["token"] = self.token
            batch.append(event)

        payload = {"data":base64.b64encode(json.dumps(batch)), "verbose":1,"api_key":self.api_key}
        response = urllib2.urlopen(url, urllib.urlencode(payload))
        message = response.read()
        print "Sent 50 events on " + strftime("%Y-%m-%d %H:%M:%S") + "!"
        print message
        if json.loads(message)['status'] != 1:
            raise RuntimeError('import failed')

    def batch_update(self, filename):
        pool = eventlet.GreenPool(size=200)
        events = []
        with open(filename,'r') as f:
            for event in f:
                events.append(json.loads(event))
                if len(events) == 50:
                    pool.spawn(self.update, events)
                    pool.waitall()
                    events = []
            if len(events):
                self.update(events)
                print str(events) + "\n" + "Sent remaining %d events!" % len(events)

token = raw_input("Token: ")
api_key = raw_input("API Key: ")
fname = raw_input("Import Filename: ")
time_offset = int(raw_input("Project time offset from GMT (ex. PST = -8): "))

import_event = EventImporter(token, api_key)
import_event.batch_update(fname)

