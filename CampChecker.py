from twilio.rest import Client
from bs4 import BeautifulSoup
import requests
import time
import logging
from logging.handlers import RotatingFileHandler
import traceback

def sendText(text):
	# put your own credentials here
	ACCOUNT_SID = "AC53722b859b69289962e963e8999840c7"
	AUTH_TOKEN  "SCRUBBED"
	client = Client(ACCOUNT_SID, AUTH_TOKEN)
	client.messages.create(
	  to="+SCRUBBED",
	  from_="+SCRUBBED",
	  body=text
	)


logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
logString = time.strftime("[%d/%m/%Y %H:%M:%S]")

#Max out at 10 MB log file. Then start spinnin'!
handler = RotatingFileHandler("campsites.log", maxBytes=10000000, backupCount=2)
logger.addHandler(handler)


#The campsite we want, really.
parkId = 70357
arrivalDate = 'Sat Jun 17 2017'
departureDate = 'Sun Jun 18 2017'

payload = {'contractCode': 'NRSO', 
'parkId': str(parkId),
'siteTypeFilter': 'ALL',
'submitSiteForm': 'true',
'arrivalDate': arrivalDate,
'departureDate': departureDate}

try:
	s = requests.Session()
	# We want to at least pretend we're not a robot; and this way we'll be more likely to get consistant HTTP responses
	s.headers.update({'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'})

	s.get("https://www.recreation.gov/campgroundDetails.do?contractCode=NRSO&parkId=" + str(parkId))
	r = s.post("https://www.recreation.gov/campsiteSearch.do", data= payload)

	statusCode = r.status_code
	logString += " statusCode: " + str(statusCode) + ". "
	soup = BeautifulSoup(r.text, "html.parser")

	#Pouched from http://alexmeub.com/finding-campsites-with-python/ because I'm lazy
	table = soup.findAll("table", attrs={"id": "shoppingitems"})
	rows = table[0].findAll("tr", {"class": "br"})
	hits = []

	for row in rows:
	    cells = row.findAll("td")
	    l = len(cells)
	    label = cells[0].findAll("div",{"class": "siteListLabel"})[0].text
	    isGroup = "group" in str(cells[2].text).lower()
	    status = cells[l-1].text
	    if( status.startswith( 'available' ) and not isGroup):
	        hits.append(label)

	text = "Found " + str(len(hits)) + " free campsite(s). Campsite name(s): " + str(hits)
	if (len(hits) > 0):
		sendText(text)

	logString += text

except Exception as e:
	stackTrace = traceback.format_exc()
	logString += " Caught exception: \n"
	logString += stackTrace

logger.info(logString)

