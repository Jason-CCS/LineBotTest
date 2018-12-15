import requests 
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('bmOpRF6paRIURucgqrm6TeWoWQH43m1kdI6zFXMYvgW4uVEaBE2pIkFdqeiDsVM4zH0jlyEMCXVuLoDv6mRZ3/PfZTN8RIMdK07p7chViDfBC1OKjV0L8kgWVFhu1fkHmdh5WsRBf89TBgOxbuYe2QdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('ad05913ee0319c600ebdb3c9882d79f4')
# heroku logs --tail --app timothyslinebot


def movie():
    target_url = 'https://movies.yahoo.com.tw/'
    res = requests.get(target_url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')   
    content = ""
    for index, data in enumerate(soup.select('div.movielist_info h2 a')):
        if index == 5:
            return content
        title = data.text
        link = data['href']
        content += '\n{}\n{}\n'.format(title, link)
    return content

# def movie():
#     r = requests.get('https://tw.yahoo.com/')
#     content = ""
#     # 確認是否下載成功
#     if r.status_code == requests.codes.ok:
#     # 以 BeautifulSoup 解析 HTML 程式碼
#         soup = BeautifulSoup(r.text, 'html.parser')

#     # 以 CSS 的 class 抓出各類頭條新聞
#     stories = soup.find_all('a', class_='story-title')
#     for s in stories:
#         title = s.text
#         link = s.get('href')
#         # 新聞標題
#         content += '{}\n{}\n'.format(title, link)
#     return content

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'



# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'hi':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = 'helasdslo'))
    elif event.message.text == 'movie':
        a = movie()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = a))
    elif event.message.text == "videos":
        line_bot_api.reply_message(event.reply_token,VideoSendMessage(original_content_url='https://www.youtube.com/watch?v=1tK95WZt5ug', preview_image_url='https://www.youtube.com/watch?v=1tK95WZt5ug'))
    elif event.message.text == "emoji":
        line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=1, sticker_id=2))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)