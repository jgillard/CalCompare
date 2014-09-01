import hashlib, getpass, requests, os, sys, math
from datetime import datetime, timezone, timedelta
from tabulate import tabulate
from icalendar import Calendar
from colorama import init, Fore

os.system("mode con lines=45")

DoW = ['Monday','Tuesday','Wednesday','Thursday','Friday']
HoD = ['9am','10am','11am','12pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm']
now = datetime.now(timezone.utc)

def makeArray():
	array = []	
	for i in range(0,12):
		x = []
		x.append(HoD[i])
		for j in range(0,5):
			x.append(0)
		array.append(x)
	return array

def readURLs():	 
	with open('calURLs.txt') as f:
		calURLs = f.readlines()
	return calURLs

def getParseCal(people):
	r = requests.get(calURLs[people])
	if r.status_code != 200:
		print("Error " + str(r.status_code) + ": We've had a fail here Jimmy...")
		sys.exit()
	rcal = Calendar.from_ical(r.text)

	# populate the events list (contains all relevant info)
	events = []
	for i in rcal.walk('VEVENT'):
		temp = {'DTSTART': i['DTSTART'].dt,
				'DTEND': i['DTEND'].dt,
				'DESCRIPTION':i['DESCRIPTION']}
		# firstly save the 1st event (regardless of RRULE)
		if temp['DTSTART'].hour != 8:
			events.append(temp)
		try:
			# if an RRULE is present, produce COUNT-1 number of extra individual events
			count = int(str(i['RRULE']['COUNT'])[1:-1])
			#day = i['RRULE']['BYDAY']  			# DOUBLE-CHECK THE DAY IS RIGHT FROM +WEEK
			week = timedelta(days = 7)
			for repeatNo in range(1, count): 		# don't add 1st event again
				temp = {'DTSTART': i['DTSTART'].dt + (repeatNo * week),
				'DTEND': i['DTEND'].dt + (repeatNo * week),
				'DESCRIPTION':i['DESCRIPTION']}	
				if temp['DTSTART'].hour != 8:
					events.append(temp)
		except:
			pass
	return events

def fillArray(events):
	# add events from list one-by-one to array
	for event in events:
		dur = int(math.ceil((event['DTEND'] - event['DTSTART']).seconds / 3600))
		day = event['DTSTART'].weekday()
		hour = event['DTSTART'].hour

		# add all new events in the next x days to array
		delta = (event['DTSTART'] - now)
		if delta.days <= 45 and delta.days >= 0:			# change to 7							
			if dur >= 1:
				for i in range(dur):
					print("HOUR = ", hour + i, "DAY = ", day+1)
					print(event['DESCRIPTION'],event['DTSTART'])
					array[hour - 9 + i][day + 1] += 1  	# offset hour by 9 (index0 = 9am, offset day by 1 as filled by time strings


array = makeArray()
calURLs = readURLs()

print("# of URLs = ", len(calURLs))

for people in range(len(calURLs)):	
	fillArray(getParseCal(people))
	
print(tabulate(array, headers = DoW))

######################################

# find the lowest value entry in array
minVal = 11
minVal = min(min(i[1:]) for i in array)
print(minVal)

# create new array with possible times
array2 = makeArray()
for i in range(0,12):		
	for j in range(1,6):
		if array[i][j] == minVal:
			array2[i][j] = 'Y'
		else:
			array2[i][j] = ''
print(tabulate(array2, headers = DoW))
