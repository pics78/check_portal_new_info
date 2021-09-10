import requests
from bs4 import BeautifulSoup
import datetime

from connector import lineConnector, dynamodbConnector
from env.envMgr import getEnv
from env.envKeyDef import Portal, StatusForRunning

loginUrl        = getEnv(Portal.URL) + getEnv(Portal.LOGINPATH)
userId          = getEnv(Portal.USR)
passwd          = getEnv(Portal.PW)
inputParamName1 = getEnv(Portal.PARAMNAME1)
inputParamName2 = getEnv(Portal.PARAMNAME2)

# テスト実行用
isTest = True if getEnv(StatusForRunning.MODE) == StatusForRunning.IS_TEST.value else False

def lambda_handler(event, context):
    ses = requests.session()

    resForLogin = ses.request('GET', loginUrl)
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

    resForHome = ses.request('POST', loginUrl, data=payload)
    soupForHome = BeautifulSoup(resForHome.text, 'html.parser')
    groupList = soupForHome.select('#innercontent > div[class="group"]')
    # 4番目のgroupクラスdiv要素がお知らせボックス
    infoList = groupList[3].select('.groupcontent > ul > li')

    now = datetime.datetime.now().strftime('%Y.%m.%d')
    newInfo = []
    lastTitle = dynamodbConnector.getLastNewsTitle()
    for info in infoList:
        updateDate = info.select_one('span:nth-child(1) > span[class="spacing"]').text
        title = info.find('a').text
        if now == updateDate and lastTitle != title:
            newInfo.append(title)
        else:
            break

    if len(newInfo) > 0:
        if isTest:
            # テスト実行時はLINE送信とDB更新を行わずコンソール出力する
            print('TEST: LastNewsTitle = ', newInfo[0])
            print('TEST: newInfo: ', newInfo)
        else:
            dynamodbConnector.updateLastNewsTitle(newInfo[0])
            lineConnector.sendPortalNewInfo(newInfo)
    else:
        print('newInfo was none.')

    return {
        'statusCode': 200
    }