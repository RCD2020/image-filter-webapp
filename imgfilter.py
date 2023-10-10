from PIL import Image
import re

class InputStream:
    """This is the Input Stream. This will give us operations to read 
    characters from the input."""

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
    

    def throw(self, msg):
        "Error message for unexpected characters."

        raise SyntaxError(f'\033[31m{self}: {msg}\033[00m')
    

    def __str__(self) -> str:
        return (
            f'InputStream(pos: {self.pos}, line: {self.line}, '
            f'col: {self.col})'
        )
    

    def __repr__(self) -> str:
        return self.__str__()
    

class Token:
    """This is a token. This defines the chunks of data with the type
    and the value."""

    def __init__(self, tType: str, value):
        self.type = tType
        self.value = value


    def __str__(self):
        return f'Token(type: {self.type}, value: {self.value})'
    

class BinaryToken(Token):
    def __init__(self, tType: str, value, left, right):
        super().__init__(tType, value)
        self.left = left
        self.right = right

    
    def __str__(self):
        return (
            f'BinaryToken(type: {self.type}, value: {self.value}, '
            f'left: {self.left}, right: {self.right})'
        )
    

class CallToken(Token):
    def __init__(self, tType: str, value, args: list):
        super().__init__(tType, value)
        self.args = args

    
    def __str__(self):
        return (
            f'CallToken(type: {self.type}, value: {self.value}, '
            f'args: {self.args})'
        )
    

class IfToken(Token):
    def __init__(self, tType: str, value, then, otherwise = None):
        super().__init__(tType, value)
        self.then = then
        self.otherwise = otherwise

    
    def __str__(self):
        return (
            f'IfToken(type: {self.type}, value: {self.value}, ',
            f'then: {self.then}, otherwise: {self.otherwise})'
        )
    

class FuncToken(Token):
    def __init__(self, tType: str, variables, body):
        self.type = tType
        self.vars = variables
        self.body = body


    def __str__(self):
        return (
            f'FuncToken(type: {self.type}, vars: {self.vars}, '
            f'body: {self.body})'
        )


class Tokenizer:
    """This is the tokenizer. Utilizing the InputStream, it converts
    data read in from the input into Tokens that define the data."""

    def __init__(self, inputStream : InputStream):
        self.stream = inputStream

        # Because self.next doesn't always call self.readNext,
        # a current variable is needed to keep track of peeked tokens.
        self.current = None


    def isKeyword(self, x) -> bool:
        "Returns true if x is a keyword."

        # To ensure that keywords aren't searched for in the middle of
        # other keywords, all the keywords are surrounded with spaces
        return " if else lambda true false ".find(' ' + x + ' ') >= 0
    

    def isDigit(self, ch) -> bool:
        "Returns true if ch is a digit 0-9"

        return re.search('[0-9]', ch)
    

    def isIdStart(self, ch) -> bool:
        """Returns true if ch is a character that can be at the
        beginning of id names. Valid characters are any letter
        regardless of case and underscores."""

        return re.search('[A-Za-z_]', ch)
    
    
    def isId(self, ch) -> bool:
        """Returns true if ch is a character that can be at the
        beginning of a keyword (see self.isIdStart) or a digit,
        which can be in the middle or end of id names."""

        return self.isIdStart(ch) or re.search("[0-9]", ch)
    

    def isOpChar(self, ch) -> bool:
        "Returns true if ch is an operator character."

        return '+-*/%=&|<>!'.find(ch) >= 0
    

    def isPunc(self, ch) -> bool:
        "Returns true if ch is a punctuation character."

        return ',;(){}[]'.find(ch) >= 0
    

    def isWhitespace(self, ch) -> bool:
        "Returns true if ch is a space, tab, or newline character."

        return ' \t\n'.find(ch) >= 0
    

    def readWhile(self, predicate) -> str:
        """Input a boolean returning function (predicate), and readWhile
        will return a string of the next characters in the InputStream
        that conform to the predicate."""

        text = ''
        # Loops while not end of file and passes the predicate.
        while not self.stream.eof() and predicate(self.stream.peek()):
            text += self.stream.next()
        return text


    def isNum(self, ch) -> bool:
        """Returns true if ch is a valid digit for a number, and is not
        a repeating decimal point."""

        # If '.', then either return False signifying that a decimal has
        # already been read in or return True and mark the decimal as
        # having been read in
        if ch == '.':
            if self._hasDot:
                return False
            self._hasDot = True
            return True
        # Else return True if ch is a valid digit
        return self.isDigit(ch)
    

    def readNumber(self) -> Token:
        "Reads a number and converts it into a Token(type: 'num')"

        # Marks the number as not yet containing a decimal point
        self._hasDot = False

        # Passes the self.isNum predicate into readWhile to get the
        # number from the InputStream
        num = self.readWhile(self.isNum)

        # Converts the string of the number into an integer or float
        if self._hasDot:
            num = float(num)
        else:
            num = int(num)
        
        return Token('num', num)

        
    def readIdent(self) -> Token:
        """Reads an identity token and determine whether it is
        type 'kw' (keyword) or type 'var'."""

        # Reads the identity from the InputStream using self.isId pred
        id = self.readWhile(self.isId)

        # Returns the Token while also determining whether it is a
        # keyword or a variable
        return Token('kw' if self.isKeyword(id) else 'var', id)
    

    def skipComment(self) -> None:
        "Skips over all the commented line in the InputStream"

        # Continue while ch is not a new line
        self.readWhile(lambda ch : ch != '\n')
        self.stream.next()

    
    def readNext(self) -> Token:
        "Validates and tokenizes all the characters in the InputStream"

        # Skip over whitespace and end when end of file
        self.readWhile(self.isWhitespace)
        if self.stream.eof():
            return None
        
        # Look at next char in InputStream to validate and Tokenize
        ch = self.stream.peek()

        # Checks if comment
        if ch == '#':
            self.skipComment()
            return self.readNext()
        
        # checks if number
        if self.isDigit(ch):
            return self.readNumber()
        
        # checks if keyword or variable name
        if self.isIdStart(ch):
            return self.readIdent()
        
        # checks if punctuation
        if self.isPunc(ch):
            return Token('punc', self.stream.next())
        
        # checks if operator
        if self.isOpChar(ch):
            return Token('op', self.readWhile(self.isOpChar))
        
        # Throws SyntaxError if ch doesn't fit into any group
        self.stream.throw(f'Unexpected character "{ch}"')

    
    def peek(self):
        "Returns next token without advancing."
        
        # Read self.__init__ for better understanding of self.current

        # Checks if the next token has already been read in or not,
        # and reads it in and returns it if it hasn't.
        if self.current == None:
            self.current = self.readNext()
        return self.current
        

    def next(self):
        "Returns the next token and advances."

        # Read self.__init__ for better understanding of self.current

        # Saves potentially peeked token (current) to token
        token = current
        # Wipes current clean
        current = None
        # Returns token if current was a token, or reads the next token
        return token or self.readNext()
    

    def eof(self):
        "Returns true if at the end of the file."

        return self.peek() == None
    

    def throw(self, msg):
        self.stream.throw(f'{self}: {msg}')


    def __str__(self):
        return 'Tokenizer()'
    

class Parser:
    FALSE = { 'type': 'bool', 'value': False }
    PRECEDENCE = {
        '=': 1, '||': 2, '&&': 3,
        '<': 7, '>': 7, '<=': 7, '>=': 7, '==': 7, '!=': 7,
        '+': 10, '-': 10,
        '*': 20, '/': 20, '%': 20
    }

    def __init__(self, tokenizer: Tokenizer):
        self.input = tokenizer
    
    
    def isPunc(self, ch):
        token = self.input.peek()
        return (
            token
            and token.type == 'punc'
            and (not ch or token.value == ch)
            and token
        )
    

    def isKw(self, kw):
        token = self.input.peek()
        return (
            token
            and token.type == 'kw'
            and (not kw or token.value == kw)
            and token
        )
    

    def isOp(self, op = None):
        token = self.input.peek()
        return (
            token
            and token.type == 'op'
            and (not op or token.value == op)
            and token
        )
    

    def skipPunc(self, ch):
        if self.isPunc(ch):
            self.input.next()
        else:
            self.input.throw(f'Expecting punctuation, got "{ch}"')


    def skipKw(self, kw):
        if self.isKw(kw):
            self.input.next()
        else:
            self.input.throw(f'Expecting keyword, got "{kw}"')

    
    def skipOp(self, op):
        if self.isOp(op):
            self.input.next()
        else:
            self.input.throw(f'Expecting operator, got "{op}"')

    
    def unexpected(self):
        self.input.throw(f'Unexpected Token: {self.input.peek()}')


    def maybeBinary(self, left, prec):
        token = self.isOp()

        if token:
            valPrec = self.PRECEDENCE[token.value]

            if valPrec > prec:
                self.input.next()

                return self.maybeBinary(
                    BinaryToken(
                        'assign' if token.value == '=' else 'binary',
                        token.value,
                        left,
                        self.maybeBinary(self.parseAtom(), valPrec)
                    ),
                    prec
                )
            
        return left
    

    def delimited(self, start, stop, separator, parser):
        a = []
        first = True

        self.skipPunc(start)

        while not self.input.eof():
            if self.isPunc(stop):
                break

            if first:
                first = False
            else:
                self.skipPunc(separator)

            if self.isPunc(stop):
                break
            
            a.append(parser())
        
        self.skipPunc(stop)
        return a
    

    def parseCall(self, func):
        return CallToken(
            'call',
            func,
            self.delimited('(', ')', ',', self.parseExpression)
        )
    

    def parseVarName(self):
        name = self.input.next()

        if name.type != 'var':
            self.input.throw(f'Expecting variable name, got {name}')

        return name.value
    

    def parseIf(self):
        self.skipKw('if')

        cond = self.parseExpression()

        then = self.parseExpression()

        ret = IfToken(
            'if',
            cond,
            then
        )

        if self.isKw('else'):
            self.input.next()
            ret.otherwise = self.parseExpression()

        return ret
    

    def parseLambda(self):
        return FuncToken(
            'lambda',
            self.delimited('(', ')', ',', self.parseVarName),
            self.parseExpression()
        )


if __name__ == '__main__':
    pass