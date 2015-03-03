import json
import operator


# Set up user list
top10file = raw_input("Please enter filename of Exported events:  ")
topSelection = int(raw_input("How many top users to return (i.e. 10, 40, 100)?  "))

eventFile = open(top10file, "rU")
idList = []

setCount = 0

eventLength = str(sum(1 for line in open(top10file)))
print eventLength

for item in eventFile:
	record = json.loads(item)
	uid = record["properties"]["distinct_id"]
	idList.append(json.dumps(uid))
	setCount += 1
	percentage = 100*(float(setCount) / float(eventLength))
	percentageStr = str(percentage)[0:4]
	print "Building set of IDs... %s/%s (%s%%):\t\t%s" % (setCount, eventLength, percentageStr, uid)

print "Done building ID set."

mainDict = {}

counter = 0

for line in idList:
	counter += 1
	# line = line[:-1]
	percentage = 100*(float(counter) / float(eventLength))
	percentageStr = str(percentage)[0:4]
	if line in mainDict:
		mainDict[line] += 1
	else:
		mainDict[line] = 1
	print "Counting up events... %d/%s (%s%%):\t\t%s:  %s" % (counter, eventLength, percentageStr, line, mainDict[line])

sortedDict = sorted(mainDict.items(), key=operator.itemgetter(1), reverse=True)

finalCount = 0
writeCount = 0

print "======Top " + str(topSelection) + " Users List======="
for count in sortedDict:
	finalCount += 1
	print "#%s:\t\t%s\t%s events" % (str(finalCount), str(count[0]), str(count[1]))
	if finalCount == topSelection:
		break

writeToFile = raw_input("Write to file (Y/N)?  ")
if writeToFile == "y" or writeToFile == "Y":
	filename = raw_input("Select filename:  ")
	newFile = open(filename, "w")
	newFile.write("======Top " + str(topSelection) + " Users List=======\n")
	for count in sortedDict:
		writeCount += 1
		newFile.write("#%s:\t%s\t%s events\n" % (str(writeCount), str(count[0]), str(count[1])))
		if writeCount > topSelection:
			"Done! %s is in the directory of this script." % (str(filename).title())
			break