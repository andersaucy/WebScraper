#weather.py
import datetime
import time
import schedule
import smtplib
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


usr = None
pw =  None
url = "https://www.weather.com"
cloud = emoji.emojize(':cloud:', use_aliases=True)
rain = emoji.emojize(':sweat_drops:',use_aliases=True)
drop = emoji.emojize(':droplet:', use_aliases=True)
umbrella = emoji.emojize(':umbrella:', use_aliases=True)
sun = emoji.emojize(':sunny:', use_aliases=True)
storm = emoji.emojize(':zap:',use_aliases=True)

daynames = {"SUN:":"SUNDAY:", "MON:":"MONDAY:", "TUES:":"TUESDAY:", "WED:":"WEDNESDAY:", "THURS:":"THURSDAY:","FRI:":"FRIDAY:","SAT:":"SATURDAY:"}
weathers = {"LOW\n":"","HIGH\n":"","°":"°F","CLOUDY":"CLOUDY"+cloud,"RAIN":"RAIN"+rain, "SUNNY":"SUNNY"+sun, "STORM":"STORM"+storm}

def main():
    startup()
    schedule.every().day.at("06:30").do(job)
    while True:
        schedule.run_pending()
        signal.signal(signal.SIGINT, signal_handler)
        time.sleep(1)

def startup():
    global usr
    global pw
    bprint('Sender Email Address:')
    usr = input()
    bprint('Password:')
    pw = input()
    bprint('Running...')
    bprint('Press Ctrl+C to enter command')

def job():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(10)

    dt = datetime.datetime.now()
    date = dt.strftime('%B %d, %Y')

    #TODAY Xpath
    TODAY_elem = driver.find_element_by_xpath('//*[@id="header-LocalsuiteNav-9e937d06-a4be-493a-bc54-942db4a05af8"]/div/div/div/ul/li[1]/a')
    TODAY_elem.click()
    driver.implicitly_wait(15)
    time.sleep(10)

    #handle popup
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
    #Raindrops and Umbrellas
    rain_check = re.findall(r'\d+%', forecast)
    seen = []
    for rc in rain_check:
        if rc not in seen:
            bring_umbrella = int(rc.strip('%')) > 55
            if bring_umbrella:
                forecast = re.sub(rc, rc + drop + umbrella, forecast)
            elif not bring_umbrella:
                forecast = re.sub(rc, rc + drop, forecast)
            seen.append(rc)
        elif rc in seen:
            continue

    #Farenheit and Weather Emojis
    for weather in weathers.keys():
        forecast = forecast.replace(weather, weathers[weather])
    #Daynames
    for day in daynames.keys():
        forecast = forecast.replace(day, daynames[day])
    print (forecast)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "AnderWeather: {}".format(date)
    msg['From'] = usr
    msg['To'] = usr

    text = '\n\nReport brought to you by ' + url + '\nFeel free to reply with any suggestions on how to improve this experience!'
    forecast = forecast + text
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(forecast, 'plain')
    msg.attach(part1)
    msg.attach(part2)

    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(usr, pw)

#    recipients = emaildb.loadDB()
    # for recip in recipients:
    #     bprint(recip)
    #     smtpObj.sendmail(usr, recip, msg.as_string())

    #Self
    #smtpObj.sendmail(usr, usr,  msg.as_string())
    #Others
    # smtpObj.sendmail(usr, Emails.SEAN_EMAIL, msg.as_string())
    # smtpObj.sendmail(usr, Emails.STEVEN_EMAIL, msg.as_string())
    # smtpObj.sendmail(usr, Emails.ERICA_EMAIL,  msg.as_string())
    # smtpObj.sendmail(usr, Emails.JENNY_EMAIL,  msg.as_string())
    #bprint('All emails sent')
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
    else:
        bprint('Returning to main dialog')

if __name__ == "__main__":
    main()
