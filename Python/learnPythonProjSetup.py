# -*- coding: utf-8 -*-
import json
import os
import random
import time
import operator
import base64
import urllib
import eventlet
import hashlib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

print """
Welcome to the Python Newbie's Guide to Mixpanel Data Manipulation!
This is the setter-upper for the test data you'll use in this 
exercise. Please create a fresh project and ensure all notifications
are disabled before running this script.

As a reminder, the customer request is to:
1) Create a CSV of the email addresses of users who opened 
notification #5309 AND/OR completed the "NEWSLETTER 53 Opt-In"
event.
2) Prepare a People Update textfile that adds a People Property of 
"Engaged" = true to those users.
3) Use people-importer to load these updates into the project.

Your deliverables are 1) the updated project, 2) a unified script
that fulfils these functions and 3) the people update textfile.
Good luck!
---------------------------------------------------------------------
"""

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
            event['properties']['time'] = str(int(event['properties']['time']) - (-28800)) #transforms timestamp to UTC
            if "token" not in event['properties']:
                event['properties']["token"] = self.token
            batch.append(event)

        payload = {"data":base64.b64encode(json.dumps(batch)), "verbose":1,"api_key":self.api_key}
        response = urllib2.urlopen(url, urllib.urlencode(payload))
        message = response.read()
        # print "Sent 50 events on " + time.strftime("%Y-%m-%d %H:%M:%S") + "!"
        # print message
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
                # print str(events) + "\n" + "Sent remaining %d events!" % len(events)

class Mixpanel(object):

    def __init__(self, api_key, api_secret, token):
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = token

    def request(self, params, format = 'json'):
        '''let's craft the http request'''
        params['api_key']=self.api_key
        params['expire'] = int(time.time())+600 # 600 is ten minutes from now
        if 'sig' in params: del params['sig']
        params['sig'] = self.hash_args(params)

        request_url = 'http://mixpanel.com/api/2.0/engage/?' + self.unicode_urlencode(params)

        request = urllib.urlopen(request_url)
        data = request.read()

        #print request_url

        return data

    def hash_args(self, args, secret=None):
        '''Hash dem arguments in the proper way
        join keys - values and append a secret -> md5 it'''

        for a in args:
            if isinstance(args[a], list): args[a] = json.dumps(args[a])

        args_joined = ''
        for a in sorted(args.keys()):
            if isinstance(a, unicode):
                args_joined += a.encode('utf-8')
            else:
                args_joined += str(a)

            args_joined += "="

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

    def unicode_urlencode(self, params):
        ''' Convert stuff to json format and correctly handle unicode url parameters'''

        if isinstance(params, dict):
            params = params.items()
        for i, param in enumerate(params):
            if isinstance(param[1], list):
                params[i] = (param[0], json.dumps(param[1]),)

        result = urllib.urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])
        return result

    def update(self, userlist):
        url = "http://api.mixpanel.com/engage/"
        batch = []
        for user in userlist:
            tempparams = {
                    'token':self.token,
                    '$distinct_id':json.loads(user)['$distinct_id'],
                    '$set':json.loads(user)['$properties'],
                    '$ignore_time': 'true',
                    '$ip': 0
                    }
            batch.append(tempparams)

        #print "Deleting %s users" % len(batch)
        payload = {"data":base64.b64encode(json.dumps(batch)), "verbose":1,"api_key":self.api_key}

        response = urllib2.urlopen(url, urllib.urlencode(payload))
        message = response.read()

        '''if something goes wrong, this will say what'''
        if json.loads(message)['status'] != 1:
            print message

    def batch_update(self, filename):
        with open(filename,'r') as f:
            users = f.readlines()
        counter = len(users) // 100
        while len(users):
            batch = users[:50]
            self.update(batch)
            if len(users) // 100 != counter:
                counter = len(users) // 100
                # print "%d users left!" % len(users)
            users = users[50:]

def buildEvent(event, timeStamp, user):
    data = {}
    data["event"] = event
    data["properties"] = {}
    data["properties"]["time"] = timeStamp
    data["properties"]["distinct_id"] = user
    eventUp.write(json.dumps(data)+"\n")

def printKav():
    response = urllib2.urlopen("https://www.dropbox.com/s/8vblzwtka3yooc1/ascii.txt?dl=1")
    for line in response:
        print line,
        time.sleep(0.03)

dummyData = [ [ "Cheryl Stewart", "2655F861-E284-9B50-B24A-EE7A681FB62A", "Rewa", "2014-11-22", "sociis.natoque@metusIn.org", 0, 0 ], [ "Summer Valencia", "D3B88DB8-B385-9807-C4F7-52B8D32E71B7", "As", "2015-09-20", "consequat.purus@Phasellusvitaemauris.com", 0, 1 ], [ "Rahim Charles", "ACAEA184-EB95-334D-32FD-18BAD0DF0F20", "Granada", "2016-03-29", "purus@facilisiseget.co.uk", 0, 1 ], [ "Erasmus Dickerson", "AC189AAC-9D53-1524-AF1A-91FC7BE0B5CE", "Tiverton", "2015-04-25", "metus.vitae.velit@Quisque.net", 0, 1 ], [ "Reece Powell", "28AE8BF2-6CFA-E444-C46C-32624C9F24CF", "Port Harcourt", "2015-04-15", "lobortis@interdumfeugiat.co.uk", 1, 0 ], [ "Micah Neal", "5068339F-151E-E50F-0B69-AD3E84370E56", "Ucluelet", "2015-04-05", "porttitor.eros@sitametluctus.ca", 1, 0 ], [ "Winter Kirby", "2C3D14C0-5D0A-0A4B-9481-C00320EE152B", "Mandya", "2014-08-07", "Aenean.eget.metus@porta.com", 0, 0 ], [ "Clark Anderson", "622EFC8C-BB7F-57DD-FFBC-44226267A7C4", "Ponte San Nicolò", "2015-08-10", "Ut.semper.pretium@utcursus.co.uk", 1, 1 ], [ "Regan Roach", "6C6CD8D7-C774-5B41-F7A3-20AF0EB7ED20", "Châteauroux", "2014-01-24", "Aliquam.gravida.mauris@metus.net", 1, 0 ], [ "Raja Goodwin", "3B0FC1CB-E074-036D-F3FF-8FA6232A0E76", "Montaldo Bormida", "2015-07-21", "placerat.eget.venenatis@duiquisaccumsan.com", 1, 0 ], [ "Maggy Hines", "901A5664-45DF-31D5-9363-911621C41D20", "Slijpe", "2015-03-03", "sed.pede@augueporttitor.net", 1, 1 ], [ "Leonard Holden", "BC349B86-3112-7927-B7C5-3C05347E4DBB", "Turgutlu", "2014-08-21", "eu@at.co.uk", 1, 0 ], [ "Orla Leach", "DCD959B4-1853-1080-2723-ADDC8C0449BE", "Perth", "2015-07-16", "ipsum@vel.com", 0, 0 ], [ "Jade Armstrong", "605D6E77-5246-E988-D975-23693CCBC1F6", "Dreieich", "2014-01-01", "Integer@quisdiam.com", 0, 0 ], [ "Shafira Morris", "2175EF0A-79E0-509E-7D02-FD74901E5D04", "Fossato Serralta", "2014-07-09", "purus.Maecenas.libero@Uttinciduntvehicula.edu", 0, 1 ], [ "Martin Cooley", "A02EE531-C610-AEF1-D624-E2A2E53C2A2C", "Springfield", "2014-04-06", "In@tristiquesenectus.net", 0, 0 ], [ "Gil Black", "4F52523C-99F8-084F-B410-1A302BFF1529", "Farciennes", "2014-12-12", "posuere@augueeu.edu", 1, 0 ], [ "Kieran Pruitt", "87F19AAB-5405-44D8-12F3-73778C482523", "Lodine", "2015-11-17", "dolor@elitAliquamauctor.net", 0, 1 ], [ "Logan Harmon", "8D5C1797-4FF2-9ECF-3234-FA0B578C282F", "Whithorn", "2015-06-20", "consequat.nec@molestiepharetra.ca", 0, 0 ], [ "Jolene Fuentes", "3F286706-EEF8-D533-1BF0-3DD3F9F76EB0", "Itzehoe", "2014-11-09", "lectus@sollicitudinorci.org", 0, 0 ], [ "Velma Colon", "1CBE874E-013A-92E8-EAA0-4859922BFAD3", "Oklahoma City", "2014-10-30", "imperdiet.ullamcorper@sapien.ca", 0, 0 ], [ "Ahmed Carson", "0F78A64F-A3B0-C335-0CE1-5CE51A272233", "Miramichi", "2016-03-05", "molestie.orci@scelerisque.com", 0, 1 ], [ "Gillian Jenkins", "1142FD52-A506-F40C-7E5D-AD4745E35AC9", "Bad Ischl", "2014-06-30", "ante.blandit@Sed.edu", 1, 0 ], [ "Anika Mcguire", "C5E2D5D8-8947-F4A4-0A99-BBA033FFA9EC", "Baie-Comeau", "2016-03-07", "dictum@eu.com", 1, 1 ], [ "Nina Estes", "79B7937A-82FD-6BE6-46B0-C41EDD73BE23", "Vorst", "2015-11-23", "sagittis.felis.Donec@sempertellusid.org", 1, 0 ], [ "Denton Nieves", "145EF4C1-FD51-00E4-D846-ADED38941139", "Glendale", "2014-04-01", "erat@gravida.edu", 1, 0 ], [ "Dorothy Durham", "181A6583-4A95-3C2E-064B-A90CA390B0FA", "Maiduguri", "2016-03-02", "Pellentesque.ultricies.dignissim@loremtristiquealiquet.net", 1, 0 ], [ "Eleanor Atkins", "6C31BAAF-4880-043C-5C51-E026F351C2EB", "Tramatza", "2016-02-22", "urna.nec@Sed.com", 0, 1 ], [ "Peter Henson", "95163536-F2AF-1CEA-B8C6-F5F1E6E83144", "Carlton", "2014-03-18", "non.lacinia.at@mauriseuelit.net", 0, 1 ], [ "Randall Whitley", "7BD23BE8-553C-3FD0-CDF1-7012D6E382A5", "Merchtem", "2015-06-30", "morbi@elementumat.edu", 1, 1 ], [ "Gannon Greene", "D5137923-3B5E-E3E4-577B-E40B22D4B873", "Allentown", "2015-02-21", "facilisis.eget.ipsum@Nullafacilisis.edu", 0, 0 ], [ "Clayton Stanton", "A281ADD8-E08A-83F9-1439-21B09479BF88", "Borno", "2014-04-03", "sollicitudin@ante.ca", 1, 0 ], [ "Neville Weeks", "6A6A8653-976F-66D7-FD62-87A929B29E05", "Colico", "2014-03-21", "Sed@nisi.edu", 1, 1 ], [ "Clio Rice", "25121B14-681D-1C46-51A7-A4421CC3646D", "Rockford", "2016-02-04", "Sed.eu@ornareIn.co.uk", 0, 1 ], [ "Shaine Herrera", "C4EC4645-51D8-1CE8-92BE-04D24E768329", "Armadale", "2016-02-05", "sit.amet@anteblandit.edu", 0, 0 ], [ "Athena Giles", "F49E1D7A-D759-D9BC-8D7F-4F4AD0379942", "Colchester", "2014-09-29", "rhoncus@convallisligula.com", 0, 1 ], [ "Erica Moore", "EE96D2CE-39F8-B314-53FD-6370A3D4E133", "Coatbridge", "2014-01-10", "auctor.velit.Aliquam@ridiculus.edu", 1, 1 ], [ "Lillith Sanchez", "5A5E9410-B763-7265-1E06-CA7CEE99D789", "Baie-Saint-Paul", "2014-06-01", "accumsan@nisiAeneaneget.net", 1, 1 ], [ "Dustin Riggs", "C3F1B929-CC17-48DD-DF67-22028CBC3ADD", "Tuscaloosa", "2014-07-31", "tellus.non.magna@atortor.com", 0, 0 ], [ "Robin Moran", "42DD62C0-5B41-D0A7-6788-D666475F6902", "Carleton", "2016-02-19", "elementum.dui.quis@Etiamvestibulummassa.net", 0, 0 ], [ "Tatyana Valdez", "32BF9826-E741-6FDD-A678-77184C28EDF1", "Burhaniye", "2015-03-24", "et.magnis.dis@atarcuVestibulum.net", 0, 1 ], [ "Merritt Clements", "E01E8435-9438-8535-D6B4-CC8048C2411A", "Cuglieri", "2015-04-18", "non.luctus.sit@iaculis.com", 1, 1 ], [ "Len Hardy", "4EC2D843-29ED-8E12-743D-F45B64F4B9F3", "Panihati", "2015-05-12", "Curae.Donec.tincidunt@sempertellusid.edu", 0, 0 ], [ "Serina Camacho", "A84A81BE-BABB-F744-F082-ED2D119E5D06", "Albiano", "2014-09-26", "neque.tellus.imperdiet@lorem.com", 1, 1 ], [ "Winifred Ray", "B91FC2C3-4C9A-B82C-39A3-5756546F01F9", "Tucson", "2015-05-15", "Quisque.purus.sapien@pharetraNamac.org", 1, 0 ], [ "Athena Dyer", "180208F5-39B2-AF6A-2A99-51C83AD58ABF", "Montgomery", "2014-06-29", "lorem@lobortisrisus.edu", 1, 1 ], [ "Mikayla Pace", "2FF6A293-D11A-4CA0-B709-DA4BBEFE8CFD", "Bouffioulx", "2014-03-21", "ligula@amet.com", 0, 0 ], [ "Fitzgerald Gilliam", "61733ADD-C4B8-CB22-54CB-AB475F3FB005", "Roccabruna", "2015-12-23", "ipsum.Suspendisse.non@Quisquefringillaeuismod.net", 1, 1 ], [ "Allen Cochran", "F3548D80-BF53-0EE1-B3FB-4B87D34A4C96", "Notre-Dame-du-Nord", "2014-10-29", "conubia.nostra.per@iaculis.ca", 0, 1 ], [ "Iliana Carver", "1249409F-82AD-564F-319A-FE9211854FCA", "San Maurizio Canavese", "2015-05-21", "aliquet@lobortisrisus.com", 0, 1 ], [ "Destiny Peck", "77A1AC27-AC11-1F7C-6A0C-C92A30494119", "Alkmaar", "2015-06-05", "mauris.Suspendisse@semmollisdui.com", 0, 0 ], [ "Kennedy Cervantes", "E3482434-F5B5-063F-F7F2-7D802DEF3FDB", "Glasgow", "2015-03-20", "vehicula@sed.org", 1, 0 ], [ "Dominique Bolton", "58C5A61A-563F-936C-5510-ED69C4944BED", "Habergy", "2014-02-10", "dictum.augue.malesuada@eunullaat.ca", 0, 1 ], [ "Remedios Cox", "BE2FDA3F-C2C3-BF88-1AAE-BBBE35826A4E", "Anthisnes", "2015-04-08", "erat@vitaeerat.net", 1, 1 ], [ "Eugenia Mcmillan", "3C21F1C2-449A-1676-0FEB-38C862EE4B5C", "Prenzlau", "2014-06-27", "euismod@sedestNunc.com", 1, 1 ], [ "Dexter Farmer", "E9944749-CF77-5B58-0158-FF493ADAE7F4", "Gavirate", "2014-05-05", "ipsum.Donec.sollicitudin@ut.org", 1, 0 ], [ "Chaim Boyle", "F55340E2-A844-F13F-F210-73AC27C621E0", "Nemoli", "2014-10-17", "orci.adipiscing@nequesed.ca", 0, 0 ], [ "Kirby French", "7EC73723-6321-3CCA-2407-A49FED0A5CA7", "Stirling", "2014-08-30", "mi.ac@nonleoVivamus.ca", 1, 1 ], [ "Sandra Weber", "25C611BB-7A54-66BC-1450-2828B92BAB2B", "Otranto", "2015-05-18", "at.sem@imperdietullamcorperDuis.org", 0, 0 ], [ "Briar Koch", "FE2AC00C-4E1A-BACF-85EA-05467D47A5A1", "Sint-Lambrechts-Woluwe", "2014-04-13", "amet@necmollis.org", 1, 1 ], [ "Nolan Hughes", "BE604724-54ED-993B-0161-7A362E860171", "Waidhofen an der Ybbs", "2015-03-09", "rhoncus@Phasellusdolor.org", 1, 1 ], [ "Thomas Brock", "A036372E-8B8C-7404-C3F9-0B7C34526B5F", "Bikaner", "2014-06-25", "mattis.Cras@tempor.edu", 1, 1 ], [ "Kelly Drake", "A2DC50DA-BF5F-8F14-A1D6-1D9CED7F67B9", "Glasgow", "2014-10-03", "lorem.ac.risus@nasceturridiculusmus.edu", 1, 1 ], [ "Sydney Yates", "3371B9A3-7AF4-591B-B23F-0573D71AF170", "Milwaukee", "2015-10-10", "at.velit@ligula.net", 0, 0 ], [ "Jillian Kerr", "1F60214D-5BE0-EC60-DD38-55A07BF681AB", "San Piero Patti", "2014-04-21", "mus.Proin@Cumsociisnatoque.com", 1, 1 ], [ "Lance Fischer", "D1DB7C62-08CA-F5D0-B02F-1B9EBE273DD0", "Roermond", "2014-06-29", "felis@justo.com", 0, 1 ], [ "Vernon Boyer", "1A6A8552-B837-42EE-72CD-5B8C3DDEDE4D", "Mainz", "2014-05-09", "non.sapien@sem.org", 1, 0 ], [ "Sheila Mcdaniel", "0B27B2B1-4B0E-DE39-6624-094FEE746B06", "Castelluccio Valmaggiore", "2014-05-30", "arcu@placerateget.ca", 1, 1 ], [ "Leilani Shepard", "0A942315-768D-F7ED-5082-8DA330E764DF", "L�rrach", "2015-10-30", "Morbi@ipsumSuspendissesagittis.org", 1, 1 ], [ "Callie Webster", "9B1818D1-6841-F312-66EE-20B596480675", "Trier", "2015-10-04", "Morbi.quis@mus.net", 1, 0 ], [ "Preston Roman", "104BAD9E-BA67-2EED-92F5-78365ED6901E", "Oswestry", "2014-10-01", "dolor.Nulla@temporaugueac.net", 0, 0 ], [ "Deborah Chang", "65C86356-D52F-9EB1-D725-65000A19D0A3", "Baltimore", "2014-12-25", "velit.justo@erosProinultrices.org", 1, 0 ], [ "Callum Wheeler", "F50A4543-1BC6-73AF-CDE4-60C24F1297CC", "Heusden", "2014-08-12", "vehicula@Etiamimperdietdictum.edu", 0, 1 ], [ "Tanner Willis", "51770B87-6835-EBF4-6E3D-057F99606610", "Bielefeld", "2015-01-08", "Pellentesque.tincidunt.tempus@consequat.co.uk", 0, 0 ], [ "Ivana Cotton", "D47EE2D6-A188-66EF-5928-C09A12A9EFB6", "Hulshout", "2015-05-09", "consequat@nonquamPellentesque.co.uk", 0, 1 ], [ "Tanner Sykes", "78EBC05E-2A9D-0485-56F8-205CC796AA35", "Kakisa", "2014-12-22", "arcu@aodiosemper.org", 1, 0 ], [ "Medge Albert", "EA3D2084-87AF-CCC3-3860-1934B141C637", "Rocourt", "2014-04-07", "ac.sem@orcilobortisaugue.edu", 1, 0 ], [ "Liberty Mejia", "148C91DC-BED9-6ACB-C4A4-0A55F233F60C", "Pocatello", "2014-11-11", "arcu.Sed@nisl.org", 1, 1 ], [ "Jonas Contreras", "A772774E-8DBE-8B25-3F39-639A5DA94130", "Arnesano", "2014-02-26", "malesuada.ut@augueid.com", 0, 0 ], [ "Rooney Mccray", "00F445E0-DD2B-383C-5606-B010ADB91DA6", "Arsiè", "2014-07-21", "auctor@placerat.net", 1, 0 ], [ "Denise William", "9325510C-8948-768D-9E97-75F272444DAA", "Herstappe", "2015-04-05", "primis.in.faucibus@Aeneangravidanunc.com", 0, 1 ], [ "Macy Michael", "D94A070C-AA9A-E052-966D-CB5C0B80C70B", "Iqaluit", "2015-10-01", "dolor.quam.elementum@porttitor.net", 0, 1 ], [ "Sylvia Francis", "4AED7B9A-5DA6-4B06-4094-C863DC71A9F6", "Boneffe", "2016-02-24", "cursus.purus.Nullam@ametloremsemper.com", 1, 1 ], [ "Angela Finley", "30AACF9D-70B5-1EE8-740D-DD508B6B5ED1", "Georgia", "2015-07-26", "primis.in@temporbibendum.edu", 0, 1 ], [ "Kennedy Pollard", "6F82143A-36AD-2B6A-10DA-A430E43374F4", "Montalto Uffugo", "2015-04-02", "Etiam.laoreet@Nullamvitaediam.edu", 1, 1 ], [ "Alvin Hansen", "C95CC8B1-10D9-13FE-FA24-562C8A529FB5", "Markham", "2016-03-26", "nulla.vulputate.dui@ac.org", 1, 1 ], [ "Maxine Witt", "59A4BDFF-E2CC-1893-55BB-5A94C3947DF5", "Osimo", "2015-11-26", "ad.litora.torquent@Fuscemollis.net", 1, 1 ], [ "Elmo Bullock", "43E8B176-F72D-DFFE-37F6-ABB07AE619BC", "Sivry-Rance", "2014-02-09", "nonummy@sagittis.org", 0, 0 ], [ "Cailin Arnold", "6D4E7371-3FE2-A3FB-05AC-A79D5EC1EEE3", "Ottawa-Carleton", "2015-09-23", "tincidunt@eliterat.net", 0, 1 ], [ "Jarrod Rice", "2C3F6B7D-E134-D66E-65D1-A53B9229137A", "Nieuwerkerken", "2014-04-17", "ullamcorper.Duis.at@ametconsectetueradipiscing.net", 0, 0 ], [ "Quinn Allen", "CEDA6D32-948E-E2FA-4C90-BCC2954590AF", "Bolano", "2014-03-16", "lacus.Ut.nec@pedenec.co.uk", 1, 0 ], [ "Isadora Mcintosh", "5D434A11-86C0-F48F-7D2E-0E35F004F498", "Orp-Jauche", "2014-09-19", "orci@Aliquamerat.edu", 0, 0 ], [ "Debra Crane", "CA94658E-C0AE-C666-8265-7DB77967AAD9", "Marseille", "2014-12-31", "egestas@pharetra.net", 0, 0 ], [ "Harper Gross", "38479BAE-7854-BE40-1F37-1C4EB17AC361", "Liverpool", "2015-11-16", "Cras@tellus.edu", 0, 0 ], [ "Olga Obrien", "676D4E1A-B226-419A-F4B0-C73306506536", "Casper", "2015-06-07", "Donec.nibh@semvitaealiquam.edu", 1, 0 ], [ "Seth Cotton", "DD95DB77-10A9-8A04-A285-FBB317662212", "Skegness", "2014-03-26", "lobortis@non.org", 1, 0 ], [ "Quintessa Crosby", "F6FBA9E2-3606-4718-2B75-BDD21D3E539B", "St. Petersburg", "2014-07-03", "iaculis.odio.Nam@at.com", 0, 1 ], [ "Lillian Bradford", "AE4FB848-2905-C8CF-16B0-FBB9BA934555", "Saint-L�onard", "2014-09-07", "libero@Duisa.net", 0, 1 ], [ "Kato Grant", "FB1AB5A6-3995-DD51-9915-BD0E9A983C38", "Aartrijke", "2014-05-23", "erat@euplacerateget.co.uk", 1, 1 ], [ "Silas Gardner", "AC17FF82-B41F-CF12-EA97-CB903FA2AABF", "Sperlinga", "2015-04-25", "Proin.velit@eu.ca", 0, 0 ], [ "Sawyer Mccarty", "238DF914-783B-0938-6AB4-6DCB3FD55A83", "Caen", "2016-02-28", "dis.parturient@semperegestas.edu", 0, 1 ], [ "Phoebe Clay", "6ED75436-9783-588F-7461-C5137D8D8F65", "Minucciano", "2015-11-07", "lobortis.nisi@loremauctor.com", 0, 0 ], [ "Eric Alston", "91755C73-22BF-2D8E-5F16-4869B7A13F21", "Gambolò", "2014-07-13", "pede.et@sagittissemper.ca", 1, 1 ], [ "Kirestin Cotton", "0810FDA2-706B-4DDB-92F1-3DB75D1864BC", "Brindisi", "2014-04-24", "Nunc.ut@Aliquamtinciduntnunc.org", 0, 1 ], [ "Neve Foley", "FF74F803-A2CD-F324-385F-9272D618887E", "Wabamun", "2015-08-12", "Curabitur.ut@Sedegetlacus.org", 0, 0 ], [ "Danielle Ayers", "6BCE9CB8-D0D7-BAF4-8544-FFA82DC53938", "Dundee", "2014-09-27", "vestibulum@facilisisSuspendissecommodo.edu", 0, 1 ], [ "Penelope Bryan", "B2AC1508-1408-AC3E-3AD9-76E6F0AD1073", "D�sseldorf", "2014-05-22", "aliquet.Phasellus.fermentum@semegestasblandit.edu", 1, 0 ], [ "Rhoda Long", "318408C1-6446-0167-1C39-CCADBD38655B", "Outrijve", "2015-09-13", "molestie.dapibus.ligula@nec.ca", 0, 1 ], [ "Jenette Gallagher", "3A2775FE-5D49-3A4C-CD3E-F1119C598045", "Vergemoli", "2014-12-18", "a.malesuada.id@ipsumSuspendissenon.net", 1, 0 ], [ "Richard Maddox", "5A3E74BD-1C3B-D95B-D89E-E3508769F1BF", "Fishguard", "2015-06-18", "Curabitur.dictum.Phasellus@mattisInteger.co.uk", 1, 0 ], [ "Oscar Campos", "0DFF4A15-D8DC-FFCA-A715-F2C0EB34A1F0", "Baltasound", "2015-02-28", "fringilla@amet.ca", 1, 1 ], [ "Martina Whitney", "53DD6ACA-F3C0-E557-9002-523D03DB8D31", "Wasseiges", "2016-03-03", "scelerisque.scelerisque.dui@odioEtiam.com", 0, 0 ], [ "Veda Freeman", "477D1545-0CE0-0033-BDC8-6072BC42AB03", "Louveign�", "2015-05-13", "id@facilisisfacilisis.com", 0, 0 ], [ "Xenos Hayes", "5E52D1E9-FD62-6DF9-9859-92F4418E9549", "Pergola", "2016-02-12", "non@laoreetliberoet.com", 0, 0 ], [ "Mira Wilkerson", "D68E5560-1AE9-97CB-906E-52E72580D544", "New Orleans", "2015-12-09", "lobortis.augue@loremauctor.co.uk", 1, 1 ], [ "Abel Fitzgerald", "4AAFA762-295E-B991-F3A2-0AD27EBCF1C6", "March", "2014-06-14", "urna@velitSed.com", 0, 0 ], [ "Regina Lester", "7A221B06-DB9F-0C29-CE97-E9F4E12EE479", "Brive-la-Gaillarde", "2014-09-23", "arcu.eu@enimconsequat.ca", 0, 0 ], [ "Heidi Daugherty", "4F0A1C4B-3875-6672-8D32-44A219FB3E2F", "Gary", "2015-04-19", "lorem@nequesed.org", 1, 1 ], [ "Shana Woods", "25DCE78F-29F9-6961-8455-171F33CA554C", "Cumbernauld", "2015-07-30", "et.netus.et@enimEtiam.com", 1, 0 ], [ "Marny Foster", "83F6F2D0-5F2E-DBF1-7B8A-5AFA623DF3B1", "Kansas City", "2014-02-08", "a@ullamcorperDuis.edu", 1, 1 ], [ "David Haley", "1DA53E94-91C4-A9A7-C16A-4072F9F1B21B", "Drongen", "2014-12-21", "mollis.Integer.tincidunt@dignissim.edu", 1, 1 ], [ "Constance Calderon", "A5F9016C-86CB-4958-D0CB-1026389B6318", "Ketchikan", "2014-05-22", "risus@convallis.net", 0, 1 ], [ "Josephine Williams", "E5420ACC-6B71-BEBE-4FC6-C8A596AF31A7", "Kuurne", "2015-12-13", "ac.nulla.In@duiin.edu", 0, 0 ], [ "Carly Chen", "136588AA-CEE8-03CF-966A-F237205F6342", "Izel", "2014-04-07", "eu@interdumCurabiturdictum.net", 1, 0 ], [ "Delilah Diaz", "34882004-404E-5B07-9DD5-0F80E7399D6D", "Sagamu", "2015-03-29", "metus@vulputateposuerevulputate.edu", 0, 1 ], [ "Yoko Best", "8257DE82-3231-51DC-EEA0-0DB919AD849C", "Hull", "2014-04-18", "Pellentesque.habitant@cursusNuncmauris.net", 0, 1 ], [ "Jin Pitts", "3D6AA56F-9B7A-46B3-D4EC-C4A3ABFE1124", "Lampeter", "2014-05-28", "convallis.convallis@egestas.co.uk", 1, 1 ], [ "Grady Shepherd", "00D437A4-6A4B-50D6-D3D0-BDC51C89F144", "Herstappe", "2014-10-13", "ornare@Etiam.edu", 1, 0 ], [ "Victoria Owens", "7262D453-64B9-8CF6-C741-B4594EF040C0", "Versailles", "2015-09-22", "auctor.odio@Sedeu.com", 1, 1 ], [ "Felix Allen", "FC6415AC-6A3F-533E-7329-4EAB6150AB82", "Maintal", "2014-01-02", "sagittis.Duis@etrutrumnon.net", 0, 1 ], [ "Paul Mcclure", "EC142726-7377-7BEB-7DA7-813AD48E3CD0", "Bornival", "2014-02-02", "Integer@euaugue.co.uk", 1, 0 ], [ "Lara Wright", "8C182A26-BA2E-AA4E-4B58-D07B58CDC5EE", "Herenthout", "2014-06-12", "Sed.auctor.odio@tempusscelerisquelorem.co.uk", 1, 0 ], [ "Linus Stuart", "DF2288E8-4393-8F3D-DDD0-D498E941B420", "Ceppaloni", "2015-01-27", "est.vitae.sodales@dignissim.org", 0, 1 ], [ "Xantha Rich", "548E38DA-8762-E8BC-2720-022471F618A1", "Ilesa", "2014-07-08", "a@vestibulummassa.com", 1, 0 ], [ "Dominique Roth", "339B58A0-C287-87BA-FF5D-D90808C0CD3D", "Bhiwandi", "2014-08-15", "tempor.arcu@facilisisvitae.co.uk", 0, 0 ], [ "Jackson Hayes", "470BF30F-D160-C9C0-E6FE-1FFB7D66B2C0", "Melsbroek", "2014-06-03", "Nulla.facilisi.Sed@quis.ca", 0, 0 ], [ "Curran Stanley", "9D9A91F3-B040-2F30-5CF0-073CB420C8BB", "St. Paul", "2015-08-23", "justo.Proin.non@lacinia.net", 1, 1 ], [ "Leonard Wilkerson", "546DCE24-A841-C1AC-A5BC-E1EBE8401CEA", "Barasat", "2015-11-18", "nec@sitamet.org", 0, 0 ], [ "Rose Sears", "EFF51A4B-E17C-20F6-B64D-6397BB233D6D", "Lochranza", "2014-03-26", "nec.tempus.scelerisque@magnased.com", 0, 0 ], [ "Lacota Kramer", "25C908F8-4DB8-CFD7-F014-47CBE50EBECE", "Montpellier", "2015-01-12", "neque.In.ornare@Vivamussit.org", 0, 0 ], [ "Axel Stafford", "252FD2EC-5861-6B6F-262F-96FC14E1CA2A", "Tillicoultry", "2015-01-28", "urna.Vivamus@gravida.com", 1, 1 ], [ "Sophia Yang", "5064639E-C6C6-4CF6-1BF9-CE0FB8C9680F", "Stamford", "2015-01-18", "eget@nectempus.com", 0, 0 ], [ "Whoopi Sawyer", "E9C2B231-DF1B-F855-AD17-237002414842", "Firozabad", "2014-03-27", "condimentum@ultriciesadipiscing.ca", 0, 1 ], [ "Dai Blevins", "788F9CA9-57BF-DB35-3020-FE9A0EAA2E0B", "Maisi�res", "2015-04-04", "magnis@erat.net", 0, 0 ], [ "Thane Meyer", "1DD3658C-CD80-6492-003A-CEE68EA4FD0A", "St. Thomas", "2015-07-20", "sed.facilisis@dictumeuplacerat.net", 1, 1 ], [ "Ifeoma Hoffman", "7C897605-F47E-D0C2-E28A-4C6FDAC53BDB", "Pretoro", "2014-08-10", "in@Namac.org", 1, 1 ], [ "Judah Haley", "2AC6F6BC-E039-AC19-1DDD-944C0A0D61DA", "Sant'Eufemia a Maiella", "2014-09-14", "molestie.orci.tincidunt@turpisnec.ca", 1, 0 ], [ "Kimberly Sweet", "6CE87350-7F34-C067-0993-1D1506866988", "Lapscheure", "2015-06-19", "tellus@orciluctuset.co.uk", 1, 0 ], [ "Cruz Lindsey", "C4325BDD-544F-BB98-1A20-1418FFCABF2A", "Denver", "2014-04-24", "in@convalliserat.edu", 1, 0 ], [ "Dai Spencer", "2D5944A4-B27B-2A7F-7295-4FAACADD6C7C", "Caplan", "2015-09-13", "hendrerit@mi.com", 0, 0 ], [ "Natalie Reed", "88DC338C-DF94-1FA7-589E-79362E340B98", "Fogo", "2014-06-24", "mauris.sit@Donec.ca", 1, 1 ], [ "Laurel Carey", "A5E7B504-8B9A-96A9-FDDF-C28129DA7605", "Saint-Vincent", "2014-06-22", "Sed.eu.eros@NulladignissimMaecenas.edu", 0, 1 ], [ "Clayton Meyers", "B5EFEBC7-6E23-E4AF-313F-0457EFAB4444", "Tulita", "2014-02-04", "dui.lectus.rutrum@nibh.org", 1, 1 ], [ "Kimberley Cotton", "099842C8-DBBC-F63F-11CE-DA648F34DB1B", "Didim", "2016-02-22", "Curabitur.ut.odio@in.net", 1, 0 ], [ "Rogan Turner", "AD03E2FE-8B57-57B2-4E50-18D40CBA9F49", "Susegana", "2014-04-08", "arcu.Nunc@arcuVestibulumante.com", 1, 1 ], [ "Rigel Moreno", "0CD52126-FFB4-B506-923B-1E00BAF68378", "Somma Lombardo", "2015-10-10", "sed.pede@tellusnonmagna.co.uk", 1, 1 ], [ "Yael Puckett", "4B1F43F9-C494-8820-1E72-8546C39A54AF", "Flawinne", "2015-04-03", "Praesent@acmattisornare.co.uk", 1, 0 ], [ "Uta Livingston", "948CC0B1-1B19-C253-84DF-B4F77AB05CF4", "Barchi", "2015-12-29", "justo@rhoncus.net", 0, 0 ], [ "Richard Webb", "1AEADAA6-8BBA-3834-408A-99647446EE87", "Hay River", "2014-11-02", "ac.mattis.ornare@Phasellusvitaemauris.co.uk", 1, 1 ], [ "Halla Fletcher", "D4DC04B6-99EF-52FB-7990-FAF350D0F532", "Donk", "2015-03-04", "id.ante.Nunc@amet.co.uk", 1, 0 ], [ "Alyssa Nguyen", "E34FD8F3-60BA-73D3-D634-050F89C6BBD7", "Cleveland", "2016-02-15", "rhoncus.id@dictum.co.uk", 0, 1 ], [ "Teagan Burks", "91ECAC5D-ED58-F1A3-0BB7-2F0A0CD7FE37", "Kimberly", "2015-11-30", "ad.litora.torquent@at.ca", 1, 1 ], [ "Linus Sargent", "7FA35736-9206-0D2F-59DE-5B2FED88AAB3", "Bonlez", "2014-12-02", "id@fermentum.ca", 0, 0 ], [ "Joan Adkins", "634EA2E8-18C7-A667-150F-7118EE00C0A5", "Orai", "2014-12-30", "Integer.vulputate@lobortisultricesVivamus.co.uk", 0, 1 ], [ "Brock Callahan", "C9CF2636-562C-801C-7BD6-8A0379FBDF75", "Minucciano", "2015-05-12", "auctor.nunc@nisisemsemper.com", 1, 0 ], [ "Blossom Patton", "496D7014-06F4-26F4-8D6C-BD7E06371AA6", "Gander", "2015-03-06", "tellus.sem.mollis@elit.net", 0, 0 ], [ "Vaughan Paul", "5274427A-0AB1-1E01-BF93-64A174BA2645", "Evansville", "2014-01-31", "libero.Morbi.accumsan@Sedmalesuada.org", 1, 1 ], [ "Nicholas Carver", "0188E9B1-CF56-B629-AC70-12CD0554F81C", "Anghiari", "2014-05-18", "rutrum.Fusce.dolor@pedenonummyut.ca", 0, 1 ], [ "Basil Henry", "F12F3BF3-0E88-6FBE-5790-25CD4C7497C5", "Rochester", "2015-11-02", "amet.diam@libero.net", 1, 1 ], [ "Lesley Pearson", "9B5B5D0D-9B86-ACC9-4CD2-56347559301B", "Titagarh", "2015-11-19", "posuere.cubilia.Curae@lectus.com", 0, 1 ], [ "Chandler Berry", "A247DA24-D186-DE4E-D56C-D2D7B5C5E26E", "Luik", "2016-03-15", "turpis@etmalesuada.ca", 0, 0 ], [ "Halee Taylor", "E70ACD88-B08D-4035-60D4-2528E48633DD", "College", "2016-03-17", "nisi.dictum@tinciduntvehicula.net", 0, 1 ], [ "Karyn Washington", "E5F1BC1D-5076-F7B2-08C9-7D9B6C37082F", "Kallo", "2014-01-31", "commodo@ipsumacmi.ca", 1, 0 ], [ "Jordan Heath", "6718F061-9493-C4F7-3FEF-64AC7C605D0F", "Grand Falls", "2015-03-22", "mollis@nec.edu", 1, 0 ], [ "Zenaida Hardy", "F3580EC3-7EF2-45C7-DD76-2D48918219D9", "Bordeaux", "2014-07-11", "Curabitur.egestas@Maurismagna.ca", 0, 0 ], [ "Odette Robles", "0C8E60A7-7700-6058-9573-DB1D6D3AF023", "Gasp?", "2015-11-20", "tortor@ut.ca", 0, 0 ], [ "Nissim Cohen", "671FCF2D-2853-498B-6EC9-5E2140DA420C", "Sete Lagoas", "2014-03-28", "dapibus@enimdiam.com", 0, 1 ], [ "Sopoline Padilla", "684E9173-94D4-BC0A-9195-4D99CB8E1A7F", "Nasino", "2014-03-21", "eu@vehicula.net", 0, 1 ], [ "Eric Koch", "3EDBC407-4A89-E165-B3FE-E0DAB752696C", "Viranşehir", "2015-07-25", "commodo.at@Maecenas.co.uk", 0, 0 ], [ "Nolan Allen", "AD80FD99-2AD6-D5BC-6344-0A7A365912DC", "Siedlce", "2015-05-29", "et.euismod.et@risusIn.ca", 0, 0 ], [ "Jasper Ruiz", "6250777E-D34F-27CB-816F-F11440F40891", "Motherwell", "2016-01-24", "metus.vitae.velit@feliseget.com", 0, 0 ], [ "Bianca Sparks", "BF28E349-F457-3EE7-5C4E-F57CF950A201", "York", "2014-08-23", "tempor@Curabitur.edu", 1, 1 ], [ "Allen Walter", "5F0D0397-C9AF-9A29-A72D-5B52FFABBC23", "Glenrothes", "2014-06-30", "pede@scelerisque.net", 0, 0 ], [ "Knox Richard", "6C1169C3-FAA2-EAF6-1FC9-7EF593F87A37", "Edremit", "2014-12-24", "sed@Duis.co.uk", 0, 1 ], [ "May Villarreal", "23A74D9F-54FF-9BEC-3727-58808EB8CAA1", "Dorval", "2016-03-10", "eget.ipsum.Donec@eros.edu", 1, 1 ], [ "Jesse Stanton", "C01F110D-E43E-E2D1-8A96-3AFA0EC7006C", "Tranent", "2015-10-15", "tincidunt.orci.quis@pedeet.com", 1, 0 ], [ "Carol Carroll", "99C8EBE8-DACF-F5AF-010A-18BEFCBA0D83", "Neder-Over-Heembeek", "2014-08-30", "feugiat.metus@nulla.org", 0, 1 ], [ "Germane Mcgee", "251A2C93-1397-F7E6-F4E0-8C43F9F1E3C0", "Ukkel", "2015-09-16", "tristique.pharetra@risusatfringilla.net", 1, 1 ], [ "Tanner Henson", "73A8654B-62B0-D915-3A82-CC47BF94D772", "Neubrandenburg", "2014-09-03", "ultricies.sem@risus.edu", 0, 1 ], [ "Nigel Molina", "500912E1-5820-1728-36E9-5BB3AEE062ED", "Rovereto", "2015-02-18", "nascetur.ridiculus@volutpat.org", 0, 1 ], [ "Conan Hawkins", "7019AC8F-F052-62B5-23F3-B53CE33FF21D", "Spy", "2016-03-25", "turpis.Aliquam@Nullamsuscipitest.com", 1, 0 ], [ "Brent Foster", "C17E7BD1-2C10-DC8E-3FAF-08DF4CC41FD5", "Comano", "2014-03-08", "nec@ornareIn.org", 0, 0 ], [ "Mechelle Hayes", "546E6B15-0660-D9C8-57A4-C3B43C25E344", "Motta Sant'Anastasia", "2014-01-17", "vitae@commodoipsumSuspendisse.edu", 0, 0 ], [ "Sonia Cabrera", "5DB5210E-F2D1-C2B9-6A00-9B8A918F8E0C", "Queenstown", "2014-09-18", "eu.ligula@auctornuncnulla.ca", 1, 1 ], [ "Jessamine Tucker", "B9F2C0CF-A27A-6225-A4FA-C9D2CB4D038A", "Lapscheure", "2015-08-18", "metus.facilisis@nonsollicitudin.net", 1, 0 ], [ "Ebony Whitley", "90024A37-FFD7-52B7-78E9-450ECB85B994", "Mataró", "2014-11-06", "metus.Aenean.sed@nequeNullamnisl.co.uk", 1, 0 ], [ "Camilla Scott", "25AACC03-FA1B-C876-ECF8-D911A69D9CEA", "Rhemes-Saint-Georges", "2015-05-02", "Nunc.ac.sem@Integeridmagna.net", 1, 0 ], [ "Jolie Witt", "B6123C24-DF32-BEAA-6B99-BBC2A97B24C9", "Conca Casale", "2015-12-24", "nisi.Cum.sociis@ligulaNullamenim.ca", 1, 1 ], [ "Evangeline Hurst", "2715FB76-69F5-D43B-6C58-AA5717CA269B", "Delhi", "2015-08-12", "magna.malesuada@felisadipiscingfringilla.com", 1, 1 ], [ "Ivor Newton", "1F6E2076-4C12-A95F-BC4D-569510C23D0F", "Ghlin", "2014-11-06", "hymenaeos.Mauris@turpisNulla.net", 0, 0 ], [ "Leonard Combs", "91D99D09-B4E6-D660-33F6-3213761562C6", "Sint-Kwintens-Lennik", "2015-10-11", "tellus.Suspendisse@pedeultrices.com", 1, 0 ], [ "Vance Gentry", "DCEE19F0-6386-83D2-B5BA-8094957352AB", "Muzaffargarh", "2014-06-05", "purus.Duis@aliquet.net", 0, 1 ], [ "Yoshio Pickett", "ED998645-DEE0-868F-F53C-17AEB9FF182F", "Castello Tesino", "2015-02-20", "dolor.vitae.dolor@faucibusorciluctus.com", 1, 1 ], [ "Christine Holloway", "9750F123-DB99-34C0-94C5-77C5EBDB0793", "Asigliano Veneto", "2014-06-04", "parturient.montes.nascetur@veliteget.co.uk", 0, 0 ], [ "Price Kelley", "CF5CC0E6-42E4-76E8-8272-8B84675DA1D4", "Siculiana", "2015-06-21", "ut.molestie@uteratSed.edu", 1, 1 ], [ "Mari Nieves", "531CCC89-7EA4-D5E8-AF57-AFDE35260807", "Mackay", "2014-02-20", "euismod.mauris@tempus.edu", 0, 0 ], [ "Amelia Abbott", "D89195E6-B9F9-0DAC-82F6-B9F18433EF76", "Otegem", "2014-12-29", "est.ac.facilisis@Donecsollicitudin.com", 1, 0 ], [ "Ifeoma Holmes", "82CE6633-112C-EFED-B778-2D26025E2B37", "Pastena", "2015-07-26", "ullamcorper.eu@Morbi.net", 1, 0 ], [ "Ava Gould", "D14D75ED-13E7-69F9-A08A-CD4768949903", "Leduc", "2014-05-24", "adipiscing.fringilla@Donecvitae.net", 1, 0 ], [ "Callie Bowers", "14C11A46-181F-D52C-B111-CDE680FF2913", "Bazel", "2015-07-20", "sed@nullaIn.co.uk", 0, 1 ], [ "Fleur Walton", "26F69BAB-2721-4BD6-FF6C-E20E0A1A8A74", "Rhyl", "2014-11-07", "magna.Sed.eu@Phasellus.co.uk", 0, 1 ], [ "Adrienne Walker", "FD3A7745-C719-46BE-8DBA-C43FD4D63F2F", "Serampore", "2015-11-07", "Vivamus.sit.amet@sitametornare.edu", 0, 0 ], [ "Kylan Parrish", "7DA04399-F0E8-C379-E102-12A33335DCEC", "Oban", "2014-08-02", "ridiculus.mus@elementumsemvitae.org", 0, 0 ], [ "Margaret Atkins", "EFF52853-3381-CDAB-F25B-4D3D3E158449", "Bahraich", "2015-06-06", "nec@sit.net", 1, 0 ], [ "Denise Graham", "78B7EDF9-5808-7387-F521-286D3FF7EEFD", "Duluth", "2014-10-29", "est.congue@tempusrisusDonec.org", 0, 0 ], [ "Guy Camacho", "A45C4014-B7F9-932B-E7D4-1DA4CD8CD353", "Tonk", "2014-12-07", "pharetra@leoVivamus.net", 0, 0 ], [ "Doris Villarreal", "6854AA3A-B903-D325-6177-DB62D4949483", "Stuttgart", "2015-11-15", "lobortis.Class@duinectempus.co.uk", 0, 1 ], [ "Moses Dudley", "E7F4BD38-7A69-03F3-6ECD-7420E4C9DB4B", "Sassocorvaro", "2014-10-04", "Nullam.suscipit@velquam.org", 1, 1 ], [ "Bert Salazar", "A73EE643-13C3-4080-D3F3-67D951795C1C", "Chesapeake", "2014-11-04", "leo.Cras.vehicula@felisorci.org", 1, 1 ], [ "Kamal Skinner", "E6EB0049-F2F3-B77E-FB4E-5B7E98F70274", "San Pancrazio Salentino", "2015-09-30", "ut@tinciduntDonec.org", 0, 0 ], [ "Jael Brock", "81816049-C82C-74D2-EEF6-F6C8DEF2AE1A", "Alacant", "2014-01-14", "justo@arcu.com", 1, 1 ], [ "Ryan Durham", "B5112F14-1494-042B-2CAE-30127E6684A6", "Llanwrtwd Wells", "2015-09-16", "purus.in.molestie@Namporttitorscelerisque.co.uk", 1, 0 ], [ "Simon Estrada", "3153DB42-533C-E59C-2887-51990AED1489", "Worcester", "2015-03-23", "Nullam.suscipit@sit.edu", 0, 1 ], [ "Dennis Dickerson", "61C06E65-6155-6F72-2E33-9AC1F8EBA6E3", "Hollogne-sur-Geer", "2014-02-03", "lobortis.ultrices@tincidunt.ca", 0, 0 ], [ "Abraham Lancaster", "6697B449-5254-CF7C-CBA3-B093B35313AA", "Stevoort", "2015-03-11", "ante@dictumProineget.ca", 1, 0 ], [ "Nissim Watts", "308BD521-EA19-376E-3615-A09C52A95A28", "Novoli", "2016-03-10", "in.felis@dolorFusce.co.uk", 1, 1 ], [ "Ignatius Rosario", "5B720D90-1E24-EFD8-F133-4C1C0CD8AC5C", "Lachine", "2016-03-30", "tellus@auctor.net", 0, 0 ], [ "Octavius Jenkins", "F21AFCD7-A651-3C39-0B73-44F6C52C39AB", "Heredia", "2016-01-17", "nunc@dolorNullasemper.ca", 1, 0 ], [ "Stephen Haley", "3BEF67AA-1495-B87D-AF41-24CCC7FA3867", "Williams Lake", "2014-08-01", "Phasellus@lobortisultricesVivamus.co.uk", 0, 0 ], [ "Declan Gibson", "F436151C-2B1A-FF52-4E30-E7A1D689F1A1", "Neupr�", "2014-05-04", "Curabitur.egestas@eratSednunc.org", 1, 0 ], [ "Kane Roy", "BE1F9A2D-07B0-8DA4-6B6C-771C5FFCC597", "Stintino", "2015-02-28", "mus.Donec@pharetrafelis.org", 1, 0 ], [ "Patience Ewing", "63BA3B4B-955C-D57A-B537-D4E2F8DBFB88", "Hospet", "2015-10-31", "cursus@antelectus.ca", 0, 0 ], [ "Meredith Colon", "6476224F-3FB4-9312-1232-D15AD85E96A9", "Roermond", "2014-04-02", "condimentum@convallisligulaDonec.org", 1, 0 ], [ "Castor Head", "E48D6981-DA53-82D5-494D-0ED03982D22B", "Manisa", "2014-10-12", "arcu.Aliquam.ultrices@ligula.org", 1, 0 ], [ "Larissa Simon", "47F6DB81-A5F9-4DA6-260C-280CA9156ED2", "Panketal", "2016-03-06", "rhoncus.id.mollis@ut.com", 1, 1 ], [ "Lani Blake", "17D2DE82-81B0-4903-F081-B067B5BF4BA0", "Naro", "2014-03-30", "metus@imperdiet.net", 1, 1 ], [ "Kermit Holt", "DFAA746B-2CC2-AE15-7234-7A02CAB2C581", "Tay", "2015-10-17", "magna.Sed@sedsem.edu", 0, 0 ], [ "Lana Sherman", "97228175-652E-4B68-DBBC-4418CD41FAE0", "L�rrach", "2014-04-12", "turpis@disparturientmontes.net", 0, 1 ], [ "Perry Gordon", "5D9D3BC6-E4E5-20A1-C3CE-FDFEA556D540", "R�dermark", "2016-03-12", "Duis.ac@nullamagnamalesuada.co.uk", 1, 0 ], [ "Bernard Carver", "78ADFFAD-C857-7F26-FCAB-8DB73C4104D5", "Glain", "2014-02-12", "nonummy.ultricies@adui.ca", 0, 1 ], [ "Xyla Keith", "646262C0-62F2-6F11-2052-67775B40ED71", "Ohain", "2015-05-07", "laoreet.posuere.enim@interdum.co.uk", 0, 1 ], [ "Irene Randall", "3ED19269-F645-C3FC-A1D2-A6E612BFEBC3", "Nakusp", "2015-05-24", "Aliquam.nisl@Crasvehiculaaliquet.net", 1, 1 ], [ "Daryl Hines", "01442ABB-DC01-D17D-07B2-6633FEB2CD76", "Gonnosfanadiga", "2016-03-29", "mauris.sit.amet@porttitor.ca", 1, 0 ], [ "TaShya Fields", "1A6297CD-3383-E0DD-3BDF-A7DF008D45C0", "Beerse", "2014-08-16", "mollis.nec@Donecporttitortellus.ca", 1, 1 ], [ "Nadine Robertson", "5EE176C0-F463-DFCF-0DBB-C19FB61930D8", "Amravati", "2014-10-04", "ante.ipsum@cursus.net", 0, 1 ], [ "Ursa Cortez", "284A8B51-4D29-4F19-2AE1-B002473AACEE", "Broken Arrow", "2014-09-28", "Mauris.vel.turpis@ultricies.net", 1, 1 ], [ "Dalton Burt", "F6C9B8EE-270F-2942-10F0-2EFCC09D6E12", "Berceto", "2014-07-31", "ornare@eget.com", 1, 0 ], [ "Mira Stephens", "607024CF-0AC0-5CBE-9BF6-13BBA808AE5B", "Cambridge Bay", "2015-12-12", "augue.eu@et.net", 0, 0 ], [ "Lani Whitney", "4365593B-0248-EC19-82B2-5AF0A9E532EC", "Town of Yarmouth", "2014-09-09", "consequat.nec.mollis@consectetuereuismod.ca", 1, 1 ], [ "Lesley England", "5F2C0AA0-ACBB-66B3-10EB-FA9D66D13C66", "Sheikhupura", "2015-04-28", "varius.et.euismod@Sedpharetra.edu", 0, 1 ], [ "Hollee Palmer", "6C3DAB96-B37A-FEE4-DFE2-B889A30973EB", "Watermaal-Bosvoorde", "2014-04-23", "pellentesque.eget@auctor.org", 1, 1 ], [ "Dorothy Compton", "8623A4F4-869F-433C-9AE7-3A47AFB983E0", "Rotheux-Rimi�re", "2015-03-15", "elit.pede.malesuada@vehiculaetrutrum.net", 1, 1 ], [ "Kylee Gonzalez", "34D7E143-E66B-E75B-CA6A-1B7A8B412979", "Tarragona", "2014-06-10", "varius.orci@Aliquamornare.edu", 1, 0 ], [ "Upton Shelton", "A6F752CD-2130-E5FC-1A40-6B5470EF8FD3", "Turriff", "2014-09-16", "tempor@sedturpisnec.com", 1, 1 ], [ "Janna Gould", "9A34A7B6-AB9B-8886-98D8-9C38F0F0AE53", "Belo Horizonte", "2016-01-30", "ultrices.mauris.ipsum@variusultrices.org", 0, 1 ], [ "Ina Branch", "49819213-7DD4-A87F-6C34-9728105F0B8B", "Heusden", "2016-03-23", "mattis.velit@nullaatsem.edu", 0, 1 ], [ "Alexander Ross", "CEFDD1B1-03A5-E4EB-0A50-5725D74F4C48", "Collinas", "2014-01-09", "mi.lorem.vehicula@ligula.com", 0, 1 ], [ "Lester Henderson", "5FE04554-DE24-C867-3BC2-1A2E9054BB8B", "Rouyn-Noranda", "2014-05-18", "nunc.In@Curabiturconsequat.com", 1, 0 ], [ "Caldwell Hensley", "81898483-29BE-DF1A-2211-4BDB316955C8", "New Glasgow", "2014-04-05", "auctor.velit.Aliquam@temporaugueac.ca", 0, 1 ], [ "Hayes Gonzalez", "5BE33517-DCF6-1CA6-6914-723985C7C1B7", "Jennersdorf", "2014-09-12", "sagittis.placerat.Cras@faucibusutnulla.ca", 1, 0 ], [ "Helen Hood", "3401482C-8F09-81A0-A5DA-26896115F6CC", "Verrebroek", "2014-10-13", "non.feugiat.nec@ullamcorperDuis.co.uk", 1, 1 ], [ "Tate Melendez", "AF207045-3858-0F01-31FD-CAA420A00B9B", "Salzgitter", "2015-04-27", "a.magna@Crasconvallisconvallis.org", 0, 0 ], [ "Juliet Howell", "012749D3-02FC-EBD5-AB07-F2CC3EDF1431", "Bastia Umbra", "2015-06-20", "iaculis.quis.pede@atfringilla.net", 1, 1 ], [ "Carlos Rios", "40167333-3157-C7C3-DAFE-B627C487254F", "Temploux", "2014-06-07", "turpis@Fuscedolorquam.co.uk", 0, 1 ], [ "Virginia Love", "7C167FDE-BF2C-923E-00DF-60388FFB1E2C", "Kufstein", "2014-05-25", "a.felis@aliquameu.net", 0, 1 ], [ "Dylan Tanner", "57B95349-39D2-CAE3-7FB1-C1E1418F8A37", "Tullibody", "2014-04-02", "eget@risusMorbi.com", 1, 0 ], [ "Mason Parrish", "146A60E7-ED04-0FC4-C5B5-C30E23099DC7", "D�gelis", "2015-09-23", "mollis@magnaPhasellusdolor.edu", 0, 0 ], [ "Lillian Valencia", "176D911A-F17C-092B-40FE-0CB3A876F714", "Borgerhout", "2014-11-17", "rutrum.lorem@facilisiSed.org", 0, 0 ], [ "Dylan Kerr", "FCA87A5E-635C-2655-F190-B1525921E4A8", "L�vis", "2014-07-07", "Maecenas@gravida.co.uk", 1, 1 ], [ "Avram Mcdowell", "3F288ED8-0216-8FA6-7C3F-9E7CE9D1AF98", "Vaughan", "2016-02-07", "tristique@Aliquamtincidunt.net", 1, 0 ], [ "Charlotte Wells", "41BB04B7-F409-53FB-7F88-228784C8B71D", "Lethbridge", "2014-06-18", "dui.in@libero.org", 1, 1 ], [ "Amos Page", "76231DA1-DF11-3EE7-9377-1973C06E33CA", "Bonavista", "2015-07-27", "posuere.cubilia.Curae@fringillaest.edu", 0, 1 ], [ "Caryn Chapman", "A2ED6165-3755-7715-DB3C-60805EDEEAB6", "Saint-Servais", "2014-05-10", "Cum.sociis.natoque@non.co.uk", 1, 0 ], [ "Nero Osborne", "22C90B30-00A1-ACF2-84C2-4047FE93BC77", "Vichy", "2015-08-24", "neque.venenatis.lacus@posuereatvelit.com", 0, 1 ], [ "David Little", "F56A6CA7-B277-99B3-B914-8C5C5D51B707", "Richmond Hill", "2014-03-20", "ac@tellusSuspendissesed.org", 1, 0 ], [ "Noelle Vargas", "3F9C80E7-F976-2E63-D895-AD645204B975", "Chicago", "2014-01-04", "sit@euaugue.net", 0, 1 ], [ "Cedric Hahn", "E926F5D9-EA60-6B65-3A03-3DF3C2A4880D", "Keiem", "2014-07-15", "euismod@atvelit.net", 0, 1 ], [ "Dominique Raymond", "7E7C71DF-DB22-D537-E34D-631EFB0CED36", "Appels", "2015-10-25", "feugiat@neque.net", 0, 1 ], [ "Acton Fitzpatrick", "930ECC31-B250-F678-EC13-C4916BF5AB6B", "Gouda", "2015-07-24", "dictum.magna.Ut@enimnisl.edu", 1, 0 ], [ "Paula Pate", "980628FE-70F0-7B52-1783-5BD9E7A86383", "Osnabr�ck", "2015-10-09", "mollis.vitae.posuere@faucibusutnulla.co.uk", 0, 0 ], [ "Myles Mcintosh", "6BEDCAAC-5B87-6FE6-E5BE-C910A94C1144", "Zwickau", "2014-02-15", "ac.turpis@magnatellus.ca", 0, 1 ], [ "Colt Blevins", "9273304E-2D72-F3E5-9BB8-266D70F1C7BD", "Dawson Creek", "2014-07-30", "sit.amet@Nullamvitae.com", 0, 0 ], [ "Hilda Hogan", "AC11BF84-DDB7-6888-B42B-04C97762DFEF", "Galbiate", "2016-01-28", "sed@ligula.org", 1, 1 ], [ "Raven Booker", "769FAF48-F78A-3BDA-23A2-D8EB93FE7D45", "Dessau", "2014-08-23", "ut@velquamdignissim.edu", 0, 1 ], [ "Griffith Huff", "0796448F-3BE0-3EF7-5A98-96D575CEED87", "Medicine Hat", "2015-04-14", "mauris@libero.com", 0, 0 ], [ "Autumn Hebert", "5F3B4F22-3E22-28CA-25E0-276CBB1AAE1A", "Oppido Mamertina", "2015-06-08", "lobortis.Class@montesnasceturridiculus.org", 0, 1 ], [ "Sybil Francis", "85012463-261F-C927-60F3-580E2C7DDA0C", "Brixton", "2014-03-22", "risus@congueIn.com", 1, 1 ], [ "Bryar Leon", "96C8F406-82E9-1887-8A8F-D940E50AD180", "Casanova Elvo", "2014-09-23", "commodo.ipsum.Suspendisse@interdumfeugiatSed.org", 0, 0 ], [ "Armand Wiggins", "E15D0DEE-F348-18A4-C8DC-1F897AFCB5EE", "Mantova", "2014-11-13", "imperdiet.ornare@metus.edu", 0, 1 ], [ "Larissa Hurst", "29568C96-4DE7-12C8-05A7-D894BADAFBE9", "Bellefontaine", "2014-02-15", "vestibulum.neque@CurabiturdictumPhasellus.ca", 0, 1 ], [ "Jocelyn Mccullough", "9F66B7DD-99B8-021F-E229-4686F2CBAFAF", "Klabbeek", "2015-01-27", "Integer.mollis@ligula.org", 0, 0 ], [ "Bree Dunlap", "E3EE5856-4698-43F5-81DC-FB0A226EA52C", "Labrecque", "2016-03-01", "senectus.et@pharetraNamac.com", 0, 1 ], [ "Ashton Quinn", "06968912-A7AB-4380-3755-C4EECD736ADD", "Gravelbourg", "2015-04-03", "ultrices.Vivamus.rhoncus@Nulla.edu", 0, 1 ], [ "Oleg Phillips", "400D9DBB-9099-7E3A-1FA8-79D7A54E71CE", "Birmingham", "2016-03-25", "purus.sapien.gravida@Curae.net", 0, 1 ], [ "Fulton Merritt", "A03A1390-7438-B59D-B035-1051FD7027EF", "Lloydminster", "2015-03-12", "egestas@magnaLoremipsum.co.uk", 0, 1 ], [ "Victoria Huffman", "5157F244-E5B7-8300-6E91-C05A195BF3AB", "Casalbuono", "2015-08-26", "velit.Cras.lorem@estMauris.ca", 1, 1 ], [ "Tarik House", "29AB9CAB-D80E-818F-167D-00EE3970CF29", "Lauder", "2014-03-28", "scelerisque@inconsectetueripsum.net", 0, 1 ], [ "Uriah Valencia", "9D48C3DD-51E6-2951-74FF-4487C263F056", "Ransart", "2014-08-10", "montes.nascetur@Loremipsumdolor.ca", 1, 0 ], [ "Harding Matthews", "411F8C97-D459-BBAC-B0B9-1BA4F39F4A90", "Suwałki", "2014-06-21", "felis.orci@egestas.org", 1, 1 ], [ "Keefe Mccarthy", "3A3EF86E-B443-FB8E-D065-9ABEBF8C1424", "Wolvertem", "2015-08-11", "Suspendisse.dui@utmolestiein.ca", 0, 1 ] ]
#I know, this is sketch. The data generator only let me build 100 records at a time unless I paid them. Quit peekin' my code!

print "====================================================================================Enlarge window please.=================================="
startDecision = raw_input("\nBefore proceeding, please enlarge this window so the double line above is unbroken. Ready? (Y/N)  ")
if startDecision.lower() != "y" and startDecision.lower() != "yes":
    print "Quitting. Maybe later!"
    quit()

api_key = raw_input("\nAPI Key: ")
api_secret = raw_input("API Secret: ")
token = raw_input("Token: ")

printKav()

pfname = "temp-people-pythonpractice.txt"
peopleUp = open(pfname, "w")
fname = "pythonPractice-Events.txt"
eventUp = open(fname, "w")
eventGrp = set()
eventsToLoad = []

for user in dummyData:
    hasBeenSent = user[5]   
    peopleDict = {}
    peopleDict["$distinct_id"] = user[1]
    peopleDict["$properties"] = {}
    props = peopleDict["$properties"]
    props["$name"] = user[0]
    props["$city"] = user[2]
    lastSeen = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime((int(time.time()) - random.randint(0, 1814400))))
    props["$last_seen"] = lastSeen
    props["$email"] = user[4]
    if hasBeenSent == 1:
        eventGrp.add(user[1])
        props["$campaigns"] = 5309
    peopleUp.write(json.dumps(peopleDict)+"\n")

for user in eventGrp:
    sentDict = {}
    sentDict["event"] = "$campaign_delivery"
    sentDict["properties"] = {}
    now = int(time.time())
    twoMonthsAgo = now - 5259487
    sentTime = random.randint(twoMonthsAgo, now)
    buildEvent("$campaign_delivery", sentTime, user)
    opened = bool(random.getrandbits(1))
    if opened:
        openTime = random.randint(sentTime, now)
        buildEvent("$campaign_open", openTime, user)
    registered = bool(random.getrandbits(1))
    if registered:
        regTime = random.randint(sentTime, now)
        buildEvent("NEWSLETTER 53 Opt-in", regTime, user)

eventUp.close()
peopleUp.close()

import_event = EventImporter(token, api_key)
import_event.batch_update(fname)

if __name__ == '__main__':
    api = Mixpanel(
        api_key = api_key,
        api_secret = api_secret,
        token = token
    )

    api.batch_update(pfname)
os.remove(pfname)


print """
Your project is all set with dummy data!
An 'events.txt' file remains in this directory for you to use,
so that you don't have to wait for the raw API to batch.
However, you'll need to download your new People data yourself.
"""
