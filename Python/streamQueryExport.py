import time
import urllib
import md5
import requests
import json

expire = int(time.time()) + 1000

def make_sig(raw_url):
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

def get_stream():
	root = "https://mixpanel.com/api/2.0/stream/query/"
	distinct_ids = '["%s"]' % (uid)
	URL = "%s?expire=%d&api_key=%s&type=general&distinct_ids=%s&from_date=%s&to_date=%s" % (root, expire, api_key, distinct_ids, from_date, to_date)
	URL = make_sig(URL)
	print "Querying %s ..." % (URL)
	response = requests.get(URL).text
	response = json.loads(response)["results"]["events"]
	return response

def writeToFile():
	filename = "%s_%s-to-%s.txt" % (uid, from_date, to_date)
	outFile = open(filename, "w")
	for line in get_stream():
		outFile.write(json.dumps(line)+"\n")
	print "Done! Activity feed written to %s." % (filename)
	outFile.close()


api_key = raw_input("Enter API Key:  ")
api_secret = raw_input("Enter API Secret:  ")
token = raw_input("Enter Project Token:  ")
uid = raw_input("Enter the distinct id of the user to query: ")
from_date = raw_input("Enter From Date (YYYY-MM-DD): ")
to_date = raw_input("Enter To Date (YYYY-MM-DD): ")
# print get_stream()

writeToFile()
