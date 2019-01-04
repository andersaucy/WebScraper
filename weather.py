#weather.py
import datetime
import time
import schedule
import smtplib
import re
import emoji
import signal
import threading
import sys
from emailaddresses import bprint
import emailaddresses as emails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

usr = emails.ANDERSON_EMAIL
pw = emails.ANDERSON_PW
daynames = {"SUN":"SUNDAY", "MON":"MONDAY", "TUES":"TUESDAY", "WED":"WEDNESDAY", "THURS":"THURSDAY","FRI":"FRIDAY","SAT":"SATURDAY"}

def job():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.weather.com")
    driver.implicitly_wait(10)

    dt = datetime.datetime.now()
    date = dt.strftime('%B %d, %Y')

    TODAYxpath = '//*[@id="header-LocalsuiteNav-9e937d06-a4be-493a-bc54-942db4a05af8"]/div/div/div/ul/li[1]/a'

    TODAY_elem = driver.find_element_by_xpath(TODAYxpath)
    TODAY_elem.click()
    driver.implicitly_wait(15)
    time.sleep(10)

    try:
        x_out = driver.find_element_by_id('kplDeferButton')
        x_out.click()
        time.sleep(5)
    except:
        pass

    looking_ahead = driver.find_elements_by_class_name('today-daypart-content')
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
    cloud = emoji.emojize(':cloud:', use_aliases=True)
    rain = emoji.emojize(':sweat_drops:',use_aliases=True)
    drop = emoji.emojize(':droplet:', use_aliases=True)
    umbrella = emoji.emojize(':umbrella:', use_aliases=True)

    rain_check = re.findall(r'\d+%', forecast)
    seen = []
    for ra in rain_check:
        if ra not in seen:
            if (int(ra.strip('%')) > 55):
                forecast = re.sub(ra, ra + drop + umbrella, forecast)
            else:
                forecast = re.sub(ra, ra + drop, forecast)
            seen.append(ra)
        elif ra in seen:
            continue
    forecast = forecast.replace('LOW\n', '')
    forecast = forecast.replace('HIGH\n', '')
    forecast = forecast.replace('°', '°' + 'F')
    forecast = forecast.replace('CLOUDY', 'CLOUDY' + cloud)
    forecast = forecast.replace('RAIN', 'RAIN' + rain)
    for day in daynames.keys():
        forecast = forecast.replace(day, daynames[day])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "AnderWeather: {}".format(date)
    msg['From'] = usr
    msg['To'] = usr

    text = '\nAy,\nCheck this site for the weather: ' + driver.current_url
    forecast = forecast + text
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(forecast, 'plain')
    msg.attach(part1)
    msg.attach(part2)

    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(usr, pw)

    recipients = emails.loadDB()
    # for recip in recipients:
    #     bprint(recip)
    #     smtpObj.sendmail(usr, recip, msg.as_string())

    smtpObj.sendmail(usr, usr,  msg.as_string())
    smtpObj.sendmail(usr, emails.SEAN_EMAIL, msg.as_string())
    smtpObj.sendmail(usr, emails.STEVEN_EMAIL, msg.as_string())
    smtpObj.sendmail(usr, emails.ERICA_EMAIL,  msg.as_string())
    bprint('All emails sent', None)
    driver.quit()

schedule.every().day.at("06:31").do(job)

def signal_handler(signal, frame):
    bprint('\nEnter command (Ctrl+C to terminate . "back" to return)', None)
    call = input()
    if (call == 'list'):
        emails.email_list()
        bprint('Press Ctrl+C to enter command', None)
        pass
    elif (call == 'restart'):
        emails.restartDB()
        bprint('Press Ctrl+C to enter command', None)
        pass
    elif (call == 'add'):
        emails.add_email()
        bprint('Press Ctrl+C to enter command', None)
        pass
    else:
        bprint('Returning to main dialog', None)

bprint('Press Ctrl+C to enter command', None)
while True:
    schedule.run_pending()
    signal.signal(signal.SIGINT, signal_handler)
    time.sleep(1)
