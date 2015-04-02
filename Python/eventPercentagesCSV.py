"""CSM-requested script. Provides a CSV of events with counts,
percentages, and existing property keys. Useful for customers who are
watching their usage and want to know if an event is firing more than
anticipated.
"""
import json
import requests
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

apiKey = raw_input("API Key:  ")
apiSecret = raw_input("API Secret:  ")
apiToken = raw_input("Project Token:  ")
from_date = raw_input("From Date (YYYY-MM-DD):  ")
to_date = raw_input("To Date (YYYY-MM-DD):  ")
filename = "EventCounts_%s_to_%s" % (from_date, to_date)

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
	eventList = json.loads(requests.get(URL).text)
	return eventList

def getCounts(eventList):
	eventCounts = []
	overallCount = 0
	for event in eventList:
		countDict = {}
		root = "http://mixpanel.com/api/2.0/segmentation/"
		URL = ("%s?event=%s&expire=%d&api_key=%s&from_date=%s&to_date=%s&type=general") % (root, event, expire, apiKey, from_date, to_date)
		URL = makeSig(URL)
		
		response = json.loads(requests.get(URL).text)
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
	percentageTest = 0.0
	for dictionary in countDict:
		percentage = (float(dictionary["Count"]) / float(totalCount))
		percentageTest += percentage
		percentage = str(percentage)[0:5] + "%"
		dictionary["Percentage"] = percentage
	# print percentageTest
	return countDict

def writeToCSV(finalDict, fieldNames):
	with open(filename+"-temp.csv", "wb") as outFile:
		writer = csv.DictWriter(outFile, delimiter=",", fieldnames=fieldNames)
		writer.writeheader()
		for row in finalDict:
			writer.writerow(row)

def addProperties():
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
			propList = json.loads(requests.get(URL).text)
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

print "Done!"
