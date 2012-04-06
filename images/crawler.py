import re
import urllib2
import urlparse
import logging


def crawl(start_page, on_page_found, max_nb_of_pages):
    tocrawl = set([start_page])
    crawled = set([])
    linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')

    while 1:
        if len(crawled) >= max_nb_of_pages:
            break;

        try:
            crawling = tocrawl.pop()
            logging.info("~~~ crawling " + crawling[0:100] + " ...")
        except KeyError:
            raise StopIteration

        url = urlparse.urlparse(crawling)

        try:
            response = urllib2.urlopen(crawling)
        except:
            continue

        msg = response.read()
        on_page_found(msg)
        
        links = linkregex.findall(msg)
        crawled.add(crawling)
        for link in (links.pop(0) for _ in xrange(len(links))):
            if link.find(url.netloc) != -1:
                if link.startswith('/'):
                    link = 'http://' + url[1] + link
                elif link.startswith('#'):
                    link = 'http://' + url[1] + url[2] + link
                elif not link.startswith('http'):
                    link = 'http://' + url[1] + '/' + link
                if link not in crawled:
                    tocrawl.add(link)
