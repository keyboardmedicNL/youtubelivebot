# What it does
This is a script i wrote so i can get notifications if certain channels go live on youtube, it check their live videos to a list of keywords and if it contains said keyword it posts a link to the video to a discord webhook. it automaticly calculates the time between polls to avoid getting rate limited. however the youtube api is very restrictive on quota's and at most you can poll every 15 minutes if you only check 1 channel

included are:
- a post script that sends a http post to a watchdog server of your choosing, wich wont happen if the url is left blank in the config
- a http webserver running to use for uptime monitoring by having an approachable url wich can be checked with something like uptime kuma


# how to use
1. place all contents in a folder and make a "config" folder.
2. make a config.json and copy the text below into the file 
```
{
    "youtubeApiKey": "youtubedataAPIkey",
    "webhookurl": "URL where the notification gets posted to",
    "webhooklogurl": "optional URL to log output to a discord webhook",
    "webhookmonitorurl": "optional URL to send simple post requests to a watchdog server in format {"name":"botname":"time":"UNIX timestamp"}",
    "botname": "name to send to watchdog server OPTIONAL",
    "posttimeout": "time between posts to watchdog OPTIONAL",
    "wordlist": ["example1","example2","example3"],
    "notificationmessage": "Example message to post to discord",
    "channels": ["YoutubechannelID1","YoutubechannelID2"],
    "hostname": "Adress for simple webserver",
    "webport": "port for simple webserver"
}
```
3. save the file and launch the script youtubelivebot.py

*you will need the actual channelID of the channel you want to monitor, not a handle like @youtube

Optionally a dockerfile is included wich can be used to build a docker image or use the one on my repository with the following code

```
docker run -dit --name youtubelivebot -v /path/to/config:/usr/src/app/config -p <port for webserver>:<port defined in config> keyboardmedic/youtubelivebot:latest
```
    