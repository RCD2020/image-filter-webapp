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
    """This is a binary token. This defines chunks of data where a
    binary operation takes place."""

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
    """This is a call token. This defines a call to a function and its
    parameters."""

    def __init__(self, tType: str, value, args: list):
        super().__init__(tType, value)
        self.args = args

    
    def __str__(self):
        return (
            f'CallToken(type: {self.type}, value: {self.value}, '
            f'args: {self.args})'
        )
    

class IfToken(Token):
    """This is an if token. It defines a chunk of data as an if
    statement."""

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
    """This is a func token. It defines a function, its variables, and
    the programming within."""

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
        "Throws an error"

        self.stream.throw(f'{self}: {msg}')


    def __str__(self):
        return 'Tokenizer()'
    

class Parser:
    """The Parser class will interpret our tokens make from the
    Tokenizer and group them together in a more programmatic way,
    making it all into a collection of tokens that contain each other"""

    # The PRECEDENCE defines the order of operations of operators
    # The higher the value, the higher the precedence
    PRECEDENCE = {
        '=': 1, '||': 2, '&&': 3,
        '<': 7, '>': 7, '<=': 7, '>=': 7, '==': 7, '!=': 7,
        '+': 10, '-': 10,
        '*': 20, '/': 20, '%': 20
    }

    def __init__(self, tokenizer: Tokenizer):
        self.input = tokenizer
    
    
    def isPunc(self, ch):
        """Returns a token if ch is punctuation or the next token is
        punctuation, otherwise returns False."""

        # Looks at next token
        token = self.input.peek()

        # If the token is of type 'punc', ch is None or the value of the
        # next token is equal to ch, then return the token
        return (
            # Token is checked first so that an error doesn't throw
            # because of trying to access members of None
            token
            and token.type == 'punc'
            and (not ch or token.value == ch)
            # Having token come last allows this statement to return
            # token instead of returning True
            and token
        )
    

    def isKw(self, kw):
        """Returns a token is kw is a keyword or if the next token is a
        keyword, otherwise returns False."""

        # Looks at next token
        token = self.input.peek()

        # See self.isPunc for explanation
        return (
            token
            and token.type == 'kw'
            and (not kw or token.value == kw)
            and token
        )
    

    def isOp(self, op = None):
        """Returns a token is op is an operator or if the next token is
        an operator, otherwise returns False."""

        # Looks at next token
        token = self.input.peek()

        # See self.isPunc for explanation
        return (
            token
            and token.type == 'op'
            and (not op or token.value == op)
            and token
        )
    

    def skipPunc(self, ch):
        """Checks if the next token is the expected ch (character), and
        skips it if so, otherwise throws an error."""

        # Looks at next token and checks if its value matches ch
        if self.isPunc(ch):
            # Skips next token if so
            self.input.next()
        else:
            # Else throws an exception
            self.input.throw(
                f'Expecting {ch}, got "{self.input.peek()}"'
            )


    def skipKw(self, kw):
        """Checks if the next token is the expected kw (keyword), and
        skips it if so, otherwise throws an error."""

        # Looks at next token and checks if its next value matches kw
        if self.isKw(kw):
            # Skips next token if so
            self.input.next()
        else:
            # Else throws an exception
            self.input.throw(
                f'Expecting {kw}, got "{self.input.peek()}"'
            )

    
    def skipOp(self, op):
        """Checks if the next token is the expected op (operator), and
        skips it if so, otherwise throws an error."""

        # Looks at next token and checks if its next value matches op
        if self.isOp(op):
            # Skips next token if so
            self.input.next()
        else:
            # Else throws an exception
            self.input.throw(
                f'Expecting {op}, got "{self.input.peek()}"'
            )

    
    def unexpected(self):
        "Throws an error, call when encountering an unexpected token."

        self.input.throw(f'Unexpected Token: {self.input.peek()}')


    def maybeBinary(self, left, prec):
        """Checks if the next token is a binary operator as opposed to a
        unary one, and returns a BinaryToken if so. Otherwise, returns 
        the given Token."""

        # Peeks next token if it is an operator
        token = self.isOp()

        # If an operator token was returned:
        if token:
            # Get the precedence of the operator in the token
            valPrec = self.PRECEDENCE[token.value]

            # If the operator precedence is greater than the given
            # precedence:
            if valPrec > prec:
                # Move to next token
                self.input.next()

                # Return a BinaryToken, while potentially filling it
                # with more operations
                return self.maybeBinary(
                    BinaryToken(
                        'assign' if token.value == '=' else 'binary',
                        token.value,
                        left,
                        self.maybeBinary(self.parseAtom(), valPrec)
                    ),
                    prec
                )
        
        # If next token isn't an operator, return the given Token
        return left
    

    def delimited(self, start, stop, separator, parser):
        """Grabs all token between start and stop, separating
        by separator, and parsing via parser."""

        # List for tokens
        a = []
        # Ensures that an error isn't thrown looking for punctuation
        # preceding the first token
        first = True

        # Skips leading delimiter
        self.skipPunc(start)

        # Reads tokens until eof file or break
        while not self.input.eof():

            # Checks for trailing delimiter and breaks if matches
            if self.isPunc(stop):
                break

            # If first Token, then do not check for separator
            if first:
                first = False
            else:
                self.skipPunc(separator)

            if self.isPunc(stop):
                break
            
            # Append parsed token
            a.append(parser())
        
        # Skips trailing delimiter
        self.skipPunc(stop)
        # Returns list of parsed tokens
        return a
    

    def parseCall(self, func):
        """Parses a function call, returns a CallToken containing the
        function and its parameters."""

        return CallToken(
            'call',
            func,
            self.delimited('(', ')', ',', self.parseExpression)
        )
    

    def parseVarName(self) -> str:
        """Parses a variable name, returns the name, and throws an error
        if the next token is not a variable name."""

        # Advance to next token
        name = self.input.next()

        # If Token.type is not 'var', throw an error
        if name.type != 'var':
            self.input.throw(f'Expecting var token, got {name}')

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
    

    def parseBool(self):
        return Token('bool', self.input.next().value == 'true')
    

    def maybeCall(self, expr):
        expr = expr()
        return self.parseCall(expr) if self.isPunc('(') else expr
    
    
    def _parseAtomHelper(self):
        if self.isPunc('('):
            self.input.next()
            expr = self.parseExpression()
            self.skipPunc(')')
            return expr
        
        if self.isPunc('{'):
            return self.parseProg()
        
        if self.isKw('if'):
            return self.parseIf()
        
        if self.isKw('true') or self.isKw('false'):
            return self.parseBool()
        
        if self.isKw('lambda'):
            self.input.next()
            return self.parseLambda()
        
        token = self.input.next()
        if token.type == 'var' or token.type == 'num':
            return token
        
        self.unexpected()


    def parseAtom(self):
        return self.maybeCall(self._parseAtomHelper)
    

    def parseTopLevel(self):
        prog = []

        while not self.input.eof():
            prog.append(self.parseExpression())
            if not self.input.eof():
                self.skipPunc(';')

        return Token('prog', prog)
    

    def parseProg(self):
        prog = self.delimited('{', '}', ';', self.parseExpression)

        if len(prog) == 0:
            return Token('bool', False)
        if len(prog) == 1:
            return prog[0]
        
        return Token('prog', prog)
    

    def _parseExprHelper(self):
        return self.maybeBinary(self.parseAtom(), 0)
    

    def parseExpression(self):
        return self.maybeCall(self._parseExprHelper)


if __name__ == '__main__':
    pass