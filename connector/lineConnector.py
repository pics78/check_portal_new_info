from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage
from env.envMgr import getEnv
from env.envKeyDef import Portal, Line

loginUrl = getEnv(Portal.URL) + getEnv(Portal.LOGINPATH)
# LINE info
channelAccessToken = getEnv(Line.TOKEN)
lineUserId         = getEnv(Line.USR)

def sendPortalNewInfo(info):
    try:
        formatedInfo = '・' + '\n・'.join(info)
        text = f'【ポータル新着お知らせ】\n{formatedInfo}\n\nログインはこちら\n{loginUrl}'
        LineBotApi(channelAccessToken).push_message(lineUserId, TextSendMessage(text=text))
    except LineBotApiError as e:
        print("ERROR: Sending message to LINE failed.")
        print(e)
        return 1
    return 0