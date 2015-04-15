import json
import urllib2
import urllib
import md5
import time
import csv
import os


print("""
Welcome! This script will:
1) Grab the current set of top Events & Properties.
2) Query your selected date range for the counts & percentages these events represented.
""")

custName = raw_input("Customer Name:  ")
apiKey = raw_input("API Key:  ")
apiSecret = raw_input("API Secret:  ")
apiToken = raw_input("Project Token:  ")
from_date = raw_input("From Date (YYYY-MM-DD):  ")
to_date = raw_input("To Date (YYYY-MM-DD):  ")
filename = "%s_EventCounts_%s_to_%s" % (custName, from_date, to_date)

collectErrors = []
expire = int(time.time()) + 1000

print "Working..."

def makeSig(raw_url):
	url = urllib.unquote(raw_url).decode('utf8')
	url = url.replace("+"," ")
	args = url.split("?")[1].split("&")
	args_new = []

	for i in args:
		if i[0:4] != "sig=":
			args_new.append(i)
	args_concat = "".join(sorted(args_new))
	sig = md5.new(args_concat+apiSecret).hexdigest()
	return raw_url + "&sig=" + sig

def getEvents():
	root = "https://mixpanel.com/api/2.0/events/names/"
	URL = "%s?expire=%d&api_key=%s&type=general" % (root, expire, apiKey)
	URL = makeSig(URL)
	eventList = json.loads(urllib2.urlopen(URL).read())
	return eventList

def getCounts(eventList):
	eventCounts = []
	overallCount = 0
	for event in eventList:
		print "Querying " + event + "..."
		countDict = {}

		encodedEvent = urllib.quote(event)
		root = "http://mixpanel.com/api/2.0/segmentation/"
		URL = ("%s?event=%s&expire=%d&api_key=%s&from_date=%s&to_date=%s&type=general") % (root, encodedEvent, expire, apiKey, from_date, to_date)
		URL = makeSig(URL)
		

		try:
			response = json.loads(urllib2.urlopen(URL).read())
		except:
			print "ERROR: Failed on " + event + "."
			print URL
			collectErrors.append(event)
			continue
		eventCount = 0
		try:
			for date in response['data']['values'][event]:
				eventCount += response['data']['values'][event][date]
		except:
			pass
		countDict["Event"] = event
		countDict["Count"] = eventCount
		overallCount += eventCount
		eventCounts.append(countDict)
	return eventCounts, overallCount

def addPercentages(countData):
	countDict = countData[0]
	totalCount = countData[1]
	for dictionary in countDict:
		try:
			percentage = (float(dictionary["Count"]) / float(totalCount))
		except:
			percentage = 0.0
		percentage *= 100.0
		percentage = str(round(percentage, 4)) + "%"
		dictionary["Percentage"] = percentage
	return countDict

def writeToCSV(finalDict, fieldNames):
	with open(filename+"-temp.csv", "wb") as outFile:
		writer = csv.DictWriter(outFile, delimiter=",", fieldnames=fieldNames)
		writer.writeheader()
		for row in finalDict:
			writer.writerow(row)

def addProperties():
	print "Collecting property keys & building CSV..."
	f = open(filename+"-temp.csv", "rU")
	finalFile = open(filename+".csv", "w")
	lineCount = 1
	for line in f:
		event = line.split(',')[0]
		if lineCount == 1:
			finalFile.write(line[:-1]+",Properties\n")
			lineCount += 1
		else:
			root = "http://mixpanel.com/api/2.0/events/properties/top"
			URL = ("%s?event=%s&expire=%d&api_key=%s&limit=20") % (root, event, expire, apiKey)
			URL = makeSig(URL)
			try:
				propList = json.loads(urllib2.urlopen(URL).read())
			except:
				print "failed to get properties for " + event
				continue
			for prop in propList.keys():
				line = line[:-1] + "," + json.dumps(prop)
			line += "\n"
			finalFile.write(line)
	finalFile.close()

countsData = getCounts(getEvents())
fieldNames = ["Event", "Count", "Percentage"]
writeToCSV(addPercentages(countsData), fieldNames)
addProperties()

os.remove(filename+"-temp.csv")

print "\n\nDone!"
print """
Please check the UI for these %d events, which returned errors
and have been excluded: %s
""" % (len(collectErrors), json.dumps(collectErrors))