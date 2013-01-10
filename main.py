import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.runtime import apiproxy_errors

from images import handler
from images import model
from twitter import TweetRandomImage


class HelpHandler(webapp.RequestHandler):
    def get(self):
        try:
            nb_images = len(model.get_all_images())
            image_name = model.get_random_image_name()

            self.response.out.write("""
    <!DOCTYPE html>
    <html>
    <pre>
                 .--.
                (    )
       ,   ,         |
       |\_/|_________|
       |+ <span id="eye">+</span>          o  ... """ + str(nb_images) + """ images and counting ...
       |_^_|-||_____||
         U   ||     ||
            (_|    (_|

    <a href="https://twitter.com/buukkit">@buukkit</a>

    <a href="/img/random">/img/random</a>.............Returns a random image
    <a href="/img/random.gif">/img/random.gif</a>.........Returns a random image
    <a href="/img/wakewhenicare.gif">/img/(.*)</a>...............Returns an image, given its file name

    <a href="/html/list">/hmtl/list</a>..............Returns an HTML page containing the list of all image names
    <a href="/html/viewall">/html/viewall</a>...........Returns an HTML page containing all images (this may freeze your browser)
    <a href="/html/search">/html/search</a>............Returns an HTML page containing a search engine for images

    <a href="/json/random?cb=callback">/json/random</a>............Returns a json response for a random image (pass ?cb= for a jsonp response)
    <a href="/json/search/cat?cb=callback">/json/search/(.*)</a>.......Returns a json response for a list of images matching the search query string (pass ?cb= for a jsonp response)
    <a href="/json/list?cb=callback">/json/list</a>..............Returns a json response for the complete list of images (pass ?cb= for a jsonp response)


    <img src="/img/""" + image_name + """" />
    <a href="/img/""" + image_name + """">""" + handler.get_img_root_url(self.request) + image_name + """</a>
    </pre>
    <script>
    var eye = document.getElementById('eye');
    function close() {eye.innerHTML = "-";setTimeout(open, 150)}
    function open() {eye.innerHTML = "+";setTimeout(close, Math.random()*7000);}
    setTimeout(close, 1000);
    </script>
    </html>
            """)
        except apiproxy_errors.OverQuotaError, message:
            logging.error(message)
            self.redirect("/static/oops.html")


class ThiefHelpHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
        <pre>

          _._     _,-'""`-._
         (,-.`._,'(       |\`-/|
             `-.-' \ )-`( , o o)
                   `-    \`_`"'-


        <a href="/__/upload">Upload a single image</a>


        <a href="/__/steal/giftv">steal some more giftv images</a>
        <a href="/__/steal/bukit">steal some more bukkit images</a>
        </pre>
        """)


def main():
    application = webapp.WSGIApplication([

        ('/html/list', handler.GetListOfImagesAsHtmlHandler),
        ('/html/viewall', handler.DisplayAllImagesAsHtmlHandler),
        ('/html/search', handler.SearchThroughImagesAsHtmlHandler),

        ('/img/random\.(?:gif|jpg|png)', handler.GetRandomImageHandler),
        ('/img/random', handler.GetRandomImageHandler),
        ('/img/(.*)', handler.GetImageHandler),

        ('/json/random', handler.GetRandomImageAsJsonHandler),
        ('/json/search/(.*)', handler.GetImageSearchListAsJsonHandler),
        ('/json/list', handler.GetListOfImagesAsJsonHandler),

        ('/__/steal/bukit', handler.StealBukitImages),
        ('/__/steal/giftv', handler.StealGifTvImages),
        #('/__/steal/mb', handler.StealMemeBaseImages),
        #('/__/steal/mbad', handler.StealMemeBaseAfterDarkImages),
        ('/__', ThiefHelpHandler),
        ('/__/upload', handler.UploadSingleImage),
        ('/__/delete', handler.DeleteImage),

        ('/tweet', TweetRandomImage),

        ('.*', HelpHandler)

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
