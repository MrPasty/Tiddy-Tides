from flask import Flask
from flask_ask import Ask, statement, question, session
from datetime import datetime, time
from bs4 import BeautifulSoup
import urllib
import json
import time
import requests
import time
import unidecode

# Get the current time and convert it to 24hours to match tide format
time12h = time.strftime("%I:%M %p")
timestrut = time.strptime(time12h, '%I:%M %p')
currenttime = time.strftime('%H:%M', timestrut)


# Read tide times in to variables to use later - note can pass a date on end of url like ..tide-times-20170918
soup = BeautifulSoup(urllib.request.urlopen('https://www.tidetimes.org.uk/st-germans-tide-times').read(), 'html5lib')
tableState = soup.find("table", {"id": "tidetimes"})

high =[]
low =[]

for row in tableState.findAll('tr')[2:]:
    col = row.findAll('td')

    try:
        tideType = col[0].string.strip()

        if (tideType == "High Tide") :
            tideTime = col[1].string.strip()
            high.append(tideTime)
        if (tideType == "Low Tide") :
            tideTime = col[1].string.strip()
            low.append(tideTime)
    except Exception as e:
        pass

# Populate the next high/low tide variable
next_hightide24H = ""
next_lowtide24H = ""
next_hightide12H = ""
next_lowtide12H = ""
last_tidetype = ""
last_tidetime = ""
hightides = 0
lowtides = 0

for h in high:
    if h >= currenttime:
        ht = datetime.strptime(h, "%H:%M")
        ht = ht.strftime("%I:%M %p")
        next_hightide24H = h
        next_hightide12H = ht
        for i in low:
            if i <= currenttime:
                i = datetime.strptime(i, "%H:%M")
                i = i.strftime("%I:%M %p")
                last_lowtidetime = i
                #last_tidetime = i
                #last_tidetype = "low"
        break

for l in low:
    if l >= currenttime:
        lt = datetime.strptime(l, "%H:%M")
        lt = lt.strftime("%I:%M %p")
        next_lowtide24H =  l
        next_lowtide12H = lt
        for i in high:
            if i <= currenttime:
                i = datetime.strptime(i, "%H:%M")
                i = i.strftime("%I:%M %p")
                last_hightidetime = i
                #last_tidetime = i
                #last_tidetype = "high"
        break


# Set last tide here
if last_hightidetime < last_lowtidetime:
    last_tidetype = "low"
    last_tidetime = last_lowtidetime
else:
    last_tidetype = "high"
    last_tidetime = last_hightidetime

# Set current tide state variable
if next_hightide12H == "":
    next_hightide12H = "High tide was at " +  last_tidetime + " so is now on its way out,  reaching low tide by " + next_lowtide12H
    hightides = 1

if next_lowtide12H == "":
    next_lowtide12H = "Low tide was at " +  last_tidetime + " so is now on its way in, reaching high tide by" + next_hightide12H
    lowtide = 1

# populate the next tide variable
if last_tidetype == "high":
    tide_state = "the tide is currently on the way out, ....  and will reach low tide at " + next_lowtide12H
else:
    tide_state = "the tide is currently on the way in, ....  and will reach high tide at " + next_hightide12H


# Variables to use next_hightide12H next_lowtide12H tide_state last_tide last_tidetime


app = Flask(__name__)
ask = Ask(app, "/tides")


@app.route('/', methods=['GET', 'POST'])
def homepage():
    return "hi there, how ya doin?"


@ask.launch
def start_skill():
    welcome_message = 'Hello, please invoke me by saying alexa ... ask the river .. when is high tide,  or when is low tide, you can even just ask what its doing, to know the details of the current tide'
    return statement(welcome_message)

@ask.intent("TideIntent", mapping={'tide': 'TideState'})
def announceTides(tide):
    if tide == "high":
        if hightides == 1:
            tideinfo = next_hightide12H
        else:
            tideinfo = "Today's high tide is at " + next_hightide12H

    if tide == "low":
        if lowtides == 1:
            tideinfo = next_lowtide12H
        else:
            tideinfo = "Today's low tide is at " + next_lowtide12H
    return statement('{}'.format(tideinfo))

@ask.intent("CurrentState")
def CurrentState():
    return statement('{}'.format(tide_state))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
