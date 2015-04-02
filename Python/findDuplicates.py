"""Find duplicates based on some "Property in Common" (e.g., name,
email) and identify any users that don't appear to be "current"
based on $last_seen. For these non-current duplicates, set up a
file that people-importer.py can use to label these users. They
can be double-checked, then batch-deleted.

This version hasn't yet been "genericized" for future use.
"""
import json
import datetime

f = open('users.txt', 'rU')


uidsToCheck = []
namesToCheck = []

for line in f:
	if len(line) > 1:
		uid = line.split('distinct_id=')
		uid = uid[1].strip(')\n')
		uidsToCheck.append(uid)

#Collect names
userbase = open('backup1427753344.txt', 'rU')
nameDict = {}

for user in userbase:
	data = json.loads(user)
	if data["$distinct_id"] in uidsToCheck:
		nameDict[data["$properties"].get("$name")] = {}

#Find users that match names
userbase = open('backup1427753344.txt', 'rU')

nameList = nameDict.keys()
matchCount = 0
for user in userbase:
	data = json.loads(user)
	name = data["$properties"].get("$name")
	
	if name and name in nameList:
		uid = data["$distinct_id"]
		lastSeen = data["$properties"].get("$last_seen")
		nameDict[name][uid] = lastSeen	

deletions = set()
#find non-current distinct_ids
for name in nameDict.keys():
	allTimestamps = []
	times = nameDict[name]
	for uid in times:
		formattedTimestamp = datetime.datetime.strptime(times[uid], "%Y-%m-%dT%H:%M:%S")
		allTimestamps.append(formattedTimestamp)

	print allTimestamps
	print max(allTimestamps)

	for uid in times:
		formattedTimestamp = datetime.datetime.strptime(times[uid], "%Y-%m-%dT%H:%M:%S")
		if formattedTimestamp < max(allTimestamps):
			deletions.add(uid)
			print "delete " + uid
		else:
			print "save " + uid


deleteFile = open("deletions.txt", "w")

for user in deletions:
	output = {}
	output["$distinct_id"] = user
	output["$properties"] = {}
	output["$properties"]["Duplicate-Mar30"] = True
	deleteFile.write(json.dumps(output)+"\n")
deleteFile.close()