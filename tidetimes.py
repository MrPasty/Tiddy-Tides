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


def convert12H(time24):
    time12 = datetime.strptime(time24, "%H:%M")
    time12 = time12.strftime("%I:%M %p")
    return time12


def parseTides(action):
    # Set variables
    time12h = time.strftime("%I:%M %p")
    time24h = time.strptime(time12h, '%I:%M %p')
    currenttime = time.strftime('%H:%M', time24h)  
    end_ofday = 0
    next_tidetime = ""
    next_tidetype = ""
    next_tide_msg = ""
    current_tidetype = ""
    current_tidetime = ""
    current_tide_msg = ""
    next_hightidetime = ""
    next_lowtidetime = ""
    next_hightide_msg = ""
    next_lowtide_msg = ""

    # Get latest tide times from web
    tides = []

    # Read tide times in to variables to use later - note can pass a date on end of url like ..tide-times-20170918
    soup = BeautifulSoup(urllib.request.urlopen('https://www.tidetimes.org.uk/<YOUR RIVER>').read(), 'html5lib')
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

    tideslen = len(tides)


    # Get current and next tides
    for tide in tides:
        tideindex = tides.index(tide)
        t = tide.split('#', 1)
        tidetime = t[0]
        tidetype = t[1]
        t = datetime.strptime(tidetime, '%H:%M')
        c = datetime.strptime(currenttime, '%H:%M')
        if t > c:
            msg = "The next tide is "
            next_tidetime = tidetime
            next_tidetype = tidetype
            next_tide_msg = msg + next_tidetype + " at " + next_tidetime
            if next_tidetype == "high":
                next_hightidetime = next_tidetime
                next_hightide_msg = "High tide is at " + convert12H(next_hightidetime)
            else:
                next_lowtidetime = next_tidetime
                next_hightide_msg = "Low tide is at " + convert12H(next_lowtidetime)

            # get current tide
            if tideindex > 1:
                ct = tides[tideindex - 1]
                ct = ct.split('#', 1)
                current_tidetime = ct[0]
                current_tidetype = ct[1]
                if current_tidetype == "low":
                    current_tide_msg = current_tidetype + " tide was at " + convert12H(current_tidetime) + " so the tide is on the way in and will reach high tide by " + convert12H(next_tidetime)
                else:
                    current_tide_msg = current_tidetype + " tide was at " + convert12H(current_tidetime) + " so the tide is on the way out and will reach low tide by " + convert12H(next_tidetime)
            else:
                # we have to go by state of current tide to work out last one, no time available
                if next_tidetype == "low":
                    current_tidetype = "high"
                    current_tidetime = ""
                    msg = "the last tide was high so it is now on the way out and will reach low tide by " + convert12H(next_tidetime)
                else:
                    current_tidetype = "low"
                    current_tidetime = ""
                    msg = "the last tide was low so it is now on the way in and will reach high tide by " + convert12H(next_tidetime)
                current_tide_msg = msg
            break

    # Check we have values for next low and high tide
    if next_lowtidetime == "":
        next_lowtide_msg = "There are no further low tides today, " + current_tide_msg
    if next_hightidetime == "":
        next_hightide_msg = "There are no further high tides today, " + current_tide_msg

    # no more tides today so populate variables accordingly
    if next_tidetime == "":
        end_ofday = 1

    if end_ofday == 1:
        msg = "There are no further tides today however the tide was "
        lt = tides[tideslen - 1]
        lt = lt.split('#', 1)
        last_tidetime = lt[0]
        last_tidetype = lt[1]
        if last_tidetype == "high":
            next_tide_msg = msg + last_tidetype + " at " + convert12H(last_tidetime) + " so it is now on the way out"
        else:
            next_tide_msg = msg + last_tidetype + " at " + convert12H(last_tidetime) + " so it is now on the way in"

    # Return the relevant details requested by calling function
    if action == "next":
        return next_tide_msg

    if action == "status":
        return current_tide_msg

    if action == "high":
        return next_hightide_msg

    if action == "low":
        return next_lowtide_msg


# END OF CODE!

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
        action = "high"
        tideinfo = parseTides(action)

    if tide == "low":
        action = "low"
        tideinfo = parseTides(action)
    return statement('{}'.format(tideinfo))

@ask.intent("CurrentState")
def CurrentState():
    action = "state"
    tideinfo = parseTides(action)
    return statement('{}'.format(tideinfo))

if __name__ == '__main__':
    app.run(host='0.0.0.0')

