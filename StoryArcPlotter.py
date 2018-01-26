import urllib.request as request
import re
import string
import matplotlib.pyplot as plt
import sys

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
	index = window//2
	while index < len(page)-window//2:
		windowSentiment = 0
		wordCount = 0
		for i in range(index - window//2,index + window//2):
			for word in [x.lower() for x in page[i].split()]:
				for char in ",./:;'?\\&":
					word = word.replace(char, "")
				if word in sentiment.keys():
					wordCount+=1
					windowSentiment += sentiment[word]
		if wordCount == 0:
			wordCount = 1
		pageSentiment.append(windowSentiment/wordCount / window)
		index+=1
	return pageSentiment

def ScaleData(pageSentiment, stepModifier = 200):
	global step
	pageSentiment2 = []
	index = 0
	step = int(len(pageSentiment)/stepModifier)
	while index < len(pageSentiment) - step:
		pageSentiment2.append(sum(pageSentiment[index:index+step])/len(pageSentiment[index:index+step]))
		index += step

	return pageSentiment2

def calculateCumulativePageSentiment(pageSentiment):
	global step
	pageSentimentCumulative = [pageSentiment[0]]
	for num in pageSentiment:
		pageSentimentCumulative.append(pageSentimentCumulative[-1]+num*step)

	return pageSentimentCumulative

def plotData(pageSentiment, pageSentiment2, playName):
	print("Plotting Data...")

	average = sum(pageSentiment)/len(pageSentiment)
	average2 = sum(pageSentiment2)/len(pageSentiment2)
	plt.subplot(2,1,1)
	plt.plot(range(0,len(pageSentiment2)*step,step),[100*((x+1)/(max(pageSentiment2)+1)) for x in pageSentiment2],"-")
	plt.title("Relative Happiness Level: "+playName)
	plt.ylabel("Happiness % (Cumulative)")
	plt.ylim([-5,105])
	plt.subplot(2,1,2)
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
	
def averageDataCumulative(pageSentiment):
	pageSentiment2 = pageSentiment[0]
	pageSentiment2 = [sum(pageSentiment2)+x for x in pageSentiment[1:]]
	if max(pageSentiment2) > min(pageSentiment2):
		return [x/max(pageSentiment2) for x in pageSentiment2]
	else:
		return [x/(-min(pageSentiment2)) for x in pageSentiment2]

def analysePlay(url, sentimentFilepath, playName):
	sentimentDict = getSentimentData(sentimentFilepath)
	play = loadPage(url)
	playSentiment = calculatePageSentiment(play, sentimentDict, window = 500)
	playSentiment = ScaleData(playSentiment)
	playSentimentCumulative = calculateCumulativePageSentiment(playSentiment)
	playSentiment = averageData(playSentiment)
	playSentimentCumulative = averageData(playSentimentCumulative)
	plotData(playSentiment, playSentimentCumulative, playName)

def getPlayLinks():
	page = str(request.urlopen("http://shakespeare.mit.edu/").read())
	links = ["http://shakespeare.mit.edu/"+x.split('/')[0]+"/full.html" for x in page.split('a href="') if "index.html" in x]
	linkText = [x.split('>')[1].split("<")[0].replace("\\n","").replace("\\","") for x in page.split('a href="') if "index.html" in x]

	return(dict(zip(linkText, links)))

def ui():
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
	analysePlay(list(links.values())[choice-1],"AFINN-111.txt",list(links.keys())[choice-1])
ui()
# if len(sys.argv) > 1 and "shakespeare.mit.edu" in sys.argv[1]:
# 	analysePlay(sys.argv[1], "AFINN-111.txt")
# else:
# 	print("Please enter the url of a shakespeare play in the format: http://shakespeare.mit.edu/[Play Title]/full.html")
# 	playUrl = input("> ")
# 	analysePlay(playUrl, "AFINN-111.txt")