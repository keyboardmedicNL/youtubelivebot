# imports needed libraries for code
import requests
import time
import json
import math
import threading
from os.path import exists
from subprocess import call

#variables used in script
l= []

# functions used in script

# formats embed for discord webhook and posts to url
def discord_log(title,color,description,ping):
    if use_discord_logs.lower() == "true":
        if color == "blue":
            color = 1523940
        elif color == "yellow":
            color = 14081792
        elif color == "red":
            color = 10159108
        elif color == "green":
            color = 703235
        elif color == "purple":
            color = 10622948
        elif color == "gray" or color == "grey":
            color = 1776669
        if ping:
            ping_string = f"<@{ping_id}>"
        else:
            ping_string = ""
        data_for_log_hook = {"content": ping_string, "embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(discord_log_webhook, json=data_for_log_hook)
        if verbose:
            print(f"sending message to discord remote log webhook with title: {title} Color: {color} Description: {description} and ping: {ping_string}")
        time.sleep(1)

# gotify notification
def gotify(title,message,priority):
    if use_gotify.lower() == "true":
        gr = requests.post(gotifyurl, data={"title": title, "message": message, "priority":priority})
        if verbose >= 2:
            print(f"sending notification to gotify with title: {title} message: {message} priority: {priority}")
        time.sleep(1)

#pulls data from config
with open("config/config.json") as config:
    config_json = json.load(config)
    youtube_api_key = config_json["youtube_api_key"]
    discord_webhook_url = config_json["discord_webhook_url"]
    word_list = config_json["word_list"]
    ignore_list = config_json["ignore_list"]
    notification_message = config_json["notification_message"]
    channels = config_json["channels"]
    use_web_server = config_json["use_web_server"]
    use_remote_post = config_json["use_remote_post"]
    use_discord_logs = config_json["use_discord_logs"]
    use_gotify = config_json["use_gotify"]
    gotifyurl = config_json["gotifyurl"]
    ping_id = config_json["ping_id"]
    verbose = int(config_json["verbose"])
    if use_discord_logs.lower() == "true":
        discord_log_webhook = config_json["discord_remote_log_url"]
print("succesfully loaded config")
discord_log("Youtubelivebot","blue","succesfully loaded config",False)

#webserver for monitoring purposes
if use_web_server.lower() == "true":
    def thread_second():
        call(["python", "webserver.py"])
    process_thread = threading.Thread(target=thread_second)
    process_thread.start()
    print("starting webserver for local monitoring") 
    discord_log("Youtubelivebot","purple","starting webserver for local monitoring",False)

#post process to talk to remote monitor
if use_remote_post.lower() == "true":
    def thread_third():
        call(["python", "post.py"])
    process_thread = threading.Thread(target=thread_third)
    process_thread.start()
    print("starting post server for remote monitoring")
    discord_log("Youtubelivebot","purple","starting post server for remote monitoring",False)

# checks if name of video contains pursuit and if so posts video to webhook
while True: 
    try:
        # calculates minimum time between api calls to avoid rate limiting
        time_to_poll= math.ceil(1440 * len(channels) / 100)
        time_to_sleep = time_to_poll * 60
        print(f"calculated time between polls is {str(time_to_poll)} minutes")
        discord_log("Youtubelivebot","yellow",f"calculated time between polls is {str(time_to_poll)} minutes",False)
        # loop checks all channels in config and searches for video titles matching defined keywords in config
        for channel in channels: 
            print(f"polling channel {channel}")
            discord_log("Youtubelivebot","green",f"polling channel {channel}",False)
            r = requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=' + channel, '&eventType=live&type=video&key=' + youtube_api_key)
            request = r
            print(f"requested information for channel {channel} with response: {str(request)}")
            # checks if get request was succesfull
            if "200" in str(request): 
                discord_log("Youtubelivebot","green",f"requested information for channel {channel} with response: {str(request)}",False)
                yt_api_json = request.json()
                try:
                    item_count = len(yt_api_json["items"])
                except:
                    item_count = 0
                if item_count > 0:
                    for item in yt_api_json["items"]: 
                        # checks if videos found contain keywords and do not contain ignored words
                        if any(s in (item["snippet"]["title"].lower()) for s in word_list) and all(s not in (item["snippet"]["title"].lower()) for s in ignore_list):
                            video_id_to_send = item["id"]["videoId"]
                            if video_id_to_send not in l:
                                l.append(video_id_to_send)
                                print(f"found video matching criteria, posting video with id: {video_id_to_send}")
                                discord_log("Youtubelivebot","green",f"found video matching criteria, posting video with id: {video_id_to_send}",False)
                                r = requests.post(discord_webhook_url, data={"content": notification_message + "https://www.youtube.com/watch?v=" + video_id_to_send,})
                        else:
                            print(f"Live video found but it did not match the criteria for {channel}")
                            discord_log("Youtubelivebot","yellow",f"Live video found but none matching the criteria {channel}",False)
                else:
                    print(f"no live videos found for channel {channel}")
                    discord_log("Youtubelivebot","yellow",f"no live videos found for channel {channel}",False)
            else:
                discord_log("Youtubelivebot","red",f"requested information for channel {channel} with response: {str(request)}",True)
                gotify("Clipbot",f"requested information for channel {channel} with response: {str(request)}","5")
        print(f"main loop finished, waiting for {str(time_to_poll)} minutes")
        discord_log("Youtubelivebot","gray",f"main loop finished, waiting for {str(time_to_poll)} minutes",False)
        time.sleep(time_to_sleep)
    except Exception as e:
        print(f"An exception occurred in main loop: {str(e)} waiting for 1 minute")
        discord_log("youtubelivebot","red",f"An exception occurred in main loop: {str(e)} waiting for 1 minute",True)
        gotify("Clipbot",f"An exception occurred in main loop: {str(e)} waiting for 1 minute","5")
        time.sleep(60)