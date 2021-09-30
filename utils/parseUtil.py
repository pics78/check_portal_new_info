from bs4 import BeautifulSoup

from env.envMgr import getEnv
from env.envKeyDef import Lambda

tmpDir = getEnv(Lambda.TMP_DIR)

class ParseUtil:
    def __init__(self, session, domain, soup=None):
        self.session = session
        self.domain  = domain
        self.soup    = soup

    def getSoup(self, method, path, data=None):
        self.soup = BeautifulSoup(
            self.session.request(method, self.domain + path, data=data).text, 'html.parser')
        return self
        
    def wget(self, path, file):
        data = self.session.request('GET', self.domain + path).content
        try:
            with open(tmpDir + file ,mode='wb') as f:
                f.write(data)
            return True
        except:
            return False
    
    def selectInSoup(self, selector):
        return self.soup.select(selector) if self.soup != None else None
    
    def findInSoup(self, target, attrs=None):
        return self.soup.find(target, attrs=attrs) if self.soup != None else None