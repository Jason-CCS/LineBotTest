import requests
import sqlite3
from flask import Flask, request, abort
from flask import g

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

''' db start '''
DATABASE = "test.db"

def get_db():
    # 程式重新啟動的時候，_database這個參數一定是None的，所以要先建立跟test.db(sqlite的檔案，存在跟code同一個資料夾)的connection存到db變數之中
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
        
        # 這邊確認db當中的資料是否初始化
        c=db.cursor() # 啟動游標，我也不知道這三小，似乎select一定要用cursor obj
        # 查詢table 'roles' 是否存在
        table_name ="roles"
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", table_name)
        result=c.fetchone()

        app.logger.info(result) # print log
        exists = bool(result) 
        app.logger.info(exists) # print bool(result)

        if !exists:
            # 如果schema.sql還沒run，那當然查不到表，所以不存在就init db
            init_db(db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 初始化 database
def init_db(db):
    with app.app_context():
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def remove_db():
    if os.path.isfile(DATABASE):
        os.remove(DATABASE) 

''' db end '''

# Channel Access Token
line_bot_api = LineBotApi('FX6hoN+w4yCvk1rpcKAmOedQ2u+I3A6KxkFId/R2BKbGVIEF7gNwa2UjnHqxkhxaS+nEORS5HFcg/5U0O+OGWRvk6OiF7cAU5G4rfW2Cw/ga+aeG4E2PbzJhN2OecXZ1PMUQOLXZxOjCVRSYBcYNvQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('a0cc121b226498a53c403b267664faf6')
# heroku logs --tail --app timothyslinebot


def movie():
    print("in movie def")
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

def users():
    db=get_db()
    c=db.cursor()
    results = c.execute("SELECT * FROM users;")
    content = ""
    for r in results:
        content += 'id:{}, name:{}, 餘額:{}\n'.format(r[0], r[1], r[2])

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
        print("except")
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'hi':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = 'helasdslo'))
    elif event.message.text == 'movie':
        print("in movie")
        a = movie()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = a))
    elif event.message.text == "videos":
        line_bot_api.reply_message(event.reply_token,VideoSendMessage(original_content_url='https://www.youtube.com/watch?v=1tK95WZt5ug', preview_image_url='https://www.youtube.com/watch?v=1tK95WZt5ug'))
    elif event.message.text == "emoji":
        line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=1, sticker_id=2))
    elif event.message.text=='users':
        users()

    else:
        line_bot_api .reply_message(event.reply_token,TextSendMessage(text=event.message.text))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)