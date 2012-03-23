import urllib2
import re
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

def get_bukkit_images():
		content = urllib2.urlopen("http://bukk.it").read()
		return re.findall('<td><a href="(.*?)">(?:.*?)</a>', content, re.DOTALL)

class MainHandler(webapp.RequestHandler):
	def get(self):
		images = get_bukkit_images()
		out = "<a href='/search' style='clear:both;'>Search</a><br />"
		for i in images:
			out += "<a href='http://bukk.it/" + i + "' style='float:left;display:block;margin:10px;text-align:center;font-size:10px;'>\
				<img src='http://bukk.it/" + i + "' / style='width:150px'>\
				<br />http://bukk.it/" + i + "\
			</a>"
		self.response.out.write(out)

class SearchHandler(webapp.RequestHandler):
	def get(self):
		images = get_bukkit_images()
		path = os.path.join(os.path.dirname(__file__), 'search.html')

		self.response.out.write(template.render(path, {"images": images}))

def main():
	application = webapp.WSGIApplication([
		('/search', SearchHandler),
		('/.*', MainHandler)
	], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
