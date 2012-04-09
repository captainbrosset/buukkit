import random
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import db


class Image(db.Model):
    file_name = db.StringProperty()
    content = db.BlobProperty(default=None)
    rand_num = db.FloatProperty()


def store_image(image_url, simple_file_name):
    if not get_image(simple_file_name):
        try:
            logging.info(">>> downloading image " + image_url)

            image = Image()
            image.content = db.Blob(urlfetch.Fetch(image_url).content)
            image.file_name = simple_file_name
            image.rand_num = random.random()
            image.put()

            return True
        except:
            return False
    else:
        return False

def get_image(file_name):
    result = db.GqlQuery("SELECT * FROM Image WHERE file_name = :1 LIMIT 1", file_name).fetch(1)
    if (len(result) > 0):
        return result[0]
    else:
        return None

def get_all_images():
    return db.GqlQuery("SELECT * FROM Image")

def get_random_image():
    rand_num = random.random()
    image = Image.all().order('rand_num').filter('rand_num >=', rand_num).get()
    if image is None:
        image = Image.all().order('rand_num').get()
    return image

def get_image_search_list(query_string):
    images = get_all_images()
    matching_images = []
    for image in images:
        if image.file_name.find(query_string) != -1:
            matching_images.append(image)
    return matching_images