from enum import Enum

# ポータルサイトへのアクセス関連
class Portal(Enum):
    USR = 'USER_ID'
    PW = 'PASS'
    URL = 'PORTAL_URL'
    LOGINPATH = 'LOGIN_PATH'
    PARAMNAME1 = 'INPUT_PARAM_1'
    PARAMNAME2 = 'INPUT_PARAM_2'

# LINE通知関連
class Line(Enum):
    TOKEN = 'LINE_CHANNEL_ACCESS_TOKEN'
    USR = 'LINE_USER_ID'

# AWS認証関連
class AwsIam(Enum):
    ACCESS_KEY_ID = 'ACCESS_KEY_ID'
    SECRET_ACCESS_KEY = 'SECRET_ACCESS_KEY'

# DynamoDB接続関連
class Dynamodb(Enum):
    TABLE = 'DYNAMODB_TABLE_NAME'
    PARTI = 'DYNAMODB_PARTITION_KEY'

# テスト実行用
class StatusForRunning(Enum):
    MODE = 'RUNNING_MODE'
    IS_TEST = '1'