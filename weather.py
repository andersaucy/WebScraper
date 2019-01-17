#weather.py
#Emails using gmail faily weather reports
import datetime
import time
import schedule
import smtplib
import requests
import json
import re
import emoji
import signal
import emaildb
from emaildb import bprint
import Emails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

usr = None
pw =  None
smtpObj = None
url = "https://www.weather.com"
cloud = emoji.emojize(':cloud:', use_aliases=True)
rain = emoji.emojize(':sweat_drops:',use_aliases=True)
drop = emoji.emojize(':droplet:', use_aliases=True)
umbrella = emoji.emojize(':umbrella:', use_aliases=True)
sun = emoji.emojize(':sunny:', use_aliases=True)
storm = emoji.emojize(':zap:',use_aliases=True)
shower = emoji.emojize(':shower:', use_aliases=True)
clear = emoji.emojize(':white_check_mark:', use_aliases=True)
wind = emoji.emojize(':dash:', use_aliases = True)
daynames = {
    "SUN:":"SUNDAY:",
    "MON":"MONDAY",
    "TUE":"TUESDAY",
    "WED":"WEDNESDAY",
    "THU":"THURSDAY",
    "FRI":"FRIDAY",
    "SAT":"SATURDAY"
}

weathers = {
    "LOW\n":"","HIGH\n":"",
    "CLOUDY":"CLOUDY"+cloud,
    "CLOUDS":"CLOUDS"+cloud,
    "RAIN":"RAIN"+rain,
    "SUNNY":"SUNNY"+sun,
    "STORM":"STORM"+storm,
    "SHOWERS":"SHOWERS"+shower,
    "CLEAR":"CLEAR" + clear,
    "WIND":"WIND" + wind
}

def main():
    startup()
    schedule.every().day.at("06:29").do(lambda: job(True))
    while True:
        schedule.run_pending()
        signal.signal(signal.SIGINT, signal_handler)
        time.sleep(1)

def startup():
    global smtpObj
    mail = connect(smtpObj)
    approved = False
    collect_info()
    while (not approved): #USE A DO_WHILE
        try:
            mail.login(usr, pw)
            approved = True
        except:
            bprint("Try again!")
            collect_info()
    bprint('Running...')
    bprint('Press Ctrl+C to enter command')

def collect_info():
    global usr
    global pw
    bprint('Sender Email Address:')
    usr = input()
    bprint('Password:')
    pw = input()

def connect(connect):
    connect = smtplib.SMTP('smtp.gmail.com', 587)
    connect.ehlo()
    connect.starttls()
    return connect

def is_connected(connect):
    try:
        status = connect.noop()[0]
    except:
        status = -1
    return True if status == 250 else False

def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def locate(driver):
    iploc = 'https://www.iplocation.net/'
    driver.get(iploc)
    IPAddr_elem =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="wrapper"]/section/div/div/div[1]/div[5]/div[2]/p/span[1]')))
    IPAddr = IPAddr_elem.text
    print (IPAddr)
    geo_req = requests.get('http://api.ipstack.com/{}?access_key={}'.format(IPAddr,Emails.LocationKEY))
    geo_json = json.loads(geo_req.text)
    city = geo_json['city'] + ', ' + geo_json['region_code']
    return city

def far_cel(far):
    raw_cel = (far-32) * (5/9)
    return int(round(raw_cel))

def job(run):
    #run is a boolean, if True, it will send. if False, emails will be sent to self
    global usr
    global pw
    global smtpObj
    if not is_connected(smtpObj):
        smtpObj = connect(smtpObj)
        smtpObj.login(usr,pw)

    driver = start_driver()
    city = locate(driver)

    dt = datetime.datetime.now()
    date = dt.strftime('%B %d, %Y')

    driver.get(url)

    location_form = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="header-TwcHeader-10c7c60c-aebb-4e78-b655-512b2460d9f4"]/div/div/div/div[1]/div/div[1]/div/input')))
    location_form.send_keys(city)
    time.sleep(3)
    location_form.send_keys(Keys.ARROW_DOWN)
    location_form.send_keys(Keys.RETURN)

    driver.implicitly_wait(10)
    time.sleep(2)
    #TODAY Xpath
    TODAY_elem = driver.find_element_by_xpath('//*[@id="header-LocalsuiteNav-9e937d06-a4be-493a-bc54-942db4a05af8"]/div/div/div/ul/li[1]/a')
    TODAY_elem.click()
    driver.implicitly_wait(15)
    time.sleep(10)

    #handle popup
    try:
        x_out = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.id, "kplDeferButton")));
        # x_out = driver.find_element_by_id('kplDeferButton')
        if(x_out):
            print("POPUP!")
        x_out.click()
        time.sleep(2)
    except:
        pass

    looking_ahead = driver.find_elements_by_class_name('today-daypart-content')
    print (looking_ahead[0].get_attribute('innerHTML'))

    fc = []
    for l in looking_ahead:
        l.click()
        time.sleep(1)
        daycast = l.text
        #format
        report = re.sub(r'\n',r': ', daycast, 1)
        #insert appropriate forescast emoji
        fc.append(report)

    forecast = '\n\n'.join(fc)

    degrees = re.findall(r'\n\d+°', forecast)
    for d in degrees:
        farenheit = int(d.strip('°'))
        celsius = far_cel(farenheit)
        forecast = re.sub(d, d + 'F | ' + str(celsius) + '°C', forecast)

    #Farenheit and Weather Emojis
    for weather in weathers.keys():
        forecast = forecast.replace(weather, weathers[weather])
    #Daynames
    for day in daynames.keys():
        forecast = forecast.replace(day, daynames[day])

    #Raindrops and Umbrellas
    rain_check = re.findall(r'\n\d+%', forecast)
    seen = []

    for rc in rain_check:
        if rc not in seen:
            seen.append(rc)
            bring_umbrella = int(rc.strip('%')) > 55
            if bring_umbrella:
                forecast = re.sub(rc, rc + drop + umbrella, forecast)
            elif not bring_umbrella:
                forecast = re.sub(rc, rc + drop, forecast)
        elif rc in seen:
            continue

    print(forecast)

    closing ="""\n\n{} Weather Report stolen from {} and brought to you by me, Anderson!\n\
Please reply with any suggestions on how to improve your daily weather report consumption experience!""".format(city, url)

    part2 = MIMEText(forecast, 'plain')
    part3 = MIMEText(closing, 'plain')
    recipients = emaildb.loadDB()

    for recip in recipients:
        bprint ("Sending to ")
        print(recip)
        p_name = recip[0]
        p_email = recip[1]
        header = 'Good morning, ' + p_name + '! The forecast is as follows! \n\n'

        msg = MIMEMultipart()
        msg['Subject'] = "AnderWeather: {}".format(date)
        msg['From'] = usr
        msg['To'] = p_email

        part1 = MIMEText(header, 'plain')

        msg.attach(part1)
        msg.attach(part2)
        msg.attach(part3)

    #Self
        if run is False:
            smtpObj.sendmail(usr, usr,  msg.as_string())
            break
    #Others
        elif run is True:
            smtpObj.sendmail(usr, p_email,  msg.as_string())

    bprint('All emails sent')
    driver.quit()

def signal_handler(signal, frame):
    bprint('\nEnter command (Ctrl+C to terminate . "back" to return)')
    call = input()
    if (call == 'list'):
        emaildb.email_list()
        bprint('Press Ctrl+C to enter command')
        pass
    elif (call == 'restart'):
        emaildb.restartDB()
        bprint('Press Ctrl+C to enter command')
        pass
    elif (call == 'add'):
        emaildb.add_email()
        bprint('Press Ctrl+C to enter command')
        pass
    elif (call == 'delete'):
        emaildb.delete_email()
        bprint('Press Ctrl+C to enter command')
        pass
    elif (call == 'test'):
        job(False)
        bprint('Returning to main dialog')
        bprint('Press Ctrl+C to enter command')
    else:
        bprint('Returning to main dialog')
        bprint('Press Ctrl+C to enter command')
        pass

if __name__ == "__main__":
    main()
