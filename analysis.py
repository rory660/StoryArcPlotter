import urllib.request as request
import re
import string
import matplotlib.pyplot as plt

sentiment = {}

with open ("AFINN-111.txt" , "r") as sentimentData:
	for item in [x.split("	") for x in sentimentData]:
		sentiment[item[0]] = item[1].replace("\n" , "")

print (sentiment["abandon"])

page = str(request.urlopen("http://shakespeare.mit.edu/macbeth/full.html").read())
page = page.split("\\n")

page = [y for y in [re.sub('<[^<]+?>', '', x) for x in page] if y != "" and len(y) > 1]
page = page[page.index("ACT I"):]

pageSentiment = []

# for line in page:
# 	lineSentiment = 0
# 	wordCount = 0
# 	for word in [x.lower() for x in line.split()]:
# 		for char in ",./:;'?\\&":
# 			word = word.replace(char, "")
# 		if word in sentiment.keys():
# 			wordCount += 1
# 			lineSentiment += int(sentiment[word])
# 	if wordCount == 0:
# 		wordCount = 1
# 	pageSentiment.append(lineSentiment/wordCount)


window = 100
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

pageSentiment3 = []

index = 0
step = int(len(pageSentiment)/200)
while index < len(pageSentiment) - step:
	pageSentiment3.append(sum(pageSentiment[index:index+step])/len(pageSentiment[index:index+step]))
	index += step
print (pageSentiment3)

pageSentiment = pageSentiment3

pageSentiment2 = [pageSentiment[0]]
for num in pageSentiment:
	pageSentiment2.append(pageSentiment2[-1]+num*step)

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
