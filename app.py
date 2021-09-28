import requests
from bs4 import BeautifulSoup
import datetime

from connector import lineConnector, awsConnector
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
    lastTitle = awsConnector.getLastNewsTitle()
    for info in infoList:
        # 締切間近の表示は日付に関わらず先頭にくるため飛ばす
        isNearDeadline = info.select_one('span:nth-child(3) > span[style="color: Red"]') != None
        if not isNearDeadline:
            updateDate = info.select_one('span:nth-child(1) > span[class="spacing"]').text
            anchor = info.find('a')
            if now == updateDate and lastTitle != anchor.text:
                newInfo.append(anchor)
            else:
                break
    
    if len(newInfo) > 0:
        if isTest:
            # テスト実行時はLINE送信とDB更新を行わずコンソール出力する
            print('TEST: LastNewsTitle = ', newInfo[0])
            print('TEST: newInfo: ', newInfo)
        else:
            infoCount = 1
            for info in newInfo:
                resForInfoDetail = ses.request('GET', getEnv(Portal.URL) + info.get('href'))
                soupForInfoDetail = BeautifulSoup(resForInfoDetail.text, 'html.parser')
                infoDetails = soupForInfoDetail.select('#innercontent > div[class="centerblock1"] > div[class="centerblock1content"] > table > tr')
                infoContentList = []
                fileList = []
                fileCount = 1
                for elem in infoDetails:
                    title = elem.select_one('td:nth-child(1)')
                    val = elem.select_one('td:nth-child(2)')
                    if val.text.strip('\n') != '':
                        fileName = val.text.strip('\n')
                        infoContentList.append(f'<{title.text}>')
                        infoContentList.append(fileName + '\n')
                        valChildAnchor = val.select_one('a[class="jsDownload"]')
                        if valChildAnchor != None:
                            hrefUrl = getEnv(Portal.URL) + valChildAnchor.get('href')
                            urlData = ses.request('GET', hrefUrl).content
                            uploadFileName = f'{updateDate}_{infoCount}_{fileCount}.pdf'
                            with open(uploadFileName ,mode='wb') as f:
                                f.write(urlData)
                            awsConnector.uploadFileToS3(uploadFileName)
                            fileUri = awsConnector.getFileUrl(uploadFileName)
                            fileList.append({
                                'fileName': fileName,
                                'uri': fileUri
                            })
                            fileCount += 1
                lineConnector.sendPortalNewInfo('\n'.join(infoContentList))
                lineConnector.sendCarousel(
                    list(map(lambda i: lineConnector.getCarouselColumn(i['fileName'], i['uri']), fileList)))
                infoCount += 1
            awsConnector.updateLastNewsTitle(newInfo[0].text)
    else:
        print('newInfo was none.')

    return {
        'statusCode': 200
    }