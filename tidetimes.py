from datetime import datetime, time
from flask import Flask
from flask_ask import Ask, statement, question, session
from bs4 import BeautifulSoup
import urllib
import json
import time
import requests
import time
import unidecode



next_tide = ""
next_tidetime = ""
last_tide = ""
last_tidetime = ""
next_hightidetime = ""
next_lowtidetime = ""
tide_state = ""
lowtides = 0
hightides = 0


def convert12H(time24):
    time12 = datetime.strptime(time24, "%H:%M")
    time12 = time12.strftime("%I:%M %p")
    return time12

def lastTide(lt):
    global last_tidetime
    global last_tide
    lt = lt.split('#',1)
    last_tidetime = convert12H(lt[0] )
    last_tide = lt[1]


def parseTides():
    # Get the current time and convert it to 24hours to match tide format
    time12h = time.strftime("%I:%M %p")
    timestrut = time.strptime(time12h, '%I:%M %p')
    currenttime = time.strftime('%H:%M', timestrut)
    tides = []

    # Read tide times in to variables to use later - note can pass a date on end of url like ..tide-times-20170918
    soup = BeautifulSoup(urllib.request.urlopen('https://www.tidetimes.org.uk/st-germans-tide-times').read(), 'html5lib')
    tableState = soup.find("table", {"id": "tidetimes"})

    for row in tableState.findAll('tr')[2:]:
        col = row.findAll('td')
        try:
            tideType = col[0].string.strip()
            if (tideType == "High Tide") :
                tideTime = col[1].string.strip()
                tides.append(tideTime + "#" + "high")
            if (tideType == "Low Tide") :
                tideTime = col[1].string.strip()
                tides.append(tideTime + "#" + "low")
        except Exception as e:
            pass


    time12h = time.strftime("%I:%M %p")
    time24h = time.strptime(time12h, '%I:%M %p')
    currenttime = time.strftime('%H:%M', time24h)
    tideslen = len(tides)
    global next_tide
    global next_tidetime
    global last_tide
    global last_tidetime
    global last_tidetime
    global next_hightidetime
    global next_lowtidetime
    global tide_state
    global lowtides
    global hightides

    # as our list is in order we can just itterate it to het next tide
    for tide in tides:
        tideindex = tides.index(tide)
        t = tide.split('#',1)
        tidetime = t[0]
        tidetype = t[1]
        t = datetime.strptime(tidetime, '%H:%M')
        c = datetime.strptime(currenttime, '%H:%M')
        if t.hour > c.hour:
            # Set next tide details here
            next_tide = tidetype
            next_tidetime = convert12H(tidetime)
            # Set the last tide
            lastTide(tides[tideindex - 1])
            break
        if t.hour == c.hour:
            if t.minute > c.minute:
            # Set next tide details here
                next_tide = tidetype
                next_tidetime = tidetime
                # Set the last tide
                lastTide(tides[tideindex - 1])
                break

    if next_tide == "":
        next_tide = "no futher tides today"
        lastTide(tides[tideindex - 1])
    if last_tidetime == "":
        if next_tide == "high":
            last_tide = "low"
            lastTide(tides[tideindex - 1])
        else:
            last_tide = "high"
            lastTide(tides[tideindex - 1])


    # Get next high tide
    for tide in tides:
        t = tide.split('#',1)
        tidetime = t[0]
        tidetype = t[1]
        t = datetime.strptime(tidetime, '%H:%M')
        c = datetime.strptime(currenttime, '%H:%M')
        if t.hour > c.hour:
            if tidetype == "high":
                next_hightidetime = convert12H(tidetime)
        if t.hour == c.hour:
            if t.minute > c.minute:
                next_hightidetime = convert12H(tidetime)

    # No high tide found so populate variable with last high tide
    if next_hightidetime == "":
        hightides = 1
        if "high" in tides[tideslen-1]:
            next_hightidetime = tides[tideslen-1]
            next_hightidetime = next_hightidetime.split('#',1)
            next_hightidetime = "high tide was at " + convert12H(next_hightidetime[0])
        if "high" in tides[tideslen-2]:
            next_hightidetime = tides[tideslen-2]
            next_hightidetime = next_hightidetime.split('#',1)
            next_hightidetime = "high tide was at " + convert12H(next_hightidetime[0])


    # get next low tide
    for tide in tides:
        t = tide.split('#',1)
        tidetime = t[0]
        tidetype = t[1]
        t = datetime.strptime(tidetime, '%H:%M')
        c = datetime.strptime(currenttime, '%H:%M')
        if t.hour > c.hour:
            if tidetype == "low":
                next_lowtidetime = convert12H(tidetime)
        if t.hour == c.hour:
            if t.minute > c.minute:
                next_lowtidetime = convert12H(tidetime)

    # No low tide found so populate variable with last low tide
    if next_lowtidetime == "":
        lowtides = 1
        if "low" in tides[tideslen - 1]:
            next_lowtidetime = tides[tideslen - 1]
            next_lowtidetime = next_lowtidetime.split('#', 1)
            next_lowtidetime = "low tide was at " + convert12H(next_lowtidetime[0])
        if "low" in tides[tideslen - 2]:
            next_lowtidetime = tides[tideslen - 2]
            next_lowtidetime = next_lowtidetime.split('#', 1)
            next_lowtidetime = "low tide was at " + convert12H(next_lowtidetime[0])

    # Get current state
    if last_tide == "high":
        if hightides > 0:
            if lowtides == 0:
                tide_state = "the tide is currently on the way out, ....  and will reach low tide by " + next_lowtidetime
            else:
                tide_state = "the tide is currently on the way out, ....  and will reach low tide by tomorrow"
        else:
            tide_state = "the tide is currently on the way out, ....  and will reach low tide by " + next_lowtidetime  # convert12H(next_lowtidetime)
    if last_tide == "low":
        if lowtides > 0:
            if hightides == 0:
                tide_state = "the tide is currently on the way in, ....  and will reach high tide by " + next_hightidetime
            else:
                tide_state = "the tide is currently on the way in, ....  and will reach high tide by tomorrow"
        else:
            tide_state = "the tide is currently on the way in, ....  and will reach high tide by " + next_hightidetime  # convert12H(next_hightidetime)

    print("Next tide time = ", next_tidetime)
    print("Next tide = ", next_tide)
    print("last tide = ", last_tide)
    print("Last tide time = ", last_tidetime)
    print("Next high tide time  = ", next_hightidetime)
    print("Next low tide time  = ", next_lowtidetime)
    print("Current state  = ", tide_state)


app = Flask(__name__)
ask = Ask(app, "/tides")


@app.route('/', methods=['GET', 'POST'])
def homepage():
    return "hi there, how ya doin?"


@ask.launch
def start_skill():
    parseTides()
    welcome_message = 'Hello, please invoke me by saying alexa ... ask the river .. when is high tide,  or when is low tide, you can even just ask what its doing, to know the details of the current tide'
    return statement(welcome_message)

@ask.intent("TideIntent", mapping={'tide': 'TideState'})
def announceTides(tide):
    parseTides()
    global next_hightidetime
    global next_lowtidetime
    global hightides
    global lowtides
    if tide == "high":
        if hightides == 1:
            tideinfo = next_hightidetime
        else:
            tideinfo = "Today's high tide is at " + next_hightidetime

    if tide == "low":
        if lowtides == 1:
            tideinfo = next_lowtidetime
        else:
            tideinfo = "Today's low tide is at " + next_lowtidetime
    return statement('{}'.format(tideinfo))

@ask.intent("CurrentState")
def CurrentState():
    parseTides()
    global tide_state
    return statement('{}'.format(tide_state))

if __name__ == '__main__':
    app.run(host='0.0.0.0')

