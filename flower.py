# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
app = Flask(__name__)
slack_token = "xoxp-501387243681-504600309376-508585041463-44c8b209fd060d757cf4fad36803916d"
slack_client_id = "501387243681.508584219431"
slack_client_secret = "097218fa2967fe7c9f889ab83dc636e1"
slack_verification = "kwVckxE3A9V91jYWV7JlhvEv"
sc = SlackClient(slack_token)
# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    if len(text)>20 :
        tmp=[]
        tmp=text.split(' ')
        month=tmp[2]
        day=tmp[3]
        url = "http://garden.sc.go.kr/?r=home&c=1118%2F1188%2F1208&m=bbs&bid=flower&cat=&sort=gid&orderby=asc&recnum=20&type=review&iframe=&skin=&month="+month+"&today="+day
        req = urllib.request.Request(url)
    
        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")
    
    
        keywords=[]
        content=[]
        flower=[]
        allst=[]
    
        if "탄생화" in text:
            for data in soup.find_all("div",{"class": "flow_title"}):
                if not data.get_text() in flower:
                    if len(flower)>= 10:
                        break
                    data.get_text().replace("\n",'')
                    flower=data.get_text()
                    allst.append(flower)
            for data in soup.find_all("div",{"class": "story"}):
                if not data.get_text() in content:
                    if len(content)>= 10:
                        break
                    data.get_text().replace("\n",'')
                    content=data.get_text().strip()
                    allst.append(content)
        keywords=allst[0]+"\n"+allst[1]
        print(keywords)
        
    elif len(text)<13:
        keywords="**입력방법**\n 탄생화 00(month) 00(day) : 해당 날짜의 탄생화, 꽃말, 꽃 이야기\n 꽃이름 : 꽃말, 이미지\n"
        
    else :
        url='https://namu.wiki/w/%EA%BD%83%EB%A7%90'
    
        
        cont =""
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        sourcecode = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(sourcecode, "html.parser")
    # 전체 태그에 대해 title이 범죄도시인 태그를 찾는다.
    #find(attrs={'title': '가막살나무'})
   #tag = soup.find('ul',class_="wiki-list").find_all('li')
        tag = soup.find_all('div', class_="wiki-heading-content")
        tag1 = tag[3].find
        p1 = soup.find_all('ul',class_="wiki-list")
        flower_list = []
        flower_w = []
        for i, p11 in enumerate(p1):
            for k in p1[i] :
                cont += k.get_text()+"/////"
    #print(cont)
        flower_list = cont.split('/////')
    
        for i in flower_list:
        #i=urllib.parse.quote_plus(i)
            flower_w.append(i.split('-'))
    #print(flower_w)
        keywords=[]
        tmp=[]
        tmp=text.split(' ')
        word=tmp[1]
        
    #word=urllib.parse.quote_plus(word)
        for n in flower_w :
            if word in n[0]:
                
                flowername=urllib.parse.quote_plus(word)
                tmpurl='https://search.naver.com/search.naver?where=image&sm=tab_jum&query='+flowername
                tmpurl2 = urllib.request.Request(tmpurl, headers={'User-Agent': 'Mozilla/5.0'})
                sourcecode1 = urllib.request.urlopen(tmpurl2).read()
                text = sourcecode1.decode('utf-8')
                soup = BeautifulSoup(sourcecode1, "html.parser")
                
                eee=soup.find("div", class_="img_area _item")
                ddd=eee.find("img")
                
                
                #print(ddd.get('data-source'))
                keywords=str(n[0])+"의 꽃말 : "+str(n[1])+"\n"+ddd.get('data-source')
                #image_url = ddd.get('data-source')
                #attachments = [{"title": "flower", "image_url": image_url}]
                #sc.api_call("chat.postMessage", channel='D0K7P9MCJ', text='postMessage test',attachments=attachments)
                
                break
                
        
        
        
            
        
  # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return keywords
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