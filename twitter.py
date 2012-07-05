import sys
sys.path.append("..")
from google.appengine.ext import webapp
import tweepy
from images import model

CONSUMER_KEY = 'YwkArwmoFKd3ZnnX0p7pXg'
CONSUMER_SECRET = 'ow10R4qr1rXUDcB2es6viBrE22U5mKnapRyP0S9Mic'
ACCESS_KEY = '627725323-KpaMoATXgTJj4JHhbTBqi5uTudag9vJOui45DgLB'
ACCESS_SECRET = 'bOudTNPJIVx9pDqfDj7QCkZoxCV8pwTLdQWCRpOmo'

class TweetRandomImage(webapp.RequestHandler):
    def get(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        api = tweepy.API(auth)
        api.update_status("http://buukkit.appspot.com/img/" + model.get_random_image_name())
        #api.update_status("http://buukkit.appspot.com/img/dogsan.png")
