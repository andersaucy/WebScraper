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

dirName = 'PokemonIcons'
if not os.path.exists(dirName):
    os.mkdir(dirName)
    print("Directory " , dirName ,  " Created ")
else:
    print("Directory " , dirName ,  " already exists")

url = "https://veekun.com/dex/pokemon/search?sort=evolution-chain&introduced_in=1&introduced_in=2&introduced_in=3&introduced_in=4&introduced_in=5&introduced_in=6&introduced_in=7"
driver.get(url)
driver.implicitly_wait(10)

xpath = '//*[@id="content"]/table/tbody/tr'
entries = driver.find_elements_by_xpath('//*[contains(@class,"evolution")]')
# pprint(list[0].get_attribute('innerHTML'))
#Program must click into each individual pokemon to retrieve Number and Artwork
for entry in entries:
    link = entry.find_element_by_css_selector('td.name a')
    #NAME
    name = link.text
    action1 = ActionChains(driver)
    action1\
         .move_to_element(link)\
         .key_down(Keys.COMMAND)\
         .click(link)\
         .key_up(Keys.COMMAND)\
         .perform()
    driver.switch_to.window(driver.window_handles[1])

    #DEX_NUM
    dex_num = driver.find_element_by_xpath('//*[@id="content"]/div[4]/div[1]/dl[1]/dd[2]').text

    image = driver.find_element_by_xpath('//*[@id="dex-pokemon-portrait-sprite"]/img')
    src = image.get_attribute('src')
    urllib.request.urlretrieve(src, "{}/{}.png".format(dirName,name))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    pprint(name)
    pprint(dex_num)
    # driver.execute_script("window.history.go(-1)")

# driver.quit()
