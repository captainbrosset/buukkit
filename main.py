import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from images import handler
from images import model
from twitter import TweetRandomImage

def main():
    application = webapp.WSGIApplication([

        ('/html/list', handler.GetListOfImagesAsHtmlHandler),
        ('/html/viewall', handler.DisplayAllImagesAsHtmlHandler),
        ('/html/search', handler.SearchThroughImagesAsHtmlHandler),

        ('/img/random\.(?:gif|jpg|png)', handler.GetRandomImageHandler),
        ('/img/random', handler.GetRandomImageHandler),
        ('/img/search/([^.]+)\.(?:gif|jpg|png)', handler.SearchImageHandler),
        ('/img/(.*)', handler.GetImageHandler),

        ('/json/random', handler.GetRandomImageAsJsonHandler),
        ('/json/search/(.*)', handler.GetImageSearchListAsJsonHandler),
        ('/json/list', handler.GetListOfImagesAsJsonHandler),

        ('/__/steal/bukit', handler.StealBukitImages),
        #('/__/steal/giftv', handler.StealGifTvImages),
        #('/__/steal/mb', handler.StealMemeBaseImages),
        #('/__/steal/mbad', handler.StealMemeBaseAfterDarkImages),
        ('/__', handler.ThiefHelpHandler),
        ('/__/upload', handler.UploadSingleImage),
        ('/__/delete', handler.DeleteImage),

        ('/tweet', TweetRandomImage),

        ('/', handler.HelpHandler)

    ], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
