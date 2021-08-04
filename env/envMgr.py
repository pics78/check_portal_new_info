import os

# 環境情報を取得
is_dev = open('env/environment', 'r').readlines()[0] == 'DEV'
# 開発(ローカル)環境の場合は環境変数をローカルファイルから読み込む
localEnvDict = None
if is_dev:
    localEnvDict = {}
    f = open('local/env_info', 'r')
    for p in map(lambda line: line.rstrip('\n'), f.readlines()):
        key, val = p.split('=', 1)
        localEnvDict[key] = val

def getEnv(key):
    if localEnvDict != None:
        return localEnvDict[key.value]
    else:
        return os.environ[key.value]

def setAwsRegion():
    os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'