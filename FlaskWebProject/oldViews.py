"""
Routes and views for the flask application.
"""

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
#Adding octave call header file


UPLOAD_FOLDER= "/"

alchemyapi=AlchemyAPI()


app.config['UPLOAD_FOLDER'] = "/"

@app.route('/')
@app.route('/home')
def home():
    print "happened"
    """Renders the home page."""
    return render_template(
        'myo.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route("/download", methods=['GET', 'POST'])
def upload_file():
    print "Accessing Alchemy"
    if (request.method == "POST"):
	"""I did not have time to make nice code, as I had two midterms the week the project was assigned, on top of an already busy plate of research, homework, other coding challenges and the production of a lecture video series.  I've copied a lot of my code around and wrote it with horrible style.  If  you are actually reading the code, I am so sorry, you must think I am an awful human being."""

	#Grab extracted  text
        url = request.form['thefile'] 
        extracted=(alchemyapi.text("url", url, {}))
        extractedText= extracted["text"]

        jsonDict=alchemyapi.entities("url", url, {})
        entityList=jsonDict["entities"]
        author=alchemyapi.author("url", url, {})["author"]
        title=alchemyapi.title("url", url, {})["title"]
        searchTerms= []
        types=[]
        for i in xrange(len(entityList)):
             if (i==5): break
             else: 
                  try: 
                      (searchTerms.append(entityList[i]["disambiguated"]["name"]))
                      types.append(entityList[i]["type"])
                      
                  except: pass
        searchTerms=helperFunctions.cleanStringArray(searchTerms)
	types=helperFunctions.cleanStringArray(types)
        


        suggestedUrls= helperFunctions.bingSearch("news "+(" ".join(searchTerms)))

        suggestedUrls=helperFunctions.cleanStringArray(suggestedUrls)

	summarizedText=helperFunctions.summary(extractedText, 300)

	with open("FlaskWebProject/templates/results.html", "r") as infile:	
	     s=infile.read()
        s=s.replace("SUMMARY_RESULTS_GO_HERE", summarizedText)
        #Get related news from bing and replace in doc: 
        breaking=False
        for i in xrange(1,6):
             try:
		if breaking: s=s.replace(("NEWS_LINK"+str(i)), " ")
		else: s=s.replace(("NEWS_LINK"+str(i)), suggestedUrls[i-1])
	     except:
		s=s.replace(("NEWS_LINK"+str(i)), " ")
                breaking=True
        breaking=False
        #Get entity info from bing and replace in doc:
        suggestedEntityUrls=[]
        for i in xrange(5): 
             try:
		suggestedEntityUrls.append((helperFunctions.bingSearch("wikipedia "+searchTerms[i]+" "+types[i]))[0])
	     except:
		break

	suggestedEntityUrls=helperFunctions.cleanStringArray(suggestedEntityUrls)

        breaking=False
        for i in xrange(1,6): 
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

        s=s.replace("About the author", "About the author, " + author)
        s=s.replace("TITLE_GOES_HERE", title)
        #Get info on author 
	try:
		authorURL=helperFunctions.bingSearch("journalist writer en.wikipedia.org "+author)[0]
		print authorURL
		extractedAuthor=(alchemyapi.text("url", authorURL, {}))
		extractedAuthorText= extractedAuthor["text"]
		if not ((((string.lower(extractedAuthorText.encode('utf8')).find(string.lower(author.encode('utf8'))))==-1) or ((string.lower(authorURL.encode('utf8')).find(string.lower("en.wikipedia.org")))==-1))):
			summarizedAuthorText=helperFunctions.summary(extractedAuthorText, 150)
			s=s.replace("AUTHOR_INFO", summarizedAuthorText)
		else:
			((string.lower(extractedAuthorText.encode('utf8')).find(string.lower(author.encode('utf8'))))==-1) 
			s=s.replace("AUTHOR_INFO", "A wikipedia page for this author could not be found. ")
	except:	
		s=s.replace("AUTHOR_INFO", "A wikipedia page for this author could not be found. ")
        with open("FlaskWebProject/templates/resultsOutput.html", "w") as outfile: outfile.write(s)

        return redirect("/download")
    else:
        return render_template("resultsOutput.html", title = "Home Page", year = datetime.now().year,)
 


