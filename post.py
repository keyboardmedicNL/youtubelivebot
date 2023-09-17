# imports needed libraries
import requests
import time
import json
from datetime import datetime, timezone, timedelta

# variables used in script
configcheck = False

# loads needed data from config to variables
while configcheck == False: # loop to ensure config gets loaded
    try:
        with open("config/config.json") as config: # opens config and stores data in variables
            configJson = json.load(config)
            webhookmonitorurl = configJson["webhookmonitorurl"]
            botname = configJson["botname"]
            timeout = 60*int(configJson["posttimeout"])
            config.close()
            configcheck = True # stops loop if succesfull
            print("<POST> Succesfully loaded config") # log message
    except Exception as e: # catches exception
        print("<POST> An exception occurred whilst trying to load the config:", str(e)) # log message
        print("<POST> trying again in 1 minute") # log message
        time.sleep(60)

# main loop
while True:
    currentTime = (datetime.now(timezone.utc))
    currentTime = currentTime.timestamp()
    myobj = {'name': botname, 'time': currentTime} # formats currenttime in unix timestamp and botname into correct json formatting
    try:
        x = requests.post( webhookmonitorurl, json = myobj) # sends post request
        print("<POST> webhook response is: " + x.text) # log message
    except Exception as e: # catches exception
        print("<POST> An exception occurred in main loop:", str(e)) # log message
    time.sleep(timeout)