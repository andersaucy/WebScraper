#Makes a self-designed Excel file of a Pokedex from Veekun
#Uses selenium instead of BeautifulSoup, since clicking into entries is needed to retrieve images
from pprint import pprint
import time
import os
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

dirName = 'PokeImg'
type_to_icon = {}

def main():
    start = time.time()
    build_dir()
    type_scrape()
    pokedex_scrape()

    end = time.time()
    elapsed = end - start
    pprint(elapsed)
    driver.quit()

def build_dir():
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ")
    else:
        print("Directory " , dirName ,  " already exists")

def type_scrape():

    type_url = 'https://veekun.com/dex/types'
    driver.get(type_url)
    driver.implicitly_wait(10)

    typelist = driver.find_elements_by_xpath('//*[@id="content"]/ul/li/a/img')
    for t in typelist:
        type = t.get_attribute('title')
        source = t.get_attribute('src')
        icon = urllib.request.urlretrieve(source, "{}/{}.png".format(dirName,type))
        type_to_icon[type] = icon




class Pokemon():
    pass



if not os.path.exists(dirName):
    os.mkdir(dirName)
    print("Directory " , dirName ,  " Created ")
else:
    print("Directory " , dirName ,  " already exists")

#
def pokedex_scrape():
    url = "https://veekun.com/dex/pokemon/search?sort=evolution-chain&introduced_in=1&introduced_in=2&introduced_in=3&introduced_in=4&introduced_in=5&introduced_in=6&introduced_in=7"
    driver.get(url)
    driver.implicitly_wait(10)

    entries = driver.find_elements_by_xpath('//*[contains(@class,"evolution")]')
    # pprint(list[0].get_attribute('innerHTML'))

    #Program must click into each individual pokemon to retrieve Number and Artwork
    for entry in entries:
        poke = Pokemon()
        link = entry.find_element_by_css_selector('td.name a')
        #NAME
        poke.name = link.text
        action = ActionChains(driver)
        action\
             .move_to_element(link)\
             .key_down(Keys.COMMAND)\
             .click(link)\
             .key_up(Keys.COMMAND)\
             .perform()
        driver.switch_to.window(driver.window_handles[1])

        #DEX_NUM
        poke.dex_num = driver.find_element_by_xpath('//*[@id="content"]/div[4]/div[1]/dl[1]/dd[2]').text


        image = driver.find_element_by_xpath('//*[@id="dex-pokemon-portrait-sprite"]/img')
        src = image.get_attribute('src')
        poke.sprite = urllib.request.urlretrieve(src, "{}/{}.png".format(dirName,poke.name))

        typons = driver.find_elements_by_xpath('//*[@id="dex-page-types"]/a/img')
        if (len(typons)==1):
            poke.typing = (type_to_icon[typons[0].get_attribute('title')])
        else:
            poke.typing = (type_to_icon[typons[0].get_attribute('title')],type_to_icon[typons[1].get_attribute('title')])

        stats = driver.find_elements_by_xpath('//*[@class="dex-pokemon-stats-bar"]')

        poke.hp = stats[0].text
        poke.atk = stats[1].text
        poke.de = stats[2].text
        poke.spA = stats[3].text
        poke.spD = stats[4].text
        poke.spe = stats[5].text
        poke.total = stats[6].text

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        pprint(poke.name)
        pprint(poke.dex_num)
        pprint(poke.sprite)
        pprint(poke.typing)
        pprint(poke.hp )
        pprint(poke.atk)
        pprint(poke.de)
        pprint(poke.spA)
        pprint(poke.spD)
        pprint(poke.spe)
        pprint(poke.total)


if __name__ == "__main__":
    main()
