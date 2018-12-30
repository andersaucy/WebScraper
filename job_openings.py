#job_openings.py

###This program will check certain sites and open the sites that have open job positions

import scraper
import json
import webbrowser
from pprint import pprint

fandom = 'http://fandom.wikia.com/careers/office/new-york'

fscrape = scraper.Scrape(fandom)
open_roles = fscrape.get_all(".open-role-label")
if (len(open_roles)>1):
    webbrowser.open(fandom)
