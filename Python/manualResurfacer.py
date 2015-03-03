# Be sure to 'pip install mixpanel-py' in your terminal before running this script. If you haven't installed Pip: https://pypi.python.org/pypi/pip
import mixpanel

from mixpanel import Mixpanel

PROJECT_TOKEN = raw_input("Project Token: ")
mp = Mixpanel(PROJECT_TOKEN)

event = raw_input("Event Name to Resurface: ")
propsDecision = raw_input("Do you need to resurface certain properties as well (Y/N)? ")

props = False

if "Y" in propsDecision or "y" in propsDecision:
	props = True
	propsDict = {}
	stopAddingProps = False
	while not stopAddingProps:
		prop = raw_input("Property to resurface: ")
		propVal = raw_input("Desired value: ")
		propsDict[prop] = propVal
		continuer = raw_input("Add more properties (Y/N)? ")
		if "N" in continuer or "n" in continuer:
			stopAddingProps = True

if props:
	print "Tracking the %s event with the following property dictionary: %s" % (event, propsDict)
	mp.track(0, event, propsDict)
else:
	print "Tracking the %s event" % (event)
	mp.track(0, event)

print "Done!"