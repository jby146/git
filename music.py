# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxp-501387243681-505536827893-507363596580-dbbafa48fcdb47ecd5a121e4b4c142a1"
slack_client_id = "501387243681.508932832070"
slack_client_secret = "9ca967b0b6c86287aeb570e77f8b5b50"
slack_verification = "E04YYc6PS8RaIGIH0Hf51iMG"
sc = SlackClient(slack_token)

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    
    #여기에 함수를 구현해봅시다.
    url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    ranks= soup.find("tbody").find_all("strong")
    titles= soup.find("tbody").find_all("p",class_="title")
    artists= soup.find("tbody").find_all("p",class_="artist")
    
    title_list = []
    rank_list = []
    artist_list = []
    return_list = []
    for i, title in enumerate(titles):
        if i < 10:
            title_list.append(title.get_text().replace('\n',''))
           
            
    for i, artist in enumerate(artists):
        if i < 10:
            artist_list.append(artist.get_text().replace('\n',''))
           
    for i, rank in enumerate(ranks):
        if i < 10:
            rank_list.append(rank.get_text().replace('\n',''))
             

    for i in range(0,10):
        return_list.append(str(rank_list[i])+"위: "+str(title_list[i])+"/"+str(artist_list[i]))

   # for k in range(10):
        
    #    keywords.append(k+1+" : "+soup.find("tbody").find_all("p",class_="title").get_text()+"/"+soup.find("tbody").find_all("p",class_="artist").get_text())  
        
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(return_list)

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
