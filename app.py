import requests
from bs4 import BeautifulSoup
import datetime

from lineConnector import sendPortalNewInfo
from dynamodbConnector import (
    getLastNewsTitle, updateLastNewsTitle
)
from portalEnv import (
    userId, passwd, portal, loginPath, inputParamName1, inputParamName2
)

def lambda_handler(event, context):
    ses = requests.session()

    resForLogin = ses.request('GET', portal + loginPath)
    soupForLogin = BeautifulSoup(resForLogin.text, 'html.parser')
    inputParam1 = soupForLogin.find('input', attrs={'name': inputParamName1}).get('value')
    inputParam2 = soupForLogin.find('input', attrs={'name': inputParamName2}).get('value')

    payload = {
        '__pjax': 'true',
        'UserID': userId,
        'Password': passwd,
        'BirthDay': '1111/11/11',
        inputParamName1: inputParam1,
        inputParamName2: inputParam2
    }

    resForHome = ses.request('POST', portal + loginPath, data=payload)
    soupForHome = BeautifulSoup(resForHome.text, 'html.parser')
    infoList = soupForHome.select('#innercontent > div:nth-child(4) > div.groupcontent > ul > li')

    now = datetime.datetime.now().strftime('%Y.%m.%d')
    newInfo = []
    lastTitle = getLastNewsTitle()
    for info in infoList:
        updateDate = info.select_one('span:nth-child(1) > span[class="spacing"]').text
        title = info.find('a').text
        if now == updateDate and lastTitle != title:
            newInfo.append(title)
        else:
            break

    if len(newInfo) > 0:
        updateLastNewsTitle(newInfo[0])
        sendPortalNewInfo(newInfo)

    return {
        'statusCode': 200
    }