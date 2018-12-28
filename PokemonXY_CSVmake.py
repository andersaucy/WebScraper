#/anaconda3/bin/python
#Takes pokemon statistics from Smogon and puts it into a csv
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup
import json
import csv
import pprint

source = "https://www.smogon.com/dex/xy/pokemon/"
uClient = uReq(source)
page_html = uClient.read()
uClient.close()

#html parse
#page contains JSON in script tag
page_soup = BeautifulSoup(page_html, "html.parser")
script = page_soup.find('script')
jsonValue = '{%s}' % (script.text.partition('{')[2].rpartition('}')[0],)
value = json.loads(jsonValue)

#Retrieve the database
database = value['injectRpcs'][1][1]

#Retrieve the pokedex
pokedex = database['pokemon']
# pprint.pprint(pokedex)

#Prepare file write
filename = "Pokédex_XY.csv"
f = csv.writer(open(filename, "w"))
headers = "Pokemon, Typing, Abilities, HP, Attack, Defense, SpA, SpD, Spe\n"
first = ["Pokemon", "Typing", "Abilities", "HP", "Attack", "Defense", "SpA", "SpD", "Spe"]
f.writerow(first)

#There are 787 Pokemon in the dex, but there are 23 Fakemons that we don't care about
#Zygarde is No. 763
#print.pprint(pokedex[0])
for pokemon in pokedex[:-23]:
    name_stem = pokemon['name']
    all_stats = pokemon['alts']
    for stats in all_stats:

        _types = '/'.join(stats['types'])
        _atk = str(stats['atk'])
        _def = str(stats['def'])
        _hp  = str(stats['hp'])
        _spa = str(stats['spa'])
        _spd = str(stats['spd'])
        _spe = str(stats['spe'])
        _abil = ', '.join(stats['abilities'])
        _suff = stats['suffix']
        if (len(_suff)>0):
            full_name = name_stem + (" ({})".format(_suff))
        else:
            full_name = name_stem
        row_data = [full_name,_types,_abil,_hp,_atk,_def,_spa,_spd,_spe]
        f.writerow(row_data)
