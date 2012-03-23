from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import urllib2
import re

class MainHandler(webapp.RequestHandler):
	def get(self):
		content = urllib2.urlopen("http://bukk.it").read()
		images = re.findall('<td><a href="(.*?)">(.*?)</a>', content, re.DOTALL)
		out = ""
		for i in images:
			out += "<a href='http://bukk.it/" + i[0] + "' style='float:left;display:block;margin:10px;text-align:center;font-size:10px;'>\
				<img src='http://bukk.it/" + i[0] + "' / style='width:150px'>\
				<br />http://bukk.it/" + i[0] + "\
			</a>"
		self.response.out.write(out)

def main():
	application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
