"""Add a 'sig' param to your API request and, optionally,
curl it directly in the terminal. Slight usability modifications 
to Evan Weiss' original script.
 """
import md5
import urllib
import urllib2

raw_url = raw_input("Paste full url without sig:" + "\n")
api_secret = raw_input("Paste api secret" + "\n")

# Decode URL
url = urllib.unquote(raw_url).decode('utf8')
url = url.replace("+"," ")

# Set up args
args = url.split("?")[1].split("&")
args_new = []
for i in args:
	if i[0:4] != "sig=":
		args_new.append(i)

# Concatenate alphabetized params
args_concat = "".join(sorted(args_new))

# Append api_secret and md5 hash
sig = md5.new(args_concat+api_secret).hexdigest()

finalURL = raw_url + "&sig=" + sig

# Print Sig & full URL for user.
print "\nSig = " + sig
print "\n\nFull URL"
print "--------" 
print finalURL

# Print API response if requested
curlDecide = raw_input("\nCurl this URL? (Y/N) ")
if curlDecide.upper() == "Y":
	print urllib2.urlopen(finalURL).read()
