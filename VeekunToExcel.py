#Makes a self-designed Excel file of a Pokedex from Veekun
#Uses selenium instead of BeautifulSoup, since clicking into entries is needed to retrieve images
#Creates NationalDex from VeekunDex
import time
from scraper import build_dir
import urllib.request
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class Pokemon():
    def __repr__(self):
        return str(self.__dict__)
        #(self.name, self.dex_num, self.sprite, self.typing, self.hp, self.atk, self.de, self.spA, self.spD, self.spe, self.total)
    def toData(self, row):
        col = 0
        for a in self.__dict__:
            value = (getattr(self, a))
            if value is None:
                col += 1
                continue
            if 'type' in a:
                worksheet.insert_image(row, col, value[0], {'x_offset': 15, 'y_offset': 15})
            elif a is 'sprite':
                worksheet.insert_image(row, col, value[0], {'x_scale': 0.5, 'y_scale': 0.5})
            else:
                worksheet.write(row, col, value, cell_format)
            col += 1

dirName = 'output/PokeImg'
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
type_to_icon = {}
workbook = xlsxwriter.Workbook('output/Pokedex.xlsx')
worksheet = workbook.add_worksheet('NationalDex')
worksheet.set_default_row(50)

bold = workbook.add_format({'bold': True, 'text_wrap': True})

cell_format = workbook.add_format({'text_wrap': True})
worksheet.set_column(0, 0, 15)
worksheet.freeze_panes(1, 0)
worksheet.freeze_panes(0, 1)

worksheet.write('A1', 'Name', bold)
worksheet.write('B1', 'Number', bold)
worksheet.write('C1', 'Image', bold)
worksheet.write('D1', 'Type', bold)
#Type takes two datas
worksheet.write('F1', 'HP', bold)
worksheet.write('G1', 'Attack', bold)
worksheet.write('H1', 'Defense', bold)
worksheet.write('I1', 'Special Attack', bold)
worksheet.write('J1', 'Special Defense', bold)
worksheet.write('K1', 'Speed', bold)
worksheet.write('L1', 'Total', bold)

def main():
    start = time.time()
    build_dir(dirName)
    type_scrape()
    pokedex_scrape()
    end = time.time()
    elapsed = end - start
    print(elapsed)
    quit()

def type_scrape():
    type_url = 'https://veekun.com/dex/types'
    driver.get(type_url)
    driver.implicitly_wait(5)
    typelist = driver.find_elements_by_xpath('//*[@id="content"]/ul/li/a/img')
    for t in typelist:
        type = t.get_attribute('title')
        source = t.get_attribute('src')
        icon = urllib.request.urlretrieve(source, "{}/{}.png".format(dirName,type))
        type_to_icon[type] = icon

def pokedex_scrape():
    url = "https://veekun.com/dex/pokemon/search?sort=evolution-chain&introduced_in=1&introduced_in=2&introduced_in=3&introduced_in=4&introduced_in=5&introduced_in=6&introduced_in=7"
    driver.get(url)
    driver.implicitly_wait(5)

    entries = driver.find_elements_by_xpath('//*[contains(@class,"evolution")]')

    row = 1
    #Program must click into each individual pokemon to retrieve Number and Sprite
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
        driver.implicitly_wait(10)
        #DEX_NUM
        dex_text = driver.find_element_by_id('dex-header').text
        req_text = str.split(str(dex_text), "\n")[3]
        poke.dex_num = ''.join(filter(str.isdigit,req_text))

        image = driver.find_element_by_xpath('//*[@id="dex-pokemon-portrait-sprite"]/img')
        src = image.get_attribute('src')
        try:
            poke.sprite = urllib.request.urlretrieve(src, "{}/{}.png".format(dirName,poke.name))
        except:
            poke.sprite = None
            pass

        typons = driver.find_elements_by_xpath('//*[@id="dex-page-types"]/a/img')
        if (len(typons)==1):
            poke.type_one = type_to_icon[typons[0].get_attribute('title')]
            poke.type_two = None
        else:
            poke.type_one = type_to_icon[typons[0].get_attribute('title')]
            poke.type_two = type_to_icon[typons[1].get_attribute('title')]

        stats = driver.find_elements_by_xpath('//*[@class="dex-pokemon-stats-bar"]')

        poke.hp = stats[0].text
        poke.atk = stats[1].text
        poke.df = stats[2].text
        poke.spA = stats[3].text
        poke.spD = stats[4].text
        poke.spe = stats[5].text
        poke.total = stats[6].text
        print('{}: {}'.format(poke.dex_num, poke.name))
        poke.toData(row)
        row += 1

        #Return to dex tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

def quit():
    print ("DONE")
    driver.close()
    driver.quit()
    workbook.close()
    exit()

if __name__ == "__main__":
    main()
