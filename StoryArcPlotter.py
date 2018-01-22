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
			sentiment[item[0]] = item[1].replace("\n" , "")
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
					windowSentiment += int(sentiment[word])
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

def plotData(pageSentiment, pageSentiment2):
	print("Plotting Data...")
	if (max(pageSentiment) > -min(pageSentiment)):
		yScale = max(pageSentiment)*1.1
	else:
		yScale = -min(pageSentiment)*1.1

	if (max(pageSentiment2) > -min(pageSentiment2)):
		yScale2 = max(pageSentiment2)*1.1
	else:
		yScale2 = -min(pageSentiment2)*1.1

	average2 = sum(pageSentiment2)/len(pageSentiment2)
	if max(pageSentiment2) - average2 > average2 - min(pageSentiment2):
		yScale2 = (max(pageSentiment2) - average2) * 1.1
	else:
		yScale2 = (average2 - min(pageSentiment2)) * 1.1
	plt.subplot(2,1,1)
	plt.plot(range(0,len(pageSentiment2)*step,step),pageSentiment2,"-")
	plt.title("Average Sentiment per Line")
	plt.ylabel("Cumulative")
	plt.ylim([average2 - yScale2 ,average2 + yScale2])
	plt.subplot(2,1,2)
	plt.plot(range(0,len(pageSentiment)*step,step),pageSentiment,"-")
	plt.xlabel("Line Number")
	plt.ylabel("Individual")
	plt.ylim([-yScale,yScale])
	plt.show()

def analysePlay(url, sentimentFilepath):
	sentimentDict = getSentimentData(sentimentFilepath)
	play = loadPage(url)
	playSentiment = calculatePageSentiment(play, sentimentDict)
	playSentiment = ScaleData(playSentiment)
	playSentimentCumulative = calculateCumulativePageSentiment(playSentiment)
	plotData(playSentiment, playSentimentCumulative)

if len(sys.argv) > 1 and "shakespeare.mit.edu" in sys.argv[1]:
	analysePlay(sys.argv[1], "AFINN-111.txt")
else:
	print("Please enter the url of a shakespeare play in the format: http://shakespeare.mit.edu/[Play Title]/full.html")
	playUrl = input("> ")
	analysePlay(playUrl, "AFINN-111.txt")