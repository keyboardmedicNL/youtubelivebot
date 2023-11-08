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
def discord_log(title,color,description):
    if use_discord_logs.lower() == "true":
        data = {"embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(discord_log_webhook, json=data)
        time.sleep(1)

#pulls data from config
with open("config/config.json") as config: # opens config and stores values in variables
    config_json = json.load(config)
    youtube_api_key = config_json["youtube_api_key"]
    discord_webhook_url = config_json["discord_webhook_url"]
    word_list = config_json["word_list"]
    notification_message = config_json["notification_message"]
    channels = config_json["channels"]
    use_web_server = config_json["use_web_server"]
    use_remote_post = config_json["use_remote_post"]
    use_discord_logs = config_json["use_discord_logs"]
    if use_discord_logs.lower() == "true":
        discord_log_webhook = config_json["discord_remote_log_url"]
print("succesfully loaded config")
discord_log("Youtubelivebot",14081792,"succesfully loaded config")

#webserver for monitoring purposes
if use_web_server.lower() == "true":
    def thread_second():
        call(["python", "webserver.py"])
    process_thread = threading.Thread(target=thread_second)
    process_thread.start()
    print("starting webserver for local monitoring") 
    discord_log("Youtubelivebot",14081792,"starting webserver for local monitoring")

#post process to talk to remote monitor
if use_remote_post.lower() == "true":
    def thread_third():
        call(["python", "post.py"])
    process_thread = threading.Thread(target=thread_third)
    process_thread.start()
    print("starting post server for remote monitoring")
    discord_log("Youtubelivebot",14081792,"starting post server for remote monitoring")

# checks if name of video contains pursuit and if so posts video to webhook
while True: 
    try:
        # calculates minimum time between api calls to avoid rate limiting
        channel_count= 0 
        for channel in channels: 
            channel_count= channel_count + 1
        time_to_poll= 1440 / channel_count / 100 
        time_to_poll= math.ceil(time_to_poll)
        time_to_sleep = time_to_poll * 60
        print(f"time between polls is {str(time_to_poll)} minutes")
        discord_log("Youtubelivebot",14081792,f"time between polls is {str(time_to_poll)} minutes")
        # loop checks all channels in config and searches for video titles matching defined keywords in config
        for channel in channels: 
            print(f"polling channel {channel}")
            discord_log("Youtubelivebot",14081792,f"polling channel {channel}")
            r = requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=' + channel, '&eventType=live&type=video&key=' + youtube_api_key)
            request = r
            print(f"request response is {str(request)}")
            discord_log("Youtubelivebot",14081792,f"request response is {str(request)}")
            # checks if get request was succesfull
            if "200" in str(request): 
                yt_api_json = request.json()
                item_count= 0
                for item in yt_api_json["items"]:
                    item_count = item_count + 1
                if item_count > 0:
                    for item in yt_api_json["items"]: 
            # checks if videos found contain keywords
                        if any(s in (item["snippet"]["title"].lower()) for s in word_list):
                            video_id_to_send = item["id"]["videoId"]
                            if video_id_to_send not in l:
                                l.append(video_id_to_send)
                                print(f"posting video with id: {video_id_to_send}")
                                discord_log("Youtubelivebot",703235,f"posting video with id: {video_id_to_send}")
                                r = requests.post(discord_webhook_url, data={"content": notification_message + "https://www.youtube.com/watch?v=" + video_id_to_send,})
                        else:
                            print(f"Live video found but no pursuit on channel {channel}")
                            discord_log("Youtubelivebot",14081792,f"Live video found but no pursuit on channel {channel}")
                else:
                    print(f"<YOUTUBELIVEBOT> no live videos found for channel {channel}")
                    discord_log("Youtubelivebot",14081792,f"no live videos found for channel {channel}")
        print(f"<YOUTUBELIVEBOT> waiting for {str(time_to_poll)} minutes")
        discord_log("Youtubelivebot",14081792,f"waiting for {str(time_to_poll)} minutes")
        time.sleep(time_to_sleep)
    except Exception as e: # catches exception
        print(f"An exception occurred in main loop: {str(e)} waiting for 1 minute")
        discord_log("youtubelivebot",10159108,f"An exception occurred in main loop: {str(e)} waiting for 1 minute")
        time.sleep(60)