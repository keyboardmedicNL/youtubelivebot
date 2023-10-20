# imports needed libraries for code
import requests
import time
import json
import math
import threading
from os.path import exists
from subprocess import call

#variables used in script
configfile=False
channelsfile=False
webservercheck=False
postcheck=False
l= []

# functions used in script

# formats embed for discord webhook and posts to url
def discord_embed(title,color,description):
    if webhooklogurl != "":
        data = {"embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(webhooklogurl, json=data)

#pulls data from config
while configfile == False: # loop to ensure config gets loaded, will retry if it fails
    try:
        with open("config/config.json") as config: # opens config and stores values in variables
            configJson = json.load(config)
            youtubeApiKey = configJson["youtubeApiKey"]
            webhookurl = configJson["webhookurl"]
            webhooklogurl = configJson["webhooklogurl"]
            webhookmonitorurl = configJson["webhookmonitorurl"]
            wordlist = configJson["wordlist"]
            notificationmessage = configJson["notificationmessage"]
            channels = configJson["channels"]
            config.close() # closes config
        configfile = True # stops loop when loaded succesfully
        print("<YOUTUBELIVEBOT> succesfully loaded config")
        discord_embed("Youtubelivebot",14081792,"succesfully loaded config")
    except Exception as e: 
        print(f"An exception occurred whilst trying to read the config: {str(e)} waiting for 1 minute")
        time.sleep(60)

#webserver for monitoring purposes
while webservercheck == False: # loop to ensure webserver gets loaded
    try:
        file_exists = exists("webserver.py")
        if file_exists == True: # check added so exception actually triggers
            def thread_second(): # start webserver.py as a second threat to allow it to run parallel with main script
                call(["python", "webserver.py"])
            processThread = threading.Thread(target=thread_second)
            processThread.start()
            webservercheck = True # stops loop if succesfull
            print("<YOUTUBELIVEBOT> starting webserver for local monitoring") 
            discord_embed("Youtubelivebot",14081792,"starting webserver for local monitoring")
    except Exception as e: 
        print(f"An exception occurred whilst trying to start the webserver: {str(e)} waiting for 1 minute")
        discord_embed("MonitorBotsBot",10159108,f"An exception occurred whilst trying to start the webserver: {str(e)} waiting for 1 minute")
        time.sleep(60)

#post process to talk to remote monitor
while postcheck == False: # loop to ensure post gets loaded
    try:
        file_exists = exists("post.py")
        if file_exists == True: # check added so exception actually triggers
            if webhookmonitorurl != "":
                def thread_third(): # start post.py as a third threat to allow it to run parallel with main script
                    call(["python", "post.py"])
                processThread = threading.Thread(target=thread_third)
                processThread.start()
                postcheck = True # stops loop if succesfull
                print("<YOUTUBELIVEBOT> starting post server for remote monitoring")
                discord_embed("Youtubelivebot",14081792,"starting post server for remote monitoring")
            else:
                postcheck = True # stops loop if succesfull
    except Exception as e: # catches exception
        print(f"An exception occurred whilst trying to start the post server: {str(e)} waiting for 1 minute")
        discord_embed("MonitorBotsBot",10159108,f"An exception occurred whilst trying to start the post server: {str(e)} waiting for 1 minute")
        time.sleep(60)

# checks if name of video contains pursuit and if so posts video to webhook
while True: 
    try:
        # calculates minimum time between api calls to avoid rate limiting
        channelCount= 0 
        for channel in channels: 
            channelCount= channelCount + 1
        timeToPoll= 1440 / channelCount / 100 
        timeToPoll= math.ceil(timeToPoll)
        timeToSleep = timeToPoll * 60
        print(f"<YOUTUBELIVEBOT> time between polls is {str(timeToPoll)} minutes")
        discord_embed("Youtubelivebot",14081792,f"time between polls is {str(timeToPoll)} minutes")
        for channel in channels: # loop checks all channels in config and searches for video titles matching defined keywords in config
            print(f"<YOUTUBELIVEBOT> polling channel {channel}")
            discord_embed("Youtubelivebot",14081792,f"polling channel {channel}")
            r = requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=' + channel, '&eventType=live&type=video&key=' + youtubeApiKey)
            request = r
            print(f"<YOUTUBELIVEBOT> request response is {str(request)}")
            discord_embed("Youtubelivebot",14081792,f"request response is {str(request)}")
            if "200" in str(request): # checks if get request was succesfull
                jstring = request.json()
                itemCount= 0
                for item in jstring["items"]:
                    itemCount = itemCount + 1
                if itemCount > 0:
                    for item in jstring["items"]: 
            # checks if videos found contain keywords
                        if any(s in (item["snippet"]["title"].lower()) for s in wordlist): # check video titles against keyword list
                            videoIdToSent = item["id"]["videoId"]
                            if videoIdToSent not in l:
                                l.append(videoIdToSent)
                                print(f"<YOUTUBELIVEBOT> posting video with id: {videoIdToSent}")
                                discord_embed("Youtubelivebot",703235,f"posting video with id: {videoIdToSent}")
                                r = requests.post(webhookurl, data={"content": notificationmessage + "https://www.youtube.com/watch?v=" + videoIdToSent,}) # post to main webhook
                        else:
                            print(f"<YOUTUBELIVEBOT> Live video found but no pursuit on channel {channel}")
                            discord_embed("Youtubelivebot",14081792,f"Live video found but no pursuit on channel {channel}")
                else:
                    print(f"<YOUTUBELIVEBOT> no live videos found for channel {channel}")
                    discord_embed("Youtubelivebot",14081792,f"no live videos found for channel {channel}")
        print(f"<YOUTUBELIVEBOT> waiting for {str(timeToPoll)} minutes")
        discord_embed("Youtubelivebot",14081792,f"waiting for {str(timeToPoll)} minutes")
        time.sleep(timeToSleep)
    except Exception as e: # catches exception
        print(f"An exception occurred in main loop: {str(e)} waiting for 1 minute")
        discord_embed("MonitorBotsBot",10159108,f"An exception occurred in main loop: {str(e)} waiting for 1 minute")
        time.sleep(60)