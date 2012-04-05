import os
import urllib2

while 1:
	domain = "http://www.gif.tv/gifs/"
	page_url = domain + "get.php?unique=1333657713701"
	image_name = urllib2.urlopen(page_url).read()
	file_name = image_name + ".gif"
	image_url = domain + file_name

	print "   ~ found image: " + image_url

	opener = urllib2.build_opener()
	picture_data = opener.open(image_url).read()

	simple_file_name = file_name.split("-")[2]
	fout = open(os.path.join("giftv", simple_file_name), "wb")
	fout.write(picture_data)
	fout.close()