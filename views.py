# -- coding: utf-8 --

from datetime import datetime
from flask import render_template
from FlaskWebProject import app
import os
import json
from flask import Flask, request, redirect, url_for
from alchemyapi import AlchemyAPI
from werkzeug import secure_filename
import helperFunctions
import time, timeit
import string
import validators

#Adding octave call header file

global firstReturn
firstReturn=True
global suggestedUrls
suggestedUrls=[" "]*4

UPLOAD_FOLDER= "/"

alchemyapi=AlchemyAPI()


app.config['UPLOAD_FOLDER'] = "/"

@app.route('/')
@app.route('/home')
def home():

    """Renders the home page."""
    return render_template(
        'myo.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route("/download/<url>", methods=['GET', 'POST'])
def download(url= "regularSearch"):
    start= timeit.default_timer()
    UUIDsBlegh= ["1db874ca-f3d8-11e5-9ce9-5e5517507c66",
	"1db87902-f3d8-11e5-9ce9-5e5517507c66",
	"1db87aec-f3d8-11e5-9ce9-5e5517507c66",
	"1db87dbc-f3d8-11e5-9ce9-5e5517507c66",
	]
    suggestedEntityUrls=[]

    if (request.method == "POST") or (not (url=="regularSearch")):
 
        with open("FlaskWebProject/templates/results.html", "r") as infile:	
             s=infile.read()
        global suggestedUrls, firstReturn
	if (url=="regularSearch"):
	    url = request.form['thefile']
	    if (not validators.url(url) and " " in url):
		print "not a url"
                url=(helperFunctions.bingSearch(("news " + url)))[0]
	else: url= suggestedUrls[int(url)]		
        print "URL is " + url
	extracted=(alchemyapi.text("url", url, {}))
	extractedText= extracted["text"]
        originalURL=helperFunctions.cleanString(url.encode("utf8"))
	jsonDict=alchemyapi.entities("url", url, {})
	entityList=jsonDict["entities"]
	author=alchemyapi.author("url", url, {})["author"]
	title=alchemyapi.title("url", url, {})["title"]
	title= (helperFunctions.cleanString(title)).encode('utf8')

	searchTerms= []
	types=[]
	maxTerm=max(4,len(entityList))
	for i in xrange(maxTerm):
          try: 
              searchTerms.append(entityList[i]["disambiguated"]["name"])
              types.append(entityList[i]["type"])
          except: pass
	searchTerms=helperFunctions.cleanStringArray(searchTerms)
	types=helperFunctions.cleanStringArray(types)
	suggestedUrls=[]
	suggestedUrlsAndTitles= helperFunctions.bingNews(" ".join(searchTerms))
        print suggestedUrlsAndTitles

	if (len(suggestedUrlsAndTitles) <= 1) and len(searchTerms) >=2: suggestedUrlsAndTitles= helperFunctions.bingNews((searchTerms[0]))
	elif (len(suggestedUrls) <= 1):  suggestedUrlsAndTitles= helperFunctions.bingNews("recent news")
        print suggestedUrls

	for i in xrange(len(suggestedUrlsAndTitles)): suggestedUrls.append(suggestedUrlsAndTitles[i][0])
	print suggestedUrls
	summarizedText=helperFunctions.summary(extractedText, 300)

	s=s.replace("SUMMARY_RESULTS_GO_HERE", summarizedText)
	#Get related news from bing and replace in doc: 
	breaking=False

	for i in xrange(1,5):
	     try:
		     s=s.replace(("NEWS_LINK"+str(i)), suggestedUrlsAndTitles[i-1][1],1)
	   	     s=s.replace((UUIDsBlegh[i-1]),str(url_for('download', url= str(i-1))))
	     except:
		     s=s.replace(("NEWS_LINK"+str(i)), "",1)

	breaking=False
	#Get entity info from bing and replace in doc:
	for i in xrange(4): 
	     try:
		try:suggestedEntityUrls.append((helperFunctions.bingSearch(("en.wikipedia.org "+searchTerms[i]+" "+types[i]), limit=1))[0])
		except: suggestedEntityUrls.append((helperFunctions.bingSearch(("en.wikipedia.org "+searchTerms[i]), limit=1))[0])

	     except:
		pass
	suggestedEntityUrls=suggestedEntityUrls[:4]
	suggestedEntityUrls=helperFunctions.cleanStringArray(suggestedEntityUrls)

	breaking=False
	for i in xrange(1,5): 
		try:
			if breaking: 
				s=s.replace(("INFO_LINK"+str(i)), " ")
			        s=s.replace((suggestedEntityUrls[i-1]), "")
				s=s.replace(("INF_LINK_NAME"+str(i)), "")
			        breaking=True
			else:
				s=s.replace(("INFO_LINK"+str(i)), suggestedEntityUrls[i-1])
				s=s.replace(("INF_LINK_NAME"+str(i)), searchTerms[i-1])
			      
		except:
			s=s.replace(("INFO_LINK"+str(i)), " ")
			s=s.replace(("INF_LINK_NAME"+str(i)), "")
	                breaking=True
	author= (helperFunctions.cleanString(author)).encode("utf-8")
	s=s.replace("About the author", "About the author: " + author)
	s=s.replace("TITLE_GOES_HERE", title)
        s=s.replace("TITLE_LINK_GOES_HERE", originalURL)
	#Get info on author 
	try:
		authorURL=helperFunctions.bingSearch("journalist writer en.wikipedia.org "+author)[0]
		extractedAuthorArticle=(alchemyapi.text("url", authorURL, {}))
		extractedAuthorText= extractedAuthorArticle["text"]
		if not ((((string.lower(extractedAuthorText.encode('utf8')).find(string.lower(author.encode('utf8'))))==-1) or ((string.lower(authorURL.encode('utf8')).find(string.lower("en.wikipedia.org")))==-1))):
			summarizedAuthorText=helperFunctions.summary(extractedAuthorText, 150)
			s=s.replace("AUTHOR_INFO", summarizedAuthorText)
		else:
			((string.lower(extractedAuthorText.encode('utf8')).find(string.lower(author.encode('utf8'))))==-1) 
			s=s.replace("AUTHOR_INFO", "A wikipedia page for this author could not be found.  This probably occured because the author is not famous enough to  have a noteworthy wikipedia page. ")
	except:	
		s=s.replace("AUTHOR_INFO", "A wikipedia page for this author could not be found.  ")
	with open("FlaskWebProject/templates/resultsOutput.html", "w") as outfile: outfile.write(s)
        stop= timeit.default_timer()
	print "total time was : " + str(stop-start)
	return redirect(url_for('download', url="regularSearch"))
    else:
        return render_template("resultsOutput.html", title = "Home Page", year = datetime.now().year,)
 


