import requests
from bs4 import BeautifulSoup
import datetime

from connector import lineConnector, awsConnector
from env.envMgr import getEnv
from env.envKeyDef import Portal, StatusForRunning
from utils.parseUtil import ParseUtil
from utils.msgUtil import LineMsgBuilder
from utils.resultUtil import Result

# テスト実行用
isTest = True if getEnv(StatusForRunning.MODE) == StatusForRunning.IS_TEST.value else False

def lambda_handler(event, context):
    parseUtil = ParseUtil(requests.session(), getEnv(Portal.URL))

    loginPath = getEnv(Portal.LOGINPATH)
    userId    = getEnv(Portal.USR)
    passwd    = getEnv(Portal.PW)
    prmName1  = getEnv(Portal.PARAMNAME1)
    prmName2  = getEnv(Portal.PARAMNAME2)

    loginSoup = parseUtil.getSoup('GET', loginPath)
    param1 = loginSoup.findInSoup('input', attrs={'name': getEnv(Portal.PARAMNAME1)}).get('value')
    param2 = loginSoup.findInSoup('input', attrs={'name': getEnv(Portal.PARAMNAME2)}).get('value')
    payload = {
        '__pjax'  : 'true',
        'UserID'  : userId,
        'Password': passwd,
        'BirthDay': '1111/11/11',
        prmName1  : param1,
        prmName2  : param2
    }
    # ログイン処理
    parseUtil.getSoup('POST', loginPath, data=payload)
    if parseUtil.soup == None:
        lineConnector.sendToAdmin('ERROR: Login failed.')
        return Result.InternalError

    groupList = parseUtil.selectInSoup('#innercontent > div[class="group"]')
    # 3番目のgroupクラスdiv要素がお知らせボックスだと想定
    infoGroup = groupList[2]
    groupHeader = infoGroup.select_one('.groupheader3')
    if groupHeader == None or groupHeader.text.strip() != getEnv(Portal.TARGET_GROUP_TITLE):
        lineConnector.sendToAdmin('ERROR: HTML structure is different from expected.')
        return Result.InternalError

    infoList = infoGroup.select('.groupcontent > ul > li')

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
                infoDetails = parseUtil.getSoup('GET', info.get('href')).selectInSoup(
                    '#innercontent > div[class="centerblock1"] > div[class="centerblock1content"] > table > tr')
                msgBuilder = LineMsgBuilder()
                columnBuilder = LineMsgBuilder(type=LineMsgBuilder.COLUMN)
                fileCount = 1
                for elem in infoDetails:
                    title = elem.select_one('td:nth-child(1)')
                    val = elem.select_one('td:nth-child(2)')
                    valText = val.text.strip('\n')
                    if valText != '':
                        msgBuilder.append(
                            title   = title.text,
                            content = valText,
                        )
                        # 添付ファイルの確認
                        valChildAnchor = val.select_one('a[class="jsDownload"]')
                        if valChildAnchor != None:
                            uploadFileName = f'{updateDate}_{infoCount}_{fileCount}.pdf'
                            if parseUtil.wget(valChildAnchor.get('href'), uploadFileName):
                                awsConnector.uploadFileToS3(uploadFileName)
                                columnBuilder.append(
                                    name = valText,
                                    uri  = awsConnector.getFileUrl(uploadFileName),
                                )
                            fileCount += 1
                lineConnector.sendPortalNewInfo(msgBuilder.toString())
                if not columnBuilder.isEmpty():
                    lineConnector.sendCarousel(columnBuilder.toList())
                infoCount += 1
            awsConnector.updateLastNewsTitle(newInfo[0].text)
    else:
        print('newInfo was none.')

    return Result.OK