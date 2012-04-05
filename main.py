import urllib2
import urlparse
import re
import os
import random
import json
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db


# TODO: Put a cron in place to update the bukit DB



class BukItBackupModel(db.Model):
    json = db.TextProperty(required=True)


def get_updated_bukit_json():
    content = urllib2.urlopen("http://bukk.it").read()
    images = re.findall('<td><a href="(.*?)">(?:.*?)</a>', content, re.DOTALL)
    return json.dumps(images)

def get_bukit_json_backup():
    try:
        return BukItBackupModel.all().fetch(1)[0].json
    except:
        json_data = get_updated_bukit_json()

        backup = BukItBackupModel(json=json_data)
        backup.put()

        return json_data

def store_bukit_json_backup(json):
    backup = BukItBackupModel.all().fetch(1)[0]
    backup.json = json
    backup.put()


def get_bukkit_images():
    json_data = get_bukit_json_backup()
    return json.loads(json_data)

def get_giftv_images():
    files = os.listdir(os.path.join("images", "giftv"))
    return [item for item in files if item[-3:] == "gif"]

def get_random_image_name():
    all_images = []

    bukit_images = get_bukkit_images()
    giftv_images = get_giftv_images()

    for i in bukit_images:
        all_images.append("http://bukk.it/" + i)

    for i in giftv_images:
        all_images.append("images/giftv/" + i)

    random_index = int(random.uniform(0, len(all_images)))
    random_image = all_images[random_index]

    return random_image 

def get_random_image_data():
    random_image = get_random_image_name()

    image_data = ""

    if random_image[0:4] == "http":
        image_data = get_remote_image_data(random_image)
    else:
        image_data = get_local_image_data(random_image)

    return (random_image, image_data)

def get_remote_image_data(image_file_name):
    opener = urllib2.build_opener()
    return opener.open(image_file_name).read()

def get_local_image_data(image_file_name):
    return open(image_file_name).read()

def respond_image(response, image_name, image_data):
    content_types = {
        "gif": "image/gif",
        "jpg": "image/jpeg",
        "png": "image/png"
    }

    try:
        response.headers.add_header("Content-Type", content_types[image_name[-3:]])
    except:
        # Here, the image extension is not in the list of known content_types, so just fallback
        response.headers.add_header("Content-Type", "images/gif")

    response.headers.add_header("Expires", "Thu, 01 Dec 1994 16:00:00 GMT")
    response.headers.add_header("X-original-image", image_name)

    response.out.write(image_data)


class HelpHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
            <pre>
                /images/(.*)        Returns an image

                /html/list/bukit    Shows the list of bukit images
                /html/list/giftv    Shows the list of giftv images

                /html/search/bukit  Gives a search tool for bukit
                /html/search/giftv  Gives a search tool for giftv

                /img/random.gif     Returns a random image
                /img/random         Returns a random image

                /json/random/(.*)   Returns a jsonp reponse for a random image (pass a callback as the last part)
                /json/random        Returns a json object for a random image
            </pre>
        """)


class HTMLListBukitImagesHandler(webapp.RequestHandler):
    def get(self):
        images = get_bukkit_images()
        out = ""
        for i in images:
            out += "<a href='http://bukk.it/" + i + "' style='float:left;display:block;margin:10px;text-align:center;font-size:10px;'>\
                <img src='http://bukk.it/" + i + "' / style='width:150px'>\
                <br />http://bukk.it/" + i + "\
            </a>"
        self.response.out.write(out)


class HTMLListGifTvImagesHandler(webapp.RequestHandler):
    def get(self):
        images = get_giftv_images()
        out = ""
        for i in images:
            out += "<a href='/images/giftv/" + i + "' style='float:left;display:block;margin:10px;text-align:center;font-size:10px;'>\
                <img src='/images/giftv/" + i + "' / style='width:150px'>\
                <br />/images/giftv/" + i + "\
            </a>"
        self.response.out.write(out)


class HTMLSearchBukitHandler(webapp.RequestHandler):
    def get(self):
        images = get_bukkit_images()
        path = os.path.join(os.path.dirname(__file__), 'search.html')

        self.response.out.write(template.render(path, {"images": images}))


class HTMLSearchGifTvHandler(webapp.RequestHandler):
    def get(self):
        images = get_giftv_images()
        path = os.path.join(os.path.dirname(__file__), 'searchgiftv.html')

        self.response.out.write(template.render(path, {"images": images}))


class StaticImageHandler(webapp.RequestHandler):
    def get(self, image_path):
        image_name = os.path.join("images", image_path)
        image_data = get_local_image_data(image_name)
        respond_image(self.response, image_name, image_data)


class IMGRandomHandler(webapp.RequestHandler):
    def get(self):
        image_info = get_random_image_data()
        respond_image(self.response, image_info[0], image_info[1])


class JSONRandomHandler(webapp.RequestHandler):
    def get(self, callback=None):
        image_info = get_random_image_data()
        image_path = image_info[0]

        if image_path[0:4] != "http":
            o = urlparse.urlparse(self.request.url)
            image_path = "http://" + o.netloc + "/" + image_path

        data = {
            "imagePath": image_path
        }
        json_data = json.dumps(data)
        if callback:
            json_data = callback + "(" + json_data + ");"
        self.response.out.write(json_data)


def main():
    application = webapp.WSGIApplication([
        ('/images/(.*)', StaticImageHandler),

        ('/html/list/bukit', HTMLListBukitImagesHandler),
        ('/html/list/giftv', HTMLListGifTvImagesHandler),
        # TODO: ('/html/list', HTMLListImagesHandler),

        ('/html/search/bukit', HTMLSearchBukitHandler),
        ('/html/search/giftv', HTMLSearchGifTvHandler),
        # TODO: ('/html/search', HTMLSearchHandler),

        ('/img/random\.gif', IMGRandomHandler),
        ('/img/random', IMGRandomHandler),

        ('/json/random/(.*)', JSONRandomHandler),
        ('/json/random', JSONRandomHandler),

        ('.*', HelpHandler)
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
