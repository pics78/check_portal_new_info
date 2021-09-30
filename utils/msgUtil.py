from connector.lineConnector import getCarouselColumn

class LineMsgBuilder:

    TEXT    = 'text'
    COLUMN  = 'column'

    def __init__(self, sep='\n', type=TEXT):
        self.msgBuffer = []
        self.sep = sep
        self.type = type
        self.next = None

    def append(self, title=None, content=None, name=None, uri=None):
        if self.type == self.TEXT:
            if title != None:
                self.msgBuffer.append(f'<{title}>')
            if content != None:
                self.msgBuffer.append(content + '\n')
        elif self.type == self.COLUMN:
            if name != None and uri != None:
                self.msgBuffer.append(getCarouselColumn(name, uri))
        return self

    def toString(self):
        if self.type == self.TEXT:
            return self.sep.join(self.msgBuffer)
        else:
            return None
    
    def toList(self):
        if self.type == self.COLUMN:
            return self.msgBuffer
        else:
            return None