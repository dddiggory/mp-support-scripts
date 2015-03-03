import json

file = "xbj"

f = open(file, "rU")

# 1: Started Trial
# 2A: Inbox Dashboard where Experiment Account Completion == "Test"
# 2B: Inbox Dashboard where Experiment Account Completion == "Control"
# 3: Template where Action == "Inserted"
# 3: Reminder where Action == "Set"
# 3: Send Later where Action == "Scheduled"
# 3: Referral where Action == "Email Sent"
StartedTrial = set()
StartedTrialCount = 0
InboxDashboard = {}
InboxDashboard["Control"] = set()
InboxDashboard["Test"] = set()
InboxDashboardChecker = set()
Feature_Template = set()
Feature_Reminder = set()
Feature_SendLater = set()
Feature_Referral = set()

Feature_Template_Test = set()
Feature_Reminder_Test = set()
Feature_SendLater_Test = set()
Feature_Referral_Test = set()
Feature_Template_Control = set()
Feature_Reminder_Control = set()
Feature_SendLater_Control = set()
Feature_Referral_Control = set()

count = 0
printCount = 0

# Collect counts for all steps
for line in f:
	count += 1
	printCount += 1
	data = json.loads(line)
	event = data["event"]
	props = data["properties"]
	uid = props["distinct_id"]
	time = props["time"]
	if "Started Trial" == event:
		StartedTrialCount += 1
		StartedTrial.add(uid)
	elif ("Inbox Dashboard" == event) and (props.get("Action")) and (uid in StartedTrial):
		if props.get("Experiment Account Completion") == "Test":
			InboxDashboard["Test"].add(uid)
			InboxDashboardChecker.add(uid)
		elif props.get("Experiment Account Completion") == "Control":
			InboxDashboard["Control"].add(uid)
			InboxDashboardChecker.add(uid)
	# Engagement Events
	elif ("Template" == event) and ("Inserted" == props.get("Action")) and (uid in InboxDashboardChecker):
		if uid in InboxDashboard["Test"]:
			Feature_Template_Test.add(uid)
		if uid in InboxDashboard["Control"]:
			Feature_Template_Control.add(uid)
		Feature_Template.add(uid)
	elif ("Reminder" == event) and ("Set" == props.get("Action")) and (uid in InboxDashboardChecker):
		if uid in InboxDashboard["Test"]:
			Feature_Reminder_Test.add(uid)
		if uid in InboxDashboard["Control"]:
			Feature_Reminder_Control.add(uid)
		Feature_Reminder.add(uid)
	elif ("Send Later" == event) and ("Scheduled" == props.get("Action")) and (uid in InboxDashboardChecker):
		if uid in InboxDashboard["Test"]:
			Feature_SendLater_Test.add(uid)
		if uid in InboxDashboard["Control"]:
			Feature_SendLater_Control.add(uid)
		Feature_SendLater.add(uid)
	elif ("Referral" == event) and ("Email Sent" == props.get("Action")) and (uid in InboxDashboardChecker):
		if uid in InboxDashboard["Test"]:
			Feature_Referral_Test.add(uid)
		if uid in InboxDashboard["Control"]:
			Feature_Referral_Control.add(uid)
		Feature_Referral.add(uid)
	if printCount == 5000:
		print "%d/41985345 (%s%%)" % (count, (str((count/41985345.0)*100)[0:5]))
		printCount = 0

twoToThree_Test = set()
twoToThree_Control = set()
twoToThree_Overall = set()


# Get Test/Control/Overall for Step 2->3
for user in InboxDashboard["Test"]:
	if ((user in Feature_Template) or (user in Feature_Reminder) or (user in Feature_SendLater) or (user in Feature_Referral)):
		twoToThree_Test.add(user)
for user in InboxDashboard["Control"]:
	if ((user in Feature_Template) or (user in Feature_Reminder) or (user in Feature_SendLater) or (user in Feature_Referral)):
		twoToThree_Control.add(user)
for user in InboxDashboardChecker:
	if ((user in Feature_Template) or (user in Feature_Reminder) or (user in Feature_SendLater) or (user in Feature_Referral)):
		twoToThree_Overall.add(user)

# Count up users who have done *ALL* engagement events
fullyEngaged = set()
fullyEngaged_Control = set()
fullyEngaged_Test = set()

for user in Feature_Template:
	if (user in Feature_Reminder) and (user in Feature_SendLater) and (user in Feature_Referral) and (user in InboxDashboard["Test"]):
		fullyEngaged_Test.add(user)
	if (user in Feature_Reminder) and (user in Feature_SendLater) and (user in Feature_Referral) and (user in InboxDashboard["Control"]):
		fullyEngaged_Control.add(user)
	if (user in Feature_Reminder) and (user in Feature_SendLater) and (user in Feature_Referral):
		fullyEngaged.add(user)

# Organize Counts
step2ControlCount = len(InboxDashboard["Control"])
step2TestCount = len(InboxDashboard["Test"])
step2OverallCount = len(InboxDashboardChecker)
step3Template = len(Feature_Template)
step3FeatureReminder = len(Feature_Reminder)
step3SendLater = len(Feature_SendLater)
step3Referral = len(Feature_Referral)


print "Step 1: %d" % (StartedTrialCount)
print "Step 2 (Control): %d (%s%%)" % (len(InboxDashboard["Control"]), (str(100*float(len(InboxDashboard["Control"]))/float(StartedTrialCount)))[:5])
print "Step 2 (Test): %d (%s%%)" % (len(InboxDashboard["Test"]), (str(100*float(len(InboxDashboard["Test"]))/float(StartedTrialCount))[:5]))
print "Step 2 (Overall): %d (%s%%)" % (len(InboxDashboardChecker), (str(100*float(len(InboxDashboardChecker))/float(StartedTrialCount))[:5]))

print "Step 2 to 3 Conversion (Control): %d (%s%%)" % (len(twoToThree_Control), (str(100*float(len(twoToThree_Control))/float(len(InboxDashboard["Control"])))[:5]))
print "Step 2 to 3 Conversion (Test):  %d (%s%%)" % (len(twoToThree_Test), (str(100*float(len(twoToThree_Test))/float(len(InboxDashboard["Test"]))))[:5])
print "Step 2 to 3 Conversion (Overall):  %d (%s%%)" % (len(twoToThree_Overall), (str(100*float(len(twoToThree_Overall))/float(len(InboxDashboardChecker))))[:5])

print "Template (Control): %d (%s%%)" % (len(Feature_Template_Control), (str(100*float(len(Feature_Template_Control))/float(StartedTrialCount))[:5]))
print "Template (Test): %d (%s%%)" % (len(Feature_Template_Test), (str(100*float(len(Feature_Template_Test))/float(StartedTrialCount))[:5]))
print "Template (Overall): %d (%s%%)" % (len(Feature_Template), (str(100*float(len(Feature_Template))/float(StartedTrialCount))[:5]))

print "Reminder (Control): %d (%s%%)" % (len(Feature_Reminder_Control), (str(100*float(len(Feature_Reminder_Control))/float(StartedTrialCount))[:5]))
print "Reminder (Test): %d (%s%%)" % (len(Feature_Reminder_Test), (str(100*float(len(Feature_Reminder_Test))/float(StartedTrialCount))[:5]))
print "Reminder (Overall): %d (%s%%)" % (len(Feature_Reminder), (str(100*float(len(Feature_Reminder))/float(StartedTrialCount))[:5]))

print "Send Later (Control): %d (%s%%)" % (len(Feature_SendLater_Control), (str(100*float(len(Feature_SendLater_Control))/float(StartedTrialCount))[:5]))
print "Send Later (Test): %d (%s%%)" % (len(Feature_SendLater_Test), (str(100*float(len(Feature_SendLater_Test))/float(StartedTrialCount))[:5]))
print "Send Later (Overall): %d (%s%%)" % (len(Feature_SendLater), (str(100*float(len(Feature_SendLater))/float(StartedTrialCount))[:5]))

print "Referral (Control): %d (%s%%)" % (len(Feature_Referral_Control), (str(100*float(len(Feature_Referral_Control))/float(StartedTrialCount))[:5]))
print "Referral (Test): %d (%s%%)" % (len(Feature_Referral_Test), (str(100*float(len(Feature_Referral_Test))/float(StartedTrialCount))[:5]))
print "Referral (Overall): %d (%s%%)" % (len(Feature_Referral), (str(100*float(len(Feature_Referral))/float(StartedTrialCount))[:5]))

print "Fully Engaged (Control): %d (%s%%)" % (len(fullyEngaged_Control), (str(100*float(len(fullyEngaged_Control))/float(StartedTrialCount))[:5]))
print "Fully Engaged (Test): %d (%s%%)" % (len(fullyEngaged_Test), (str(100*float(len(fullyEngaged_Test))/float(StartedTrialCount))[:5]))
print "Fully Engaged (Overall): %d (%s%%)" % (len(fullyEngaged), (str(100*float(len(fullyEngaged))/float(StartedTrialCount))[:5]))