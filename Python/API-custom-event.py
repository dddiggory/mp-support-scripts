"""
Create a custom event via the API! The customer's use case was to create a Custom Event 
that included an event/property that went beyond the UI's dropdown limits.
"""
import time
import urllib
import md5
import requests
import json

expire = int(time.time()) + 1000

def make_sig(raw_url):
	"""Take a raw URL, formulate a sig, and return the new 
	complete URL.
	"""
	url = urllib.unquote(raw_url).decode('utf8')
	url = url.replace("+"," ")
	args = url.split("?")[1].split("&")
	args_new = []

	for i in args:
		if i[0:4] != "sig=":
			args_new.append(i)
	args_concat = "".join(sorted(args_new))
	sig = md5.new(args_concat+api_secret).hexdigest()
	return raw_url + "&sig=" + sig

def collect_events():
	"""Collect events from the user."""
	addMore = True
	alternatives = []
	while addMore:
		altEvent = raw_input("Add an Event to this Custom Event:  ")
		event = {}
		event["event"] = altEvent
		alternatives.append(event)
		addMoreQ = raw_input("Thanks! Add another? (Y/N)  ")
		if addMoreQ.lower() != "y":
			addMore = False

	alternatives = json.dumps(alternatives)
	print alternatives
	return alternatives

def create_custom_event():
	"""Send an API request that creates a custom event based on 
	the user's input.
	"""
	root = "https://mixpanel.com/api/2.0/custom_events/create/"
	URL = "%s?expire=%d&api_key=%s&name=%s&alternatives=%s" % (root, expire, api_key, name, alternatives)
	URL = make_sig(URL)
	print "Sending request to %s ..." % (URL)
	print "\n\n'%s' custom event created!" % (name)
	response = requests.post(URL).text
	return response

api_key = raw_input("Enter API Key:  ")
api_secret = raw_input("Enter API Secret:  ")
token = raw_input("Enter Project Token:  ")
name = raw_input("What would you like to call the custom event?  ")

alternatives = collect_events()
print create_custom_event()