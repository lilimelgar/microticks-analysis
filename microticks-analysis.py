import json
#note: heatmap library requires pillow
import heatmap
import operator
from dateutil import parser
import calendar
import sys, getopt
import os

def isExcludedSession(ses,f,l,skippedSesArr):
	#include only a certain range of sessions
	if(ses < f or ses > l):
		return True 
	#do not include specified invalid sessions
	for skippedSes in skippedSesArr:
		if(ses == skippedSes):
			return True
	#false: session should not be excluded
	return False

def addFiltSubjClick(subj,filteredSubjectClicksDict):
	if(subj in filteredSubjectClicksDict):
		filteredSubjectClicksDict[subj]+=1
	else:
		filteredSubjectClicksDict[subj]=1

def generateStatistics(inputFile,stats,firstSes,lastSes,homeScrName,skippedSesArr):
	#create statistics dictionaries
	simpleSubjectClicksDict = {}
	filteredSubjectClicksDict = {}
	sessionClicksDict = {}
	sessionClicksOrderDict = {}
	dateDict = {}
	timeDict = {}
	simpleTimeCumuDict = {}
	filteredTimeCumuDict = {}
	dayDict = {}
	#page changes per ebook
	pageChangeDict = {} 
	#page changes per session
	pageChangesPerSessionDict = {} 
	#first, second, third click
	sessionsFirstClickDict = {}
	sessionsSecondClickDict = {}
	sessionsThirdClickDict = {}
	sessionsFirstClickCountDict = {}
	sessionsSecondClickCountDict = {}
	sessionsThirdClickCountDict = {}
	#screen duration dicts
	timePerScreenDict = {}
	totalOpenScreenCountDict = {}
	minOpenScreenCountDict = {}
	maxOpenScreenCountDict = {}

	#1. count clicks on items (unfiltered, including duplicates)
	for entry in stats['events']:
		if (not isExcludedSession(entry['session_id'],firstSes,lastSes,skippedSesArr)):
			#check if subject exists (otherwise: timeout entry)
			if('subject' in entry['data']):
				#existing entry
				if(entry['data']['subject'] in simpleSubjectClicksDict):
					simpleSubjectClicksDict[entry['data']['subject']]+=1
				else:
					#new entry
					simpleSubjectClicksDict[entry['data']['subject']]=1

	#2. count session-related data
	for entry in stats['events']:
		dateTime = parser.parse(entry['time'])
		date = dateTime.date()
		#logging hour is UTC, add 1 or 2 hours dep. on summer/winter time
		hours = dateTime.hour + 1
		#calculate time in seconds for capturing how long a screen is open
		time = dateTime.hour*3600 + dateTime.minute*60 + dateTime.second
		day = dateTime.weekday()

		#skip excluded sessions
		if(isExcludedSession(entry['session_id'],firstSes,lastSes,skippedSesArr)):
			continue
	
		#optional: skip clicks leading to nowhere
		##if(not 'prevSubject' in entry['data']):
		##	continue
	
		#store number of pages viewed per session (pdf viewer), count all
		if(entry['action'] == 'pageChange'):
			if (entry['session_id'] in pageChangesPerSessionDict):
				pageChangesPerSessionDict[entry['session_id']] += 1 
			else: 
				pageChangesPerSessionDict[entry['session_id']] = 1
	
		#store various click/swipe related data
		if(entry['action'] == 'click' or entry['action'] == 'swipe'):
			if('subject' in entry['data']):
				#count raw number of clicks during a session 
				#(includes duplicates, e.g. caused by 'faulty' clicks within a single subject)
				if (entry['session_id'] in sessionClicksDict):
					sessionClicksDict[entry['session_id']]+=1
				else:
					sessionClicksDict[entry['session_id']]=1
		
				#store order of clicks
				if (entry['session_id'] in sessionClicksOrderDict):
					sessionLength = len(sessionClicksOrderDict[entry['session_id']])
					#prevent double counting (i.e. repeated clicks on same subject)
					if(sessionClicksOrderDict[entry['session_id']][sessionLength-1] != entry['data']['subject']):
						#optional: do not count home screen
						##if(entry['data']['subject'] != homeScrName):
						sessionClicksOrderDict[entry['session_id']].append(entry['data']['subject'])
				else:
					#optional: ignore first 'home' button press(es)
					##if(entry['data']['subject'] != homeScrName):
					sessionClicksOrderDict[entry['session_id']] = []
					sessionClicksOrderDict[entry['session_id']].append(entry['data']['subject'])
		
				#store number of sessions per day, only count each session once
				if (entry['session_id'] not in dateDict):
					#quick fix: add a -1 entry for each session id into the same dict, to only count a session id once,
					#i.e. by checking if entry['session_id'] not in dateDict
					dateDict[entry['session_id']] = -1
					if (date in dateDict):
						dateDict[date]+=1
					else:
						dateDict[date]=1

				#store sessions time of day, only count each session once
				if (entry['session_id'] not in timeDict):
					#quick fix: add a -1 entry for each session id into the same dict, to only count a session id once,
					#i.e. by checking if entry['session_id'] not in timeDict
					timeDict[entry['session_id']] = -1	
					if (hours in timeDict):
						timeDict[hours]+=1
					else:			
						timeDict[hours]=1
	
				#store time of clicks for each hour the day, count all, cumulative
				if (hours in simpleTimeCumuDict):
					simpleTimeCumuDict[hours]+=1
				else:			
					simpleTimeCumuDict[hours]=1
			
				#store time of clicks for each hour of the day, not counting multiple clicks within the same subject
				if (hours in filteredTimeCumuDict):
					if (entry['session_id'] in filteredTimeCumuDict):
						sessionLength = len(filteredTimeCumuDict[entry['session_id']][0])
						if(filteredTimeCumuDict[entry['session_id']][0][sessionLength-1] != entry['data']['subject']):
							filteredTimeCumuDict[entry['session_id']][0].append(entry['data']['subject'])
							filteredTimeCumuDict[entry['session_id']][1].append(time)
							filteredTimeCumuDict[entry['session_id']][2].append(time-filteredTimeCumuDict[entry['session_id']][1][sessionLength-1])
							addFiltSubjClick(entry['data']['subject'],filteredSubjectClicksDict)
							filteredTimeCumuDict[hours]+=1
					else:
						filteredTimeCumuDict[entry['session_id']] = [[],[],[]]
						filteredTimeCumuDict[entry['session_id']][0].append(entry['data']['subject'])
						filteredTimeCumuDict[entry['session_id']][1].append(time)
						addFiltSubjClick(entry['data']['subject'],filteredSubjectClicksDict)
						filteredTimeCumuDict[hours]+=1
				else:
					if (entry['session_id'] in filteredTimeCumuDict):
						sessionLength = len(filteredTimeCumuDict[entry['session_id']][0])
						if(filteredTimeCumuDict[entry['session_id']][0][sessionLength-1] != entry['data']['subject']):
							filteredTimeCumuDict[entry['session_id']][0].append(entry['data']['subject'])
							filteredTimeCumuDict[entry['session_id']][1].append(time)
							filteredTimeCumuDict[entry['session_id']][2].append(time-filteredTimeCumuDict[entry['session_id']][1][sessionLength-1])
							addFiltSubjClick(entry['data']['subject'],filteredSubjectClicksDict)
							filteredTimeCumuDict[hours]=1
					else: 
						filteredTimeCumuDict[entry['session_id']] = [[],[],[]]
						filteredTimeCumuDict[entry['session_id']][0].append(entry['data']['subject'])
						filteredTimeCumuDict[entry['session_id']][1].append(time)
						addFiltSubjClick(entry['data']['subject'],filteredSubjectClicksDict)
						filteredTimeCumuDict[hours]=1
		
				#count sessions for each day of the week, only count each session once
				#i.e. by checking if entry['session_id'] not in dayDict
				if (entry['session_id'] not in dayDict):
					dayDict[entry['session_id']] = -1
					if (day in dayDict):
						dayDict[day]+=1
					else:
						dayDict[day]=1

	#count page changes per book
	for entry in stats['events']:
		if (not isExcludedSession(entry['session_id'],firstSes,lastSes,skippedSesArr)):		
			#check if subject exists
			if(entry['action']=="pageChange"):
				if('subject' in entry['data']):
					if(entry['data']['subject'] in pageChangeDict):
						pageChangeDict[entry['data']['subject']]+=1
					else:
						#new entry
						pageChangeDict[entry['data']['subject']]=1

	#create heatmaps for clicks within each subject
	heatmapDict = {}
	for entry in stats['events']:
		if (not isExcludedSession(entry['session_id'],firstSes,lastSes,skippedSesArr) and entry['action']=='click'):
			if ('clickX' in entry['data'] and 'prevSubject' in entry['data']):
				subj = ""	
				
				#optional: if it's a click leading to another subject	
				##if('prevSubject' in entry['data']):
				
				#optional: by date
				##subj = entry['time'][0:10] + "_" + entry['data']['prevSubject']
				
				#optional: by time of the day
				##subj = entry['time'][11:13] + "_" + entry['data']['prevSubject']
				
				subj = entry['data']['prevSubject']
							
				if(subj in heatmapDict):				heatmapDict[subj].append([entry['data']['clickX'],entry['data']['clickY']])
				else: 
					heatmapDict[subj] = []
					heatmapDict[subj].append([entry['data']['clickX'],entry['data']['clickY']])
	
	#calculate durations for each screen (excl. duplicates)
	for entry in filteredTimeCumuDict:
		if(entry >= firstSes):
			if(len(filteredTimeCumuDict[entry][2])>0):	
				for x in range(0,len(filteredTimeCumuDict[entry][0])-1):
					if (filteredTimeCumuDict[entry][0][x] in timePerScreenDict):
						timePerScreenDict[filteredTimeCumuDict[entry][0][x]]+=filteredTimeCumuDict[entry][2][x]
						totalOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]]+=1
					
						if(filteredTimeCumuDict[entry][2][x] < minOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]]):
							minOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]] = filteredTimeCumuDict[entry][2][x]
						if(filteredTimeCumuDict[entry][2][x] > maxOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]]):
							maxOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]] = filteredTimeCumuDict[entry][2][x]
					else:
						timePerScreenDict[filteredTimeCumuDict[entry][0][x]]=filteredTimeCumuDict[entry][2][x]
						totalOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]]=1
						minOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]]=filteredTimeCumuDict[entry][2][x]
						maxOpenScreenCountDict[filteredTimeCumuDict[entry][0][x]]=filteredTimeCumuDict[entry][2][x]

	
	#write heatmaps to file
	for entry in heatmapDict:
		#reset heatmapPoints object, otherwise heatmap is cumulative			
		heatmapPoints = []
		for xy in heatmapDict[entry]:
			heatmapPoints.append((xy[0],1080-xy[1]))
			#print "Processing %d points..." % len(heatmapPoints)
		hm = heatmap.Heatmap()
		
		#name folder based on input filename
		dir = str(inputFile.split('.')[0])
		#create subdirectories if needed
		if not os.path.exists(dir):
			os.makedirs(dir)
		#function supposes full hd resolution
		img = hm.heatmap(heatmapPoints,size=(1920, 1080),area=((0, 0), (1920, 1080))).save(dir + "/" + entry.replace(":","-").replace("/","-") + ".png")

	#capture clicks in order
	for entry in sessionClicksOrderDict:
		if (entry not in sessionsFirstClickDict):
			sessionsFirstClickDict[entry] = sessionClicksOrderDict[entry][0]
		
			if(sessionClicksOrderDict[entry][0] in sessionsFirstClickCountDict):
				sessionsFirstClickCountDict[sessionClicksOrderDict[entry][0]] += 1
			else:
				sessionsFirstClickCountDict[sessionClicksOrderDict[entry][0]] = 1
	
			if(len(sessionClicksOrderDict[entry]) > 1):
				if(sessionClicksOrderDict[entry][1] in sessionsSecondClickCountDict):
					sessionsSecondClickCountDict[sessionClicksOrderDict[entry][1]] += 1
				else:
					sessionsSecondClickCountDict[sessionClicksOrderDict[entry][1]] = 1
				
			if(len(sessionClicksOrderDict[entry]) > 2):
				if(sessionClicksOrderDict[entry][1] in sessionsThirdClickCountDict):
					sessionsThirdClickCountDict[sessionClicksOrderDict[entry][1]] += 1
				else:
					sessionsThirdClickCountDict[sessionClicksOrderDict[entry][1]] = 1
		
	
	###print / display the stats, based on an appended csv-like format###
	print 'total_num_sessions ' + str(len(sessionClicksDict))

	print '\nscreen_name num_clicks_incl_duplicates'
	totalClInclDup=0	
	for entry in sorted(simpleSubjectClicksDict, key=simpleSubjectClicksDict.get, reverse=True):
		print entry, simpleSubjectClicksDict[entry]
		totalClInclDup += simpleSubjectClicksDict[entry]
	print 'NUM-SCREENS', str(len(simpleSubjectClicksDict))
	print 'TOTAL-CLICKS', totalClInclDup

	print '\nscreen_name num_clicks_excl_duplicates'
	totalClExclDup=0
	for entry in sorted(filteredSubjectClicksDict, key=filteredSubjectClicksDict.get, reverse=True):
		print entry, filteredSubjectClicksDict[entry]
		totalClExclDup += filteredSubjectClicksDict[entry]
	print 'NUM-SCREENS', str(len(filteredSubjectClicksDict))
	print 'TOTAL-CLICKS ', totalClExclDup
	
	print '\nsession num_clicks_incl_duplicates'
	totalSesCl = 0
	for entry in sorted(sessionClicksDict, key=sessionClicksDict.get, reverse=True):
		print entry, sessionClicksDict[entry]
		totalSesCl += sessionClicksDict[entry]
	print 'NUM-SESSIONS', str(len(sessionClicksDict))
	print 'TOTAL-CLICKS', totalSesCl
	print 'AVG-CLICKS-P-SESSION', float(totalSesCl)/float(len(sessionClicksDict))

	print '\nsession_id num_subjects_viewed'
	totalSubjV = 0
	for entry in sessionClicksOrderDict:
		print entry, len(sessionClicksOrderDict[entry])
		totalSubjV += len(sessionClicksOrderDict[entry])
	print 'NUM-SESSIONS', str(len(sessionClicksOrderDict))
	print 'TOTAL-SUBJECT-VIEWS', totalSubjV
	print 'AVG-SUBJ-VIEWS-P-SESSION', float(totalSubjV)/float(len(sessionClicksOrderDict))
	
	print '\n1st_selected_subj_in_session num_sessions'
	firstClickCount = 0
	for subject in sorted(sessionsFirstClickCountDict, key=sessionsFirstClickCountDict.get, reverse=True):
		print subject, sessionsFirstClickCountDict[subject]
		firstClickCount += sessionsFirstClickCountDict[subject]
	print "NUM-SUBJECTS", str(len(sessionsFirstClickCountDict))
	print "NUM-SESSIONS", str(firstClickCount)

	print '\n2nd_selected_subj_in_session num_sessions'
	secondClickCount = 0
	for subject in sorted(sessionsSecondClickCountDict, key=sessionsSecondClickCountDict.get, reverse=True):
		print subject, sessionsSecondClickCountDict[subject]
		secondClickCount += sessionsSecondClickCountDict[subject]
	print "NUM-SUBJECTS", str(len(sessionsSecondClickCountDict))
	print "NUM-SESSIONS", str(secondClickCount)
	
	print '\n3rd_selected_subj_in_session num_sessions'
	thirdClickCount = 0
	for subject in sorted(sessionsThirdClickCountDict, key=sessionsThirdClickCountDict.get, reverse=True):
		print subject, sessionsThirdClickCountDict[subject]
		thirdClickCount += sessionsThirdClickCountDict[subject]	
	print "NUM-SUBJECTS", str(len(sessionsThirdClickCountDict))
	print "NUM-SESSIONS", str(thirdClickCount)

	print '\ndate number_of_sessions'
	sessionCount = 0
	numDates = 0
	for entry in sorted(dateDict, key=dateDict.get, reverse=True):
		#-1 values are sessions ids, so do not display
		if(dateDict[entry]>-1):
			print entry, dateDict[entry]
			sessionCount += dateDict[entry]
			numDates += 1
	print "NUM-DATES", str(numDates)
	print "TOTAL-SESSIONS", str(sessionCount)

	print '\nhour cumu_clicks_(incl_duplicates) num_sessions mean_clicks_incl_duplicates'
	ssCount = 0
	hourSes = 0
	for entry in simpleTimeCumuDict:
		#-1 values are sessions ids, so do not display
		if(simpleTimeCumuDict>-1):
			timeD = 0
			timeCumuD = 0
			meanCl = 0
			if(entry in timeDict):
				timeD = timeDict[entry]
			if(entry in simpleTimeCumuDict):
				timeCumuD = simpleTimeCumuDict[entry]
			if(timeD > 0 and timeCumuD > 0):
				meanCl = timeCumuD / timeD
			print entry, simpleTimeCumuDict[entry], timeD, meanCl
			hourSes += timeD
			ssCount += simpleTimeCumuDict[entry]
	print "NUM-HOURS", str(len(simpleTimeCumuDict))
	print "TOTAL-CLICKS", ssCount
	print "TOTAL-SESSIONS", hourSes


	print '\nscreen_type clicks_(no_duplicates)'
	screenCatDict = {}
	totalClicksSubject = 0
	for entry in filteredSubjectClicksDict:#sorted(filteredSubjectClicksDict, key=filteredSubjectClicksDict.get, reverse=True):
		category = entry.split(':')[0]
		if(category in screenCatDict):
			screenCatDict[category] += filteredSubjectClicksDict[entry]
		else:
			#new entry
			screenCatDict[category] = filteredSubjectClicksDict[entry]
	
	for category in screenCatDict:
		print category, screenCatDict[category]
		totalClicksSubject += screenCatDict[category]
	print 'NUM-SUBJECTS', len(screenCatDict)
	print 'TOTAL-CLICKS', str(totalClicksSubject)


	print '\nday number_of_sessions'
	sCount = 0
	dayCount = 0
	for entry in sorted(dayDict):
		#-1 values are sessions ids, so do not display
		if(dayDict[entry]>-1):
			print calendar.day_name[entry], dayDict[entry]
			sCount += dayDict[entry]
			dayCount += 1
	print "NUM-DAYS", str(dayCount)
	print "TOTAL-SESSIONS", str(sCount)
	
	
	print '\nresource total_num_page_changes total_num_clicks mean_viewed_pages_(2_per_page_change)'	
	sCount = 0
	totalNumViewedPages = 0
	totalNumClicks = 0
	for entry in sorted(pageChangeDict, key=pageChangeDict.get, reverse=True):
		print entry, pageChangeDict[entry], filteredSubjectClicksDict[entry], 2*(float(pageChangeDict[entry])/float(filteredSubjectClicksDict[entry]))
		sCount += 1
		totalNumViewedPages += pageChangeDict[entry]
		totalNumClicks += filteredSubjectClicksDict[entry]
	print "TOTAL-PAGE-CHANGES", totalNumViewedPages
	print "TOTAL-NUM-CLICKS", totalNumClicks
	print "TOTAL-AVG-VIEWED-PAGES", 2*(float(totalNumViewedPages)/float(totalNumClicks))


	print '\nsession num_page_changes num_viewed_pages'
	sessionCount = 0
	for entry in sorted(pageChangesPerSessionDict, key=pageChangesPerSessionDict.get, reverse=True):
		print entry, pageChangesPerSessionDict[entry], 2*pageChangesPerSessionDict[entry]
		sessionCount += pageChangesPerSessionDict[entry]
	print "TOTAL-PAGE-CHANGES", str(sessionCount)
	print "TOTAL-SESSIONS-WITH-BOOK-USE", str(len(pageChangesPerSessionDict))
	
	
	print '\nscreen time_spent min_time_spent max_time_spent total_screen_open_count mean_seconds_in_screen'
	sCount = 0
	for entry in sorted(timePerScreenDict, key=timePerScreenDict.get, reverse=True):
		print entry, timePerScreenDict[entry], minOpenScreenCountDict[entry], maxOpenScreenCountDict[entry], totalOpenScreenCountDict[entry], (float(timePerScreenDict[entry])/float(totalOpenScreenCountDict[entry]))
		sCount += 1
	print "TOTAL-SCREENS", str(sCount)
	
	
	print '\n\nTIME_PER_SCREEN'
	sCount = 0
	for entry in filteredTimeCumuDict:
		if(entry >= firstSes):
 			print '\nsubject',
 			for subj in filteredTimeCumuDict[entry][0]:
 				print str(subj),
 			print '\ndur_sec',
 			for time in filteredTimeCumuDict[entry][2]:
 				print str(time),
 			#last screen: not possible to determine duration, so always -1
 			print '-1',
	print '\n'		


	print '\nORDER_CLICKS_IN_SESSIONS'
	for entry in sessionClicksOrderDict:
		print '\n'+str(entry), 
		for subj in sessionClicksOrderDict[entry]:
			print subj,
	print "\nTOTAL-SESSIONS", str(len(sessionClicksOrderDict))
	

def loadInputFile(i,f,l,h,s):
	stats = json.load(open(i))
	generateStatistics(i,stats,f,l,h,s)
		
		
def main(argv):
	INPUT_FILE = ''
	FIRST_SESSION = ''
	LAST_SESSION = ''
	SKIPPED_SESSIONS = ''
	skippedSessionsArr = []
	HOME_SCR_NAME = ''
	SCREEN_CATEGORIES = ''
	screenCategoriesArr = []
	try:
		opts, args = getopt.getopt(argv,"i:f:l:h:s:")
	except getopt.GetoptError:
		print 'error in arguments'
		print 'processStats.py -i <inputfile> -f <first session id> -l <last session id> -h <name of home screen in ximpel app> [-s <comma separated list of session numbers to skip>]'
		sys.exit(2)
	for opt, arg in opts:
		#print opts
		if opt == '-i':
			INPUT_FILE = arg
		elif opt in ("-f"):
			FIRST_SESSION = int(arg)
		elif opt in ("-l"):
			LAST_SESSION = int(arg)
		elif opt in ("-h"):
			HOME_SCR_NAME = arg
		elif opt in ("-s"):
			SKIPPED_SESSIONS = arg
			skippedSessionsArr = map(int, SKIPPED_SESSIONS.split(',')) 
					
	print '#Input file is: ', INPUT_FILE
	print '#First session is: ', FIRST_SESSION
	print '#Last session is: ', LAST_SESSION
	print '#Home screen name is: ', HOME_SCR_NAME
	print '#Skipped sessions are: ', skippedSessionsArr
	print '\n'
	if(INPUT_FILE == '' or FIRST_SESSION == '' or LAST_SESSION == '' or HOME_SCR_NAME == ''):
		print 'missing argument(s)'
		print 'processStats.py -i <inputfile> -f <first session id> -l <last session id> -h <name of home screen in ximpel app> [-s <comma separated list of session numbers to skip>]'
		sys.exit(2)
	loadInputFile(INPUT_FILE,FIRST_SESSION,LAST_SESSION,HOME_SCR_NAME,skippedSessionsArr)

if __name__ == "__main__":
   main(sys.argv[1:])