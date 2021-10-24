from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import (TextSendMessage, TemplateSendMessage, FlexSendMessage,
    CarouselTemplate, CarouselContainer, CarouselColumn, URIAction)
from env.envMgr import getEnv
from env.envKeyDef import Line

# LINE info
channelAccessToken = getEnv(Line.TOKEN)
lineAdminId = getEnv(Line.ADMIN)

def sendToAdmin(text):
    try:
        LineBotApi(channelAccessToken).push_message(
            to=lineAdminId,
            messages=TextSendMessage(text=text))
    except LineBotApiError as e:
        print('ERROR: Sending message to admin failed.')
        print(e)

def send(messages):
    try:
        LineBotApi(channelAccessToken).broadcast(messages=messages)
    except LineBotApiError as e:
        errMsg = 'ERROR: Sending message to LINE failed.'
        sendToAdmin(errMsg)
        print(errMsg)
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