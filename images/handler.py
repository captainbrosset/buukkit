import urllib2
import re
import logging
import random
from urlparse import urlparse
import os

from google.appengine.runtime import apiproxy_errors
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson

import model
import crawler


def get_img_root_url(request):
    o = urlparse(request.url)
    return o.scheme + "://" + o.netloc + "/img/"


def respond_image(db_image, response, short_time_to_live=False):
    file_name = db_image.key().name()
    extension = file_name[file_name.rfind(".")+1:]

    content_types = {
        "gif": "image/gif",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png"
    }

    if short_time_to_live:
        response.headers["Expires"] = "Thu, 01 Dec 1994 16:00:00 GMT"
    else:
        response.headers["Expires"] = "Thu, 01 Dec 2504 16:00:00 GMT"
        
    response.headers["Content-Type"] = content_types[extension]
    response.headers["X-image-name"] = file_name
    response.out.write(db_image.content)


def respond_json(response, request, data):
    json_data = simplejson.dumps(data)
    if request.get('cb'):
        json_data = request.get('cb') + "(" + json_data + ");"

    response.out.write(json_data)


def respond_template(response, template_name, data):
    path = os.path.join(os.path.dirname(__file__), '..', 'templates',  template_name)
    response.out.write(template.render(path, data))


class HelpHandler(webapp.RequestHandler):
    def get(self):
        try:
            nb_images = len(model.get_all_images())
            image_name = model.get_random_image_name()
            image_url = get_img_root_url(self.request) + image_name
            
            respond_template(self.response, 'home.html', {"image_url": image_url, "nb_images": str(nb_images)})
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

        <a href="/__/steal/bukit">steal some more bukkit images</a>
        </pre>
        """)


class GetImageHandler(webapp.RequestHandler):
    def get(self, file_name):
        image = model.get_image(file_name)
        if image:
            respond_image(image, self.response)
        else:
            self.redirect("/static/unexplainable.jpg")


class GetRandomImageHandler(webapp.RequestHandler):
    def get(self):
        image = model.get_random_image()
        respond_image(image, self.response, True)


class GetRandomImageAsJsonHandler(webapp.RequestHandler):
    def get(self):
        data = {
            "imagePath": get_img_root_url(self.request) + model.get_random_image().key().name()
        }

        respond_json(self.response, self.request, data)


class GetImageSearchListAsJsonHandler(webapp.RequestHandler):
    def get(self, query_string):
        images = model.get_image_search_list(query_string)
        
        data = {
            "query_string": query_string,
            "images": []
        }

        for image in images:
            data["images"].append(get_img_root_url(self.request) + image)

        respond_json(self.response, self.request, data)


class GetListOfImagesAsHtmlHandler(webapp.RequestHandler):
    def get(self):
        respond_template(self.response, 'list.html', {"images": model.get_all_images()})


class GetListOfImagesAsJsonHandler(webapp.RequestHandler):
    def get(self):
        images = model.get_all_images()

        data = {
            "images": []
        }

        for image in images:
            data["images"].append(get_img_root_url(self.request) + image)

        respond_json(self.response, self.request, data)


class DisplayAllImagesAsHtmlHandler(webapp.RequestHandler):
    def get(self):
        respond_template(self.response, 'view.html', {"images": model.get_all_images()})


class SearchThroughImagesAsHtmlHandler(webapp.RequestHandler):
    def get(self):
        images = model.get_all_images()

        image_list = []
        for image in images:
            image_list.append(image)

        respond_template(self.response, 'search.html', {"images": simplejson.dumps(image_list)})


class StealBukitImages(webapp.RequestHandler):
    def get(self):
        """
        To avoid doing long requests, just get the full list of images, then randomize it, and download the 10 first ones.
        Anyway, this will be cron'd, so we'll in the end get all images.
        """

        content = urllib2.urlopen("http://bukk.it").read()
        image_names = re.findall('<td><a href="(.*?)">(?:.*?)</a>', content, re.DOTALL)
        random.shuffle(image_names)

        i = 0
        for image_name in image_names:
            url = "http://bukk.it/" + image_name
            logging.info(">>> Stealing bukkit image: " + image_name + " (url: " + url + ")")
            model.store_image(url, image_name)
            i += 1
            if i > 10:
                break
        self.response.out.write("done ... downloaded 10 images on bukkit")


class UploadSingleImage(webapp.RequestHandler):
    def get(self):
        respond_template(self.response, 'add_single.html', {})

    def post(self):
        is_done = model.store_image(self.request.get("url"), self.request.get("file_name"))
        if is_done:
            self.response.out.write("Image " + self.request.get("file_name") + " added ! (from: " + self.request.get("url") + ").<br /><img src='/img/" + self.request.get("file_name") + "' /><br /><a href='/__/upload'>Add an other image</a>")
        else:
            self.response.out.write("Sorry, could not add image. Either there's already an image with the same name or the image couldn't be uploaded (probably more than 1Mb).<br /><a href='/__/upload'>Try again</a>")


"""
class StealGifTvImages(webapp.RequestHandler):
    def get(self):
        
        To avoid doing long requests, just download the 10 first ones. Anyway this will be cron'd as well.
        And on top of this, giftv always answers with different images

        nb = 0
        domain = "http://www.gif.tv/gifs/"
        page_url = domain + "get.php?unique=1333657713701"

        while nb < 10:
            nb += 1

            image_name = urllib2.urlopen(page_url).read()
            file_name = image_name + ".gif"
            image_url = domain + file_name
            simple_file_name = "-".join(file_name.split("-")[2:])

            logging.info(">>> Stealing giftv image: " + simple_file_name + " (url: " + image_url + ")")

            model.store_image(image_url, simple_file_name)

        self.response.out.write("done ... downloaded 10 images on giftv")


class StealMemeBaseImages(webapp.RequestHandler):
    def on_page_found(self, msg):
        images = re.findall("(http://chzmemebase.files.wordpress.com/[0-9]+/[0-9]+/internet-memes-([a-zA-Z\-]+)\.(jpg|png|gif))", msg)
        for image in images:
            logging.info("     ~~~ Found image: " + image[1] + "." + image[2] + " (on " + image[0][0:50] + "...)")
            model.store_image(image[0], image[1] + "." + image[2])

    def get(self):
        crawler.crawl("http://memebase.com/", self.on_page_found, 10)
        self.response.out.write("done ... crawled 10 pages on memebase")


class StealMemeBaseAfterDarkImages(webapp.RequestHandler):
    def on_page_found(self, msg):
        images = re.findall("(http://chzmemeafterdark.files.wordpress.com/[0-9]+/[0-9]+/naughty-memes-([a-zA-Z\-]+)\.(jpg|png|gif))", msg)
        for image in images:
            logging.info("     ~~~ Found image: " + image[1] + "." + image[2] + " (on " + image[0][0:50] + "...)")
            model.store_image(image[0], image[1] + "." + image[2])

    def get(self):
        crawler.crawl("http://memebaseafterdark.com/", self.on_page_found, 10)
        self.response.out.write("done ... crawled 10 pages on memebase afterdark")
"""

class DeleteImage(webapp.RequestHandler):
    def get(self):
        model.delete_image(self.request.get("file_name"))
        self.response.out.write("should be done")
