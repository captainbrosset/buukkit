import urllib2
import re
import logging
import random
from urlparse import urlparse
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson

import model


def get_img_root_url(request):
    o = urlparse(request.url)
    return o.scheme + "://" + o.netloc + "/img/"


def respond_image(db_image, response):
    content_types = {
        "gif": "image/gif",
        "jpg": "image/jpeg",
        "png": "image/png"
    }

    response.headers["Expires"] = "Thu, 01 Dec 1994 16:00:00 GMT"
    response.headers["Content-Type"] = content_types[db_image.file_name[-3:]]
    response.headers["X-image-name"] = db_image.file_name
    response.out.write(db_image.content)


def respond_json(response, request, data):
    json_data = simplejson.dumps(data)
    if request.get('cb'):
        json_data = request.get('cb') + "(" + json_data + ");"

    response.out.write(json_data)


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
        respond_image(image, self.response)


class GetRandomImageAsJsonHandler(webapp.RequestHandler):
    def get(self):
        data = {
            "imagePath": get_img_root_url(self.request) + model.get_random_image().file_name
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
            data["images"].append(get_img_root_url(self.request) + image.file_name)

        respond_json(self.response, self.request, data)


class GetListOfImagesAsHtmlHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'list.html')
        self.response.out.write(template.render(path, {"images": model.get_all_images()}))


class GetListOfImagesAsJsonHandler(webapp.RequestHandler):
    def get(self):
        images = model.get_all_images()

        data = {
            "images": []
        }

        for image in images:
            data["images"].append(get_img_root_url(self.request) + image.file_name)

        respond_json(self.response, self.request, data)


class DisplayAllImagesAsHtmlHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'view.html')
        self.response.out.write(template.render(path, {"images": model.get_all_images()}))


class SearchThroughImagesAsHtmlHandler(webapp.RequestHandler):
    def get(self):
        images = model.get_all_images()

        image_list = []
        for image in images:
            image_list.append(image.file_name)

        path = os.path.join(os.path.dirname(__file__), '..', 'search.html')
        self.response.out.write(template.render(path, {"images": simplejson.dumps(image_list)}))


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
        self.response.out.write("done ... stole 10 images")


class StealGifTvImages(webapp.RequestHandler):
    def get(self):
        """
        To avoid doing long requests, just download the 10 first ones. Anyway this will be cron'd as well.
        And on top of this, giftv always answers with different images
        """

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

        self.response.out.write("done ... stole 10 images")
