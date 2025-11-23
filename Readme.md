# important
i have completely refactored the script and a lot has changed, if you ran this script previously please start from scratch and rebuild your config as described below

# What it does
This is a script i wrote so i can get notifications if certain channels go live on youtube, it check their live videos to a list of keywords and if it contains said keyword it posts a link to the video to a discord webhook. it automaticly calculates the time between polls to avoid getting rate limited. however the youtube api is very restrictive on quota's and at most you can poll every 15 minutes if you only check 1 channel

![Alt text](screenshot.png)


# how to use
1. install python on your system from the python website https://www.python.org/downloads/ if you plan on using the included batch files make sure to select ```intall to path``` during the installation
2. install the needed libraries with pip ```pip install requests``` and ```pip install pyyaml```
3. you will need a youtube data api key for the data api v3, you can get one on https://console.cloud.google.com/ it can be difficult to find the right menu's if your new to this. refer to a quick google search on how to
4. go to the config folder and copy the ```example_config.yaml``` and rename it to ```config.yaml```.
5. adjust the appropriate config for your version   
* you will need the actual channelID of the channel you want to monitor, not a handle like @youtube, plenty of tools out there that do it for you, just google ```youtube channel id finder```

```
"youtube_api_key": YOUR_YOUTUBE_API_KEY
"discord_webhook_url": YOUR_DISCORD_WEBHOOK_URL
"word_list": # list of words you want the bot to post if they are in the title of the video
- space
- cool
"ignore_list": # list of words you want the bot to not post if they are in the title of the video
- high
- low
"notification_message": YOUR_DISCORD_NOTIFICATION_MESSAGE
"channels": # list of youtube channel id's to check for livestreams
- UCLA_DiR1FfKNvjuUpBHmylQ
```

6. launch the script
on windows: with the included batch file
on linux: in a terminal with ```python src/youtube_live.py```

Optionally a dockerfile is included wich can be used to build a docker image or use the one on my repository with the following code

```
docker run -dit --name youtubelivebot -v /path/to/config:/usr/src/app/config keyboardmedic/youtubelivebot:latest
```

# disclaimer
Scripts are written by an amateur, use at your own risk

the only vibe used in this code is background drum and bass
    