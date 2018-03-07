import urllib.request as request
import re
import string
import sys
import csv
import zipfile
import os
plottable = False
try:
	import matplotlib.pyplot as plt
	plottable = True
except ImportError:
	print("Error importing matplotlib, unable to plot data. However, csv files can still be exported.\nTo create data plots, ensure that your Python distrubution has matplotlib installed.")

def downloadAFINN():
	print("Downloading Sentiment Data...")
	with open("AFINN.zip", "wb") as writeFile:
		opening = True
		while opening:
			try:
				writeFile.write(request.urlopen("http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6010/zip/imm6010.zip").read())
				opening = False
			except:
				print("Connection error, retrying.")
		zipData = zipfile.ZipFile("AFINN.zip", "r")
		zipData.extractall("./")
		zipData.close()
		writeFile.close()
	os.remove("AFINN.zip")

def getSentimentData(filename):
	print("Importing sentiment Data...")
	sentiment = {}
	with open (filename , "r") as sentimentData:
		for item in [x.split("	") for x in sentimentData]:
			sentiment[item[0]] = int(item[1].replace("\n" , ""))
	return sentiment

def loadPage(url):
	print("Loading Play...")
	page = str(request.urlopen(url).read())
	page = page.split("\\n")

	page = [y for y in [re.sub('<[^<]+?>', '', x) for x in page] if y != "" and len(y) > 1]
	page = page[page.index("ACT I"):]
	return page

def calculatePageSentiment(page, sentiment, window = 100):
	print("Analysing Play...")
	pageSentiment = []
	index = 0
	for line in page:
		lineSentiment = 0
		wordCount = 0
		for word in [x.lower() for x in line.split()]:
			for char in ",./:;'?\\&":
				word = word.replace(char, "")
				if word in sentiment.keys():
					wordCount +=1
					lineSentiment += sentiment[word]
		if wordCount == 0:
			wordCount = 1
		pageSentiment.append(lineSentiment/wordCount)

	pageSentiment2 = [sum(pageSentiment[:window])]

	while index < len(pageSentiment):
		if index - window/2-1 < 0:
			remove = 0
		else:
			remove = pageSentiment[index-int(window/2)-1]
		if index + window/2 + 1 > len(pageSentiment)-1:
			add = 0
		else:
			add = pageSentiment[index+int(window/2)+1]
		pageSentiment2.append(pageSentiment2[-1]+add-remove)
		index +=1
	pageSentiment2 = [x/window for x in pageSentiment2]

	return pageSentiment2

def ScaleData(pageSentiment, stepModifier = 200):
	global step
	pageSentiment2 = []
	index = 0
	step = int(len(pageSentiment)/stepModifier)
	while index < len(pageSentiment) - step:
		pageSentiment2.append(sum(pageSentiment[index:index+step])/len(pageSentiment[index:index+step]))
		index += step

	return pageSentiment2

def plotData(pageSentiment, playName):
	global step
	if plottable:
		print("Plotting Data...")
		plt.figure().canvas.set_window_title("Relative Happiness Level: " + playName)
		plt.title("Relative Happiness Level: " + playName)
		plt.plot(range(0,len(pageSentiment)*step,step),[100*((x+1)/(max(pageSentiment)+1)) for x in pageSentiment],"-")
		plt.xlabel("Line Number")
		plt.ylabel("Happiness %")
		plt.ylim([-5,105])
		plt.show()

def averageData(pageSentiment):
	average = sum(pageSentiment)/len(pageSentiment)
	pageSentiment = [x-average for x in pageSentiment]
	if max(pageSentiment) > -min(pageSentiment):
		return [x/max(pageSentiment) for x in pageSentiment]
	else:
		return [x/(-min(pageSentiment)) for x in pageSentiment]

def analysePlay(url, sentimentFilepath):
	sentimentDict = getSentimentData(sentimentFilepath)
	play = loadPage(url)
	playSentiment = calculatePageSentiment(play, sentimentDict, window = 500)
	playSentiment = ScaleData(playSentiment)
	playSentiment = averageData(playSentiment)
	return playSentiment

def getImportantLines(playSentiment):
	global step
	index = 1
	turningPoints = []
	while index < len(playSentiment) - 1:
		if (playSentiment[index] < playSentiment[index - 1] and playSentiment[index] < playSentiment[index+1]):
			turningPoints.append([index, playSentiment[index], False])
		if (playSentiment[index] > playSentiment[index - 1] and playSentiment[index] > playSentiment[index+1]):
			turningPoints.append([index, playSentiment[index], True])
		index += 1
	turningPoints2 = []

	while len(turningPoints) > 5:
		turningPoints2 = []
		index = 2
		while index < len(turningPoints) - 2 and len(turningPoints) > 5:
			if (turningPoints[index][1] < turningPoints[index + 2][1] and turningPoints[index][1] < turningPoints[index - 2][1] and not turningPoints[index][2]) or (turningPoints[index][1] > turningPoints[index + 2][1] and turningPoints[index][1] > turningPoints[index - 2][1] and turningPoints[index][2]):
				turningPoints2.append([turningPoints[index][0], turningPoints[index][1], turningPoints[index][2]])
			index += 1
		if len(turningPoints2) > 3:
			turningPoints = turningPoints2
		else:
			break
	return [x[0]*step for x in turningPoints]

def exportLines(lines, playName):
	with open(playName+".txt","w") as writeFile:
		writeFile.write("Potentially important lines: \nLine "+"\nLine ".join([str(x) for x in lines]))

def getPlayLinks():
	page = str(request.urlopen("http://shakespeare.mit.edu/").read())
	links = ["http://shakespeare.mit.edu/"+x.split('/')[0]+"/full.html" for x in page.split('a href="') if "index.html" in x]
	linkText = [x.split('>')[1].split("<")[0].replace("\\n","").replace("\\","") for x in page.split('a href="') if "index.html" in x]
	return(dict(zip(linkText, links)))

def writeCSV(playSentiment, name):
	with open (name+".csv","w") as writeFile:
		writer = csv.writer(writeFile)
		writer.writerow(["Line Number","Happiness Level"])
		line = 0
		for row in playSentiment:
			line+=1
			writer.writerow([line,int(row*10**5)/10**5])

def ui():
	if not os.path.isfile("AFINN/AFINN-111.txt"):
		print("Sentiment data not found.")
		downloadAFINN()
	connecting = True
	print("Connecting to http://shakespeare.mit.edu/...")
	while connecting:
		try:
			links = getPlayLinks()
			connecting = False
		except:
			print("Cannot connect, retrying...")
	choice = None
	print(("\n".join([str(list(links.keys()).index(x)+1)+". "+x for x in links.keys()]))+"\nChoose a play by entering its number.")
	selecting = True
	while selecting:
		choice = input("> ")
		try:
			print (choice)
			choice = int(choice.strip())
			selecting = False
		except:
			print("Enter a number corresponding to your play choice.")

	playSentiment = analysePlay(list(links.values())[choice-1],"AFINN/AFINN-111.txt")
	playName = list(links.keys())[choice-1]
	if (input("Output data as a CSV file? y/n\n>").lower().strip() == "y"):
		writeCSV(playSentiment, playName)
	if plottable:
		if (input("Generate a Graph? y/n\n>").lower().strip() == "y"):
			plotData(playSentiment, playName)
	if (input("Get important lines? y/n\n>").lower().strip() == "y"):
		lines = getImportantLines(playSentiment)
		print("Potentially important lines: \nLine: "+"\nLine ".join([str(x) for x in lines]))
		if (input("Export lines to .txt file? y/n\n>").lower().strip() == "y"):
			exportLines(lines, playName)

ui()