#/anaconda3/bin/python
#Takes pokemon statistics from Smogon and puts it into csv files
import scraper
import os
import json
import csv
from pprint import pprint

generations = ['rb','gs','rs','dp','bw','xy','sm']
#make directory to hold the CSVs
dirName = 'CSVs'
if not os.path.exists(dirName):
    os.mkdir(dirName)
    print("Directory " , dirName ,  " Created ")
else:
    print("Directory " , dirName ,  " already exists")

for gen in generations:
    scrape = scraper.Scrape("https://www.smogon.com/dex/{}/pokemon/".format(gen))
    script = scrape.get('script')

    #page contains JSON in script tag
    jsonValue = '{%s}' % (script.text.partition('{')[2].rpartition('}')[0],)
    value = json.loads(jsonValue)

    #Maneuver json to the Pokedex
    database = value['injectRpcs'][1][1]

    #Retrieve the pokedex entries
    pokedex = database['pokemon']

    #Prepare file write
    filename = "CSVs/Pokédex_{}.csv".format(gen.upper())
    f = csv.writer(open(filename, "w"))
    first = ["Pokemon", "Typing", "Abilities", "HP", "Attack", "Defense", "SpA", "SpD", "Spe"]
    f.writerow(first)


    for pokemon in pokedex:
        #Skips create-a-pokemons
        if (pokemon['cap']):
            continue
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
