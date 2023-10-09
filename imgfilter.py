from PIL import Image
import re

class InputStream:
    """This is the Input Stream. This will give us operations to read 
    characters from our input."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 0
    
    
    def peek(self) -> str:
        "Returns the next value but without removing it from the stream"

        try:
            return self.text[self.pos]
        except:
            return ''
        

    def next(self) -> str:
        "Returns the next value and discards it from the stream"

        ch = self.peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 0
        else:
            self.col += 1

        return ch
    

    def eof(self) -> bool:
        "Returns true if at the end of the file"

        return self.peek() == ''
    

    def throw(self, ch):
        raise SyntaxError(f'Cannot handle "{ch}". {self}')
    

    def __str__(self) -> str:
        return f'InputStream(pos: {self.pos}, line: {self.line}, col: {self.col})'
    

    def __repr__(self) -> str:
        return self.__str__()
    

class Token:
    def __init__(self, tType: str, value):
        self.type = tType
        self.value = value


    def __str__(self):
        return f'Token(type: {self.type}, value: {self.value})'


class Tokenizer:
    keywords = " if then else lambda true false "
    def __init__(self, inputStream : InputStream):
        self.stream = inputStream
        self.current = None


    def isKeyword(self, x):
        return self.keywords.find(' ' + x + ' ') >= 0
    

    def isDigit(self, ch):
        return re.search('[0-9]', ch)
    

    def isIdStart(self, ch):
        return re.search('[A-Za-z_]', ch)
    
    
    def isId(self, ch):
        return self.isIdStart(ch) or re.search("[0-9]", ch)
    

    def isOpChar(self, ch):
        return '+-*/%=&|<>!'.find(ch) >= 0
    

    def isPunc(self, ch):
        return ',;(){}[]'.find(ch) >= 0
    

    def isWhitespace(self, ch):
        return ' \t\n'.find(ch) >= 0
    

    def readWhile(self, predicate):
        text = ''
        while not self.stream.eof() and predicate(self.stream.peek()):
            text += self.stream.next()
        return text
    

    def readNumber(self):
        pass



class ImgFilter:
    def __init__(self, path):
        self.img = Image.open(path)
        self.vars = {}


    # def readCode(text):
    #     lines = text.split(';')
    #     current = ''
    #     for line in lines:
    #         for char in line:
    #             if re.search("[A-Za-z0-9_]", char):
    #                 current += char
    #                 print(char, 'is not /[A-Za-z0-9_]/g', current)
    #             else:
    #                 current = ''
    #                 print(char, 'is /[A-Za-z0-9_]/g', current)
            

if __name__ == '__main__':
    # InputStream.throw('@')
    # ImgFilter.readCode('test = 54 + 6')
    pass