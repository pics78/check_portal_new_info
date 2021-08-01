import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from portalEnv import portal, loginPath

# LINE bot info
channelAccessToken = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
lineUserId         = os.environ['LINE_USER_ID']

def sendPortalNewInfo(info):
    try:
        formatedInfo = '・' + '\n・'.join(info)
        loginUrl = portal + loginPath
        text = f'【ポータル新着お知らせ】\n{formatedInfo}\n\nログインはこちら\n{loginUrl}'
        LineBotApi(channelAccessToken).push_message(lineUserId, TextSendMessage(text=text))
    except LineBotApiError as e:
        print("ERROR: Sending message to LINE failed.")
        print(e)
        return 1
    return 0