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

#pulls data from config
with open("config/config.json") as config:
    config_json = json.load(config)
    youtube_api_key = config_json["youtube_api_key"]
    discord_webhook_url = config_json["discord_webhook_url"]
    word_list = config_json["word_list"]
    ignore_list = config_json["ignore_list"]
    notification_message = config_json["notification_message"]
    channels = config_json["channels"]
print("succesfully loaded config")

# checks if name of video contains pursuit and if so posts video to webhook
while True: 
    try:
        # calculates minimum time between api calls to avoid rate limiting
        time_to_poll= math.ceil(1440 * len(channels) / 100)
        time_to_sleep = time_to_poll * 60
        print(f"calculated time between polls is {str(time_to_poll)} minutes")
        # loop checks all channels in config and searches for video titles matching defined keywords in config
        for channel in channels: 
            print(f"polling channel {channel}")
            r = requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=' + channel, '&eventType=live&type=video&key=' + youtube_api_key)
            request = r
            print(f"requested information for channel {channel} with response: {str(request)}")
            # checks if get request was succesfull
            if "200" in str(request): 
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
                                r = requests.post(discord_webhook_url, data={"content": notification_message + "https://www.youtube.com/watch?v=" + video_id_to_send,})
                        else:
                            print(f"Live video found but it did not match the criteria for {channel}")
                else:
                    print(f"no live videos found for channel {channel}")
        print(f"waiting for {str(time_to_poll)} minutes")
        time.sleep(time_to_sleep)
    except Exception as e:
        print(f"An exception occurred in main loop: {str(e)} waiting for 1 minute")
        time.sleep(60)