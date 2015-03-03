#import md5 library
import md5
import urllib

raw_url = raw_input("Paste full url without sig:" + "\n")
api_secret = raw_input("Paste api secret" + "\n")
url = urllib.unquote(raw_url).decode('utf8')
url = url.replace("+"," ")
print "Decoded URL = " + url

#get args from user somehow
args = url.split("?")[1].split("&")

args_new = []

for i in args:
	if i[0:4] != "sig=":
		args_new.append(i)


#create concatenation of alphabetized params
args_concat = "".join(sorted(args_new))

print "Args sorted and joined = " + args_concat


#append api_secret and hash
print "Args with the API secret on the end = " + (args_concat + api_secret)
sig = md5.new(args_concat+api_secret).hexdigest()


finalURL = raw_url + "&sig=" + sig

#print sig to check
print "Sig = " + sig

print "Full URL = " + finalURL

