import housey_logging
housey_logging.configure()

import requests
import time
import math
import sys
import config_loader
import logging
import requests_error_handler

#variables

config = config_loader.load_config()

init_error_handler = requests_error_handler.init_error_handler
handle_response_not_ok = requests_error_handler.handle_response_not_ok
handle_request_exception = requests_error_handler.handle_request_exception
raise_no_more_tries_exception = requests_error_handler.raise_no_more_tries_exception

list_of_posted_videos= []

def get_livestreams_from_youtube(channel: str) -> dict:

    logging.info("polling channel %s", channel)

    error_retry_timeout, max_errors_allowed, error_count = init_error_handler()

    while error_count < max_errors_allowed:

        try:
            youtube_response = requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=' + channel, '&eventType=live&type=video&key=' + config.youtube_api_key)
            logging.info("youtube_requested information for channel %s with response: %s",channel ,youtube_response)

            if youtube_response.ok:
                return(youtube_response)
            
            else:
                error_count, remaining_errors = handle_response_not_ok(error_count)
                logging.error("tried to get livestreams from youtube with response %s trying %s more times and waiting for %s seconds",youtube_response ,remaining_errors, error_retry_timeout)
                
                if not error_count == max_errors_allowed:
                    time.sleep(error_retry_timeout)

        except Exception as e:
            error_count, remaining_errors = handle_request_exception(error_count)
            logging.error("unable to request live streams from youtube with exception %s trying %s more times and waiting %s seconds",e ,remaining_errors, error_retry_timeout)
            
            if not error_count == max_errors_allowed:
                time.sleep(error_retry_timeout)

    if error_count == max_errors_allowed:
        raise_no_more_tries_exception(max_errors_allowed)

def check_if_livestream_to_post(livestream_data: dict) -> str:
    parsed_livestream_data = livestream_data.json()

    try:
        item_count = len(parsed_livestream_data["items"])

    except:
        item_count = 0

    if item_count > 0:

        for item in parsed_livestream_data["items"]: 

            video_title = item["snippet"]["title"].lower()

            # checks if videos found contain keywords and do not contain ignored words
            if any(word in video_title for word in config.word_list) and all(word not in video_title for word in config.ignore_list):
                video_id_to_send = item["id"]["videoId"]

                if video_id_to_send not in list_of_posted_videos:
                    list_of_posted_videos.append(video_id_to_send)
                    logging.info("found video matching criteria with id: %s", video_id_to_send)

                    send_video_to_discord(video_id_to_send)
                    
            else:
                logging.info("Live video found but it did not match the criteria")

def send_video_to_discord(video_id: str):

    error_retry_timeout, max_errors_allowed, error_count = init_error_handler()

    while error_count < max_errors_allowed:

        try:

            discord_webhook_response = requests.post(config.discord_webhook_url, data={"content": config.notification_message + "https://www.youtube.com/watch?v=" + video_id,})

            if discord_webhook_response.ok:
                logging.info("posted video to discord with id: %s with response: %s",video_id ,discord_webhook_response)
                break
            
            else:
                error_count, remaining_errors = handle_response_not_ok(error_count)
                logging.error("tried to posting video to discord with response %s trying %s more times and waiting for %s seconds",discord_webhook_response ,remaining_errors, error_retry_timeout)
                
                if not error_count == max_errors_allowed:
                    time.sleep(error_retry_timeout)

        except Exception as e:
            error_count, remaining_errors = handle_request_exception(error_count)
            logging.error("unable to post video to discord with exception %s trying %s more times and waiting %s seconds",e ,remaining_errors, error_retry_timeout)
            
            if not error_count == max_errors_allowed:
                time.sleep(error_retry_timeout)

    if error_count == max_errors_allowed:
        raise_no_more_tries_exception(max_errors_allowed)

def main():

    # logic to log exceptions to file
    sys.excepthook = housey_logging.log_exception

    while True:

        # calculates minimum time between api calls to avoid rate limiting
        time_between_poll = math.ceil(1440 * len(config.channels) / 100)
        time_between_poll_minutes = time_between_poll * 60
        logging.info("calculated time between polls is %s minutes", time_between_poll_minutes)

        # loop checks all config.channels in config and searches for video titles matching defined keywords in config
        for channel in config.channels: 

            youtube_response = get_livestreams_from_youtube(channel)
            check_if_livestream_to_post(youtube_response)

        logging.info("waiting for %s minutes",str(time_between_poll_minutes))
        time.sleep(time_between_poll_minutes)

if __name__ == "__main__":
    main()