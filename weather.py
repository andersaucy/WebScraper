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
shower = emoji.emojize(':shower:', use_aliases=True)
clear = emoji.emojize(':white_check_mark:', use_aliases=True)
daynames = {
    "SUN:":"SUNDAY:",
    "MON:":"MONDAY:",
    "TUES:":"TUESDAY:",
    "WED:":"WEDNESDAY:",
    "THURS:":"THURSDAY:",
    "FRI:":"FRIDAY:",
    "SAT:":"SATURDAY:"
}

weathers = {
    "LOW\n":"","HIGH\n":"","°":"°F",
    "CLOUDY":"CLOUDY"+cloud,
    "RAIN":"RAIN"+rain,
    "SUNNY":"SUNNY"+sun,
    "STORM":"STORM"+storm,
    "SHOWERS":"SHOWERS"+shower,
    "CLEAR":"CLEAR" + clear
}

def main():
    startup()
    schedule.every().day.at("06:30").do(job)
    while True:
        schedule.run_pending()
        signal.signal(signal.SIGINT, signal_handler)
        time.sleep(1)

def startup():
    global smtpObj
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    collect_info()
    approved = False
    while (not approved): #USE A DO_WHILE
        try:
            smtpObj.login(usr, pw)
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
        x_out = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.id, "kplDeferButton")));
        # x_out = driver.find_element_by_id('kplDeferButton')
        if(x_out):
            print("POPUP!")
        x_out.click()
        time.sleep(2)
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

    #Farenheit and Weather Emojis
    for weather in weathers.keys():
        forecast = forecast.replace(weather, weathers[weather])
    #Daynames
    for day in daynames.keys():
        forecast = forecast.replace(day, daynames[day])

    # temp = re.findall(r'\n\d+°F', forecast)
    # for t in temp:
    #     forecast = forecast.replace(t, bprint(t))
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

    closing = '\n\n{} Weather Report brought to you by {}\nPlease reply with any suggestions on how to improve this experience!'.format(city, url)

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
    # forecast = header + forecast + text
        msg.attach(part1)
        msg.attach(part2)
        msg.attach(part3)

    #Self
        #smtpObj.sendmail(usr, usr,  msg.as_string())
    #Others
        smtpObj.sendmail(usr, p_email,  msg.as_string())
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
    elif (call == 'test'):
        job()
        exit()
    else:
        bprint('Returning to main dialog')

if __name__ == "__main__":
    main()
