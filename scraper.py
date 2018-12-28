#scraper.py
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup

class Scrape:
    def __init__(self, source):
        uClient = uReq(source)
        page_html = uClient.read()
        uClient.close()
        self.soup = BeautifulSoup(page_html, "html.parser")

    def get(self, tag):
        return self.soup.find(tag)
