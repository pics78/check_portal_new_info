from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import (TextSendMessage, TemplateSendMessage,
    CarouselTemplate, CarouselColumn, URIAction)
from env.envMgr import getEnv
from env.envKeyDef import Line

# LINE info
channelAccessToken = getEnv(Line.TOKEN)
lineUserId         = getEnv(Line.USR)

def send(message):
    try:
        LineBotApi(channelAccessToken).push_message(lineUserId, message)
    except LineBotApiError as e:
        print("ERROR: Sending message to LINE failed.")
        print(e)

def sendPortalNewInfo(contents):
    text = f'【ポータル新着お知らせ】\n\n{contents}'
    send(TextSendMessage(text=text))

def sendCarousel(columns):
    send(TemplateSendMessage(
        alt_text='Carousel',
        template=CarouselTemplate(columns=columns)))

def getCarouselColumn(fileName, uri):
    return CarouselColumn(
        title =  '添付ファイル',
        text = fileName,
        actions = [
            URIAction(
                label = 'ダウンロード',
                uri = uri
            )
        ]
    )