from flask import Flask,render_template,url_for,request
from flask import Flask, request, jsonify

import nltk
import tweepy 
import csv
import pandas as pd
from random import shuffle 

import string
import re
 
from nltk.corpus import stopwords 
from nltk.tokenize import TweetTokenizer
from nltk.stem import PorterStemmer

from nltk import classify
from nltk import NaiveBayesClassifier

from nltk.corpus import twitter_samples

nltk.download('vader_lexicon')
nltk.download('stopwords')

from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from textblob import TextBlob 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import operator
from emoji import UNICODE_EMOJI
import emoji


app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/predict',methods=['POST'])
def predict():
	username = request.form['username']
	number = request.form['number']

	number = int(number)
	username = str(username)

	consumer_key = '8AO6OU5ubyi4XO47b1C7Sjdlz'
	consumer_secret = 'FS1usPrfPolvjLXbwGka5N8TWkOZhUsdxGmmTwuO016koesUSt'
	access_key = '1151573806680592384-OUFeUtpsRFZM6jQxl1AG99NEjlY0Kt'
	access_secret = 'KKHmkHkDGVaDof8XK4fKKI52DmNl4vZlaXnx85WRfd4Lr'

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth,wait_on_rate_limit=True)	

	stopwords_english = stopwords.words('english')
	stemmer = PorterStemmer()


	def clean_tweets(tweet):
 
		# remove hyperlinks
		tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
		
		# remove hashtags
		# only removing the hash # sign from the word
		tweet = re.sub(r'#', '', tweet)
	
		# tokenize tweets
		tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
		tweet_tokens = tokenizer.tokenize(tweet)
	
		tweets_clean = []
		for word in tweet_tokens:
			if (word not in stopwords_english and # remove stopwords 
					word not in string.punctuation): # remove punctuation
				stem_word = stemmer.stem(word) # stemming word
				tweets_clean.append(stem_word)
	
		return tweets_clean

	twit= []
	X_final = []	
	compound_scores =[]
	
	for tweet in tweepy.Cursor(api.user_timeline,screen_name="@"+username,
                           lang="en",
						   tweet_mode="extended",
                           since="2021-07-11").items(number):
		data = tweet.full_text
		clean_data = re.sub(r"http\S+", "", data)
		twit.append(clean_data)
		for words in clean_data:
			if (words in UNICODE_EMOJI['en']):
				dum=emoji.demojize(words) 
				dum=dum.replace("_"," ")	# :winking_face: :water_wave: removing '_' between the words here
				data=data.replace(words,dum)
			X_final.append(words)

		analyzer = SentimentIntensityAnalyzer()
		vs = analyzer.polarity_scores(X_final)
		finalscore=(vs.get("compound"))
		if finalscore>=0.05:
			compound_scores.append("Positive")
		elif finalscore<=-0.05:
			compound_scores.append("Negative")
		elif finalscore > -0.05 and finalscore < 0.05 :
			compound_scores.append("Neutral")
		# for i, j in newl:
		# 	print(i,' : ', j)
		# print(twit[-2], compound_scores[-2])
		# for i in range(len(compound_scores)):
		# 	print(compound_scores[i])
		# for i in range(len(twit)):
		# 	print(twit[i])

	newl = zip(twit,compound_scores)
	return render_template('result.html', newl=newl, username=username)



if __name__ == '__main__':
	app.run(debug=True)
