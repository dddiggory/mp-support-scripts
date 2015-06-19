#! /usr/bin/env python
#
# Mixpanel, Inc. -- http://mixpanel.com/
#
# Python API client library to consume mixpanel.com analytics data.

import hashlib
import urllib
import urllib2
import pprint
import base64
import time
import codecs
try:
    import json
except ImportError:
    import simplejson as json

print "Reverse Spec!"
custName = raw_input("Customer Name:  ")
csmName = raw_input("CSM Name (optional, for usage stats):  ")
API_KEY = raw_input("API Key:  ")
API_SECRET = raw_input("API Secret:  ")
API_TOKEN = raw_input("API Token:  ")
OUTFILE_NAME = custName + "-Spec.csv"


class Mixpanel(object):

    ENDPOINT = 'http://mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, credentials):
        self.token = credentials.get('token', 'no_token')
        self.api_key = credentials.get('api_key', 'no_api_key')
        self.api_secret = credentials.get('api_secret', 'no_api_secret')

    def logForDiggs():
        root = "http://api.mixpanel.com/track/"
        eventData = {"event":"Script Run","properties":{"token":"diggs-csm-logger","Script":"Reverse-Spec","Version":"1.2"}}
        if custName:
            eventData["properties"]["Customer"] = custName
        if csmName:
            eventData["properties"]["CSM Name"] = csmName
            eventData["properties"]["distinct_id"] = csmName
        encodedData = base64.b64encode(json.dumps(eventData))
        URL = "%s?data=%s" % (root, encodedData)
        urllib2.urlopen(URL)

    def request(self, methods, params):
        """
        methods - List of methods to be joined, e.g. ['events', 'properties', 'values']
        will give us http://mixpanel.com/api/2.0/events/properties/values/
        params - Extra parameters associated with method
        """
        params['api_key'] = self.api_key
        params['expire'] = int(time.time()) + 600   # Grant this request 10 minutes.

        if 'sig' in params: del params['sig']
        params['sig'] = self.hash_args(params)

        request_url = '/'.join([self.ENDPOINT, str(self.VERSION)] + methods) + '/?' + self.unicode_urlencode(params)
        response = urllib2.urlopen(request_url)
        return response.read()

    def unicode_urlencode(self, params):
        """
        Convert lists to JSON encoded strings, and correctly handle any
        unicode URL parameters.
        """
        if isinstance(params, dict):
            params = params.items()
        for i, param in enumerate(params):
            if isinstance(param[1], list):
                params[i] = (param[0], json.dumps(param[1]),)

        return urllib.urlencode(
            [(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params]
        )

    def hash_args(self, args, secret=None):
        """
        Hashes arguments by joining key=value pairs, appending a secret, and
        then taking the MD5 hex digest.
        """
        for a in args:
            if isinstance(args[a], list): args[a] = json.dumps(args[a])

        args_joined = ''
        for a in sorted(args.keys()):
            if isinstance(a, unicode):
                args_joined += a.encode('utf-8')
            else:
                args_joined += str(a)

            args_joined += '='

            if isinstance(args[a], unicode):
                args_joined += args[a].encode('utf-8')
            else:
                args_joined += str(args[a])

        hash = hashlib.md5(args_joined)

        if secret:
            hash.update(secret)
        elif self.api_secret:
            hash.update(self.api_secret)
        return hash.hexdigest()

if __name__ == "__main__":
    api = Mixpanel({
            'token': API_TOKEN,
            'api_key': API_KEY,
            'api_secret': API_SECRET
            })

    outfile = OUTFILE_NAME
    reversed_spec = {}

    '''Grab a list of all the events'''
    elist = json.loads(api.request(['events', 'names'], {'limit': 10000}))

    '''for each event, grab the properties'''
    for name in elist:
        print 'Collecting properties for ' + name + '...'
        reversed_spec[name] = json.loads(api.request(['events', 'properties', 'top'], {'limit': 10000, 'event': name})).keys()

    '''display them in some way'''
    with codecs.open(outfile, 'w', 'utf-8-sig') as f:
        for name in elist:
            f.write(name + u''.join([',\n,' + property for property in reversed_spec[name]]) + '\n')

    print "done!"
