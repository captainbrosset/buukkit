from random import choice
import logging

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import db


class Image(db.Model):
    content = db.BlobProperty(default=None)


class ImageInfo(db.Model):
    pass


def store_image(image_url, simple_file_name):
    if not get_image(simple_file_name):
        try:
            logging.info(">>> downloading image " + image_url)

            image = Image(key_name=simple_file_name)
            image.content = db.Blob(urlfetch.Fetch(image_url).content)
            image.put()

            image_info = ImageInfo(key_name=simple_file_name)
            image_info.put()

            # Re-create the memcache list
            set_image_keys_in_memcache()

            return True
        except:
            return False
    else:
        return False

IMAGE_KEY_LIST_MEMCACHE = "image_key_list"

def set_image_keys_in_memcache():
    image_key_list = []
    query = ImageInfo.all(keys_only=True)
    for result in query:
        if result.name() is not None:
            image_key_list.append(result.name())
    memcache.set(IMAGE_KEY_LIST_MEMCACHE, image_key_list)
    return image_key_list

def get_image_keys_from_memcache():
    image_key_list = memcache.get(IMAGE_KEY_LIST_MEMCACHE)
    if not image_key_list:
        image_key_list = set_image_keys_in_memcache()
    return image_key_list

def get_image(file_name):
    return Image.get_by_key_name(file_name)

def get_random_image_name():
    return choice(get_image_keys_from_memcache())

def get_random_image():
    return get_image(get_random_image_name())

def get_all_images():
    return get_image_keys_from_memcache()

def get_image_search_list(query_string):
    image_key_list = get_all_images()
    matching_images = []
    for image_name in image_key_list:
        if image_name.find(query_string) != -1:
            matching_images.append(image_name)
    return matching_images

def delete_image(file_name):
    info = ImageInfo.get_by_key_name(file_name)
    if info:
        info.delete()
        Image.get_by_key_name(file_name).delete()
        return True
    else:
        return False
