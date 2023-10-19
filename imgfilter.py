from PIL import Image
import math
import re

class InputStream:
    """This is the Input Stream. This will give us operations to read 
    characters from the input."""

    def __init__(self, text: str):
        # self.text is the code that is being streamed
        self.text = text

        # These are for showing where the stream is pointing
        self.pos = 0
        self.line = 1
        self.col = 0
    
    
    def peek(self) -> str:
        "Returns the next value but without removing it from the stream"

        # get character at pointed position,
        # if out of bounds, return empty string
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
    

    def __repr__(self):
        return self.__str__()
    

class BinaryToken(Token):
    """This is a binary token. This defines chunks of data where a
    binary operation takes place."""

    def __init__(self, tType: str, value, left, right):
        super().__init__(tType, value)
        self.left = left
        self.right = right

    
    def __repr__(self):
        return (
            f'BinaryToken(type: {self.type}, value: {self.value}, '
            f'left: {self.left}, right: {self.right})'
        )
    

    def __str__(self):
        return f'{self.left} {self.value} {self.right}'
    

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
    

class IndexToken(Token):
    """This is an index token. This defines accessing a value in a list,
    or for our purpose, accessing pixels."""

    def __init__(self, tType: str, var, index):
        self.type = tType
        self.var = var
        self.index = index

    
    def __str__(self):
        return (
            f'IndexToken(type: {self.type}, var: {self.var}, '
            f'index: {self.index})'
        )
    

class IfToken(Token):
    """This is an if token. It defines a chunk of data as an if
    statement."""

    def __init__(self, tType: str, cond, then, otherwise = None):
        super().__init__(tType, cond)
        self.then = then
        self.otherwise = otherwise

    
    def __str__(self):
        return (
            f'IfToken(type: {self.type}, cond: {self.value}, ',
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


class ForToken:
    """This is a for token. It defines a for loop, its initialization,
    its condition, and its increment condition."""

    def __init__(self, tType: str, init, cond, incr, body):
        self.type = tType
        self.init = init
        self.cond = cond
        self.incr = incr
        self.body = body

    
    def __str__(self):
        return (
            f'ForToken(type: {self.type}, init: {self.init}, '
            f'cond: {self.cond}, incr: {self.incr}, body: {self.body})'
        )


class Tokenizer:
    """This is the tokenizer. Utilizing the InputStream, it converts
    data read in from the input into Tokens that define the data."""

    def __init__(self, text : str):
        self.stream = InputStream(text)

        # Because self.next doesn't always call self.readNext,
        # a current variable is needed to keep track of peeked tokens.
        self.current = None


    def isKeyword(self, x) -> bool:
        "Returns true if x is a keyword."

        # To ensure that keywords aren't searched for in the middle of
        # other keywords, all the keywords are surrounded with spaces
        return " if else lambda true false for ".find(
            ' ' + x + ' '
        ) >= 0
    

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
        token = self.current
        # Wipes current clean
        self.current = None
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
    

# I would like to convert this class into a function, as it doesn't
# make use of anything exclusive to a class
class Parser:
    """The Parser class will interpret the tokens made from the
    Tokenizer and group them together in a more programmatic way,
    making it all into a collection of tokens that contain each other"""

    # The PRECEDENCE defines the order of operations of operators
    # The higher the value, the higher the precedence
    PRECEDENCE = {
        '=': 1, '||': 2, '&&': 3,
        '<': 7, '>': 7, '<=': 7, '>=': 7, '==': 7, '!=': 7,
        '+': 10, '-': 10,
        '*': 20, '/': 20, '%': 20, '//': 20
    }

    def __init__(self, text: str):
        self.input = Tokenizer(text)
        # Parses everything and saves it to tokens
        # However, it would be better to convert our Parser class
        # to a function, as that makes more sense
        self.tokens = self.parseTopLevel()
    
    
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

    
    def unexpected(self, token):
        "Throws an error, call when encountering an unexpected token."

        self.input.throw(f'Unexpected Token: {token}')


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
    

    def parseIndex(self, var):
        """Parses an indice, returns a IndexToken containing the
        variable name and its index."""

        return IndexToken(
            'index',
            var,
            self.delimited('[', ']', ',', self.parseExpression)
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
        "Parses an if statement, returns an IfToken."

        # Skips past 'if' keyword
        self.skipKw('if')

        # Reads a conditional expression
        cond = self.parseExpression()

        # Reads if logic
        then = self.parseExpression()

        # Generates the IfToken
        ret = IfToken(
            'if',
            cond,
            then
        )

        # If next token is an 'else' keyword, then add else expression
        if self.isKw('else'):
            self.input.next()
            ret.otherwise = self.parseExpression()

        return ret
    

    def parseLambda(self):
        "Parses a lambda function, returns FuncToken."

        return FuncToken(
            'lambda',
            # Grabs parameters between ( and )
            self.delimited('(', ')', ',', self.parseVarName),
            # Parses the logic
            self.parseExpression()
        )
    

    def parseFor(self):
        "Parses a for loop, returns ForToken."

        # Skips for keyword
        self.input.next()
        # Skips first parenthese
        self.skipPunc('(')

        # Gets expressions in the for loop
        init = self.parseExpression()
        self.skipPunc(';')
        cond = self.parseExpression()
        self.skipPunc(';')
        incr = self.parseExpression()
        self.skipPunc(')')
        body = self.parseProg()

        # Returns ForToken
        return ForToken(
            'for',
            init = init,
            cond = cond,
            incr = incr,
            body = body
        )
    

    def parseBool(self):
        "Parses a bool, returns a Token containing boolean."

        return Token(
            'bool',
            # Works because it will return True if the value is
            # equal to true and False otherwise
            self.input.next().value == 'true'
        )
    

    def maybeAccess(self, expr):
        """Parses whether or not a function is being called or indexed.
        Returns a CallToken if being called, an IndexToken if being
        indexed, otherwise returns the inputted expression."""

        expr = expr()

        if self.isPunc('('): return self.parseCall(expr)
        if self.isPunc('['): return self.parseIndex(expr)
        return expr
    
    
    def _parseAtomHelper(self):
        """Determines the type of the next Token, and parses
        accordingly. Returns a Token of some sort."""

        # If next Token is a '(', parse next Tokens as an expression
        if self.isPunc('('):
            self.input.next()
            expr = self.parseExpression()
            self.skipPunc(')')
            return expr
        
        # If next Token is a '{', parse next Tokens as a program
        if self.isPunc('{'):
            return self.parseProg()
        
        # If 'if', parse if statement
        if self.isKw('if'):
            return self.parseIf()
        
        # If 'bool', parse boolean
        if self.isKw('true') or self.isKw('false'):
            return self.parseBool()
        
        # If 'lambda', parse lambda function
        if self.isKw('lambda'):
            self.input.next()
            return self.parseLambda()
        
        # If 'for', parse for loop
        if self.isKw('for'):
            return self.parseFor()
        
        # All of the Token checks automatically advance Tokens,
        # but because this isn't using a Token check, we advance it
        # manually, and check if it's a variable name or number
        token = self.input.next()
        if token.type == 'var' or token.type == 'num':
            return token
        
        # Throws an error because unknown Token
        self.unexpected(token)


    def parseAtom(self):
        """Parses the next collection of Tokens, while also checking if
        is a function call or an index."""

        return self.maybeAccess(self._parseAtomHelper)
    

    def parseTopLevel(self):
        """Loops through all Tokens, adding all the classified Tokens
        to a list, and then finally returning a Token containing the
        program in Token form."""

        prog = []

        # Loop through all tokens
        while not self.input.eof():
            # Add parsed expressions to list
            prog.append(self.parseExpression())

            # Skip semicolons
            if not self.input.eof():
                self.skipPunc(';')

        return Token('prog', prog)
    

    def parseProg(self):
        "Parses code in between {}, returns a Token of type 'prog'."

        # Parses all the code in between the {}s
        prog = self.delimited('{', '}', ';', self.parseExpression)

        # If there were no Tokens in between the {}s,
        # return a False Token
        if len(prog) == 0:
            return Token('bool', False)
        # Or if there was only one expression in the braces,
        # just return the expression
        if len(prog) == 1:
            return prog[0]
        
        return Token('prog', prog)
    

    def _parseExprHelper(self):
        """Parses expressions, determining whether they are binary
        expressions in the process."""

        return self.maybeBinary(self.parseAtom(), 0)
    
 
    def parseExpression(self):
        """Parses an expression, while also checking if it is a
        function being called or a variable being indexed."""
        
        return self.maybeAccess(self._parseExprHelper)


class Environment:
    """The Environment class is keeps track of variables, as well as
    ensuring that new variables are saved to the correct scope.
    
    It can be initialized with variables via vars, and can simulate
    scope by giving it another instance of Environment via parent."""


    def __init__(self, vars : dict = dict(), parent = None):
        # dictionary of variables in scope
        self.vars = vars
        # parent Environment instance, used to simiulate scope
        self.parent : Environment = parent


    def _lookup(self, key):
        "Checks to see if key is in scope or parent's scope."

        # Checks own scope
        if key in self.vars:
            return True
        
        # Checks if there is a parent
        if not self.parent:
            return False

        # Checks parent's scope
        return self.parent._lookup(key)

    
    def __getitem__(self, key):
        "Gets item from either own scope or parent's scope."

        # If key in scope, return value
        if key in self.vars:
            return self.vars[key]
        
        # If key in parent, return value
        if self.parent and self.parent._lookup(key):
            return self.parent[key]
        
        # KeyError, key not found
        raise KeyError(key)
    

    def __setitem__(self, key, value):
        "Adds new variable to scope."

        self.vars[key] = value


# This could also be made into a function, or we could apply multiple
# filters to one image, which is an interesting idea
class ImgFilter:
    """The ImgFilter class will take the given image and open it, and
    also evaluate the written code, giving it ways to access and filter
    the given image."""

    def __init__(self, imgname):
        self.imgname = imgname
        # Opens the image and saves it to the class
        with Image.open(f'static/images/source/{imgname}') as self.img:
            if self.img.mode != 'RGB':
                self.img = self.img.convert('RGB')
            # Also saves the pixels, which is what we can edit to change
            # the photo
            self.pixels = self.img.load()

        # Saves the dimensions for use in the user's code
        self.width = self.img.size[0]
        self.height = self.img.size[1]

        # Saves variables accessible to the user
        self.env = Environment({
            'pixels': self.pixels,
            'width': self.width,
            'height': self.height,
            'rgb': lambda r, g, b : (int(r), int(g), int(b)),
            'loadColor': lambda x, y : self.loadColor(x, y),
            'makeRef': self.makeRef,
            'loadRef': lambda x, y : self.loadRef(x, y),
            'sqrt': lambda x : math.sqrt(x)
        })


    def evaluate(self, token: Token, env):
        """Reads tokens and returns and saves them in a way usable by
        Python."""

        # Gets the type of the given token
        typ = token.type

        # If number or boolean, return the value as int, float, or bool
        if typ in ('num', 'bool'):
            return token.value
        
        # If the name of a variable, return the value of the variable
        if typ == 'var':
            return env[token.value]
        
        # If assignment token, then save the variable to the environment
        if typ == 'assign':
            # If the token that is to be saved is an index
            if token.left.type == 'index':
                if token.left.var.value != 'pixels':
                    raise SyntaxError(f'Cannot assign to {token.left}')
                if len(token.left.index) != 2:
                    raise SyntaxError(f'index must include x and y')
                if token.right.value.value != 'rgb':
                    raise SyntaxError(
                        f'rgb function must be used to save to pixels'
                    )
                
                x = self.evaluate(token.left.index[0], env)
                y = self.evaluate(token.left.index[1], env)

                color = self.evaluate(token.right, env)
                env[token.left.var.value][x, y] = color

                return color

            # If the token that is supposed to be saved to isn't a
            # variable name, then throw an error
            if token.left.type != 'var':
                raise SyntaxError(f'Cannot assign to {token.left}')
            # Otherwise, evaluate the tokens that are supposed to be
            # assigned to the variable
            value = self.evaluate(token.right, env)
            # And then save it to the environment
            env[token.left.value] = value
            # And return the value that was saved
            return value
        
        # If it is a BinaryToken, then apply the operation
        # and return the value
        if typ == 'binary':
            return self.applyOp(
                # First give the operator
                op = token.value,
                # Then the numbers that are being operated on
                a  = self.evaluate(token.left, env),
                b  = self.evaluate(token.right, env)
            )

        # If it is a lambda token, then call makeLambda, a functino
        # used for Interpreting functions and making them callable
        if typ == 'lambda':
            return self.makeLambda(token, env) 
        
        # If it is an IfToken
        if typ == 'if':
            # Evaluate the if condition
            cond = self.evaluate(token.value, env)

            # If a condition is true,
            # evaluate the then part of the IfToken
            # else, evaluate otherwise of IfToken
            # Finally return False if there was no condition
            # and there was no otherwise statement
            if cond:
                return self.evaluate(token.then, env)
            elif token.otherwise:
                return self.evaluate(token.otherwise, env)
            else:
                return False
            
        # If type 'prog', go through all the contained tokens
        # and evaluate them, returning the value of the final token
        if typ == 'prog':
            val = False
            for expr in token.value:
                val = self.evaluate(expr, env)
            return val

        # If the Token is calling a function
        if typ == 'call':
            # Get the function saved in memory by evaluating the name
            # of the function
            func = self.evaluate(token.value, env)

            # And then apply the saved args to the function using the
            # splat operator to unpack it into the function
            return func(
                *[self.evaluate(arg, env) for arg in token.args]
            )
        
        # If the Token is a for loop
        if typ == 'for':
            return self.forEval(token, env)
        
        # Raise an error if the token isn't recognized
        raise SyntaxError(f'Unable to evaluate {token}')
    

    def applyOp(self, op, a, b):
        """The applyOp function will perform the given operation (op)
        on a and b."""

        def num(x):
            "This will ensure that x is operable."

            # If it's not an int or a float, throw an error
            if type(x) != int and type(x) != float:
                raise TypeError(
                    f'Expected int of float, got {x}, type {type(x)}'
                )
            return x
        
        def div(x):
            """This will ensure that x is both not zero (so that other
            numbers can be divided by it), and is operable."""

            if num(x) == 0:
                raise ZeroDivisionError('division by zero')
            return x
        
        # Applies the operator
        if op == '+' : return num(a) + num(b)
        if op == '-' : return num(a) - num(b)
        if op == '*' : return num(a) * num(b)
        if op == '/' : return num(a) / div(b)
        if op == '%' : return num(a) % div(b)
        if op == '&&': return a != False and b
        if op == '||': return a if a != False else b
        if op == '<' : return num(a) < num(b)
        if op == '>' : return num(a) > num(b)
        if op == '<=': return num(a) <= num(b)
        if op == '>=': return num(a) >= num(b)
        if op == '==': return a == b
        if op == '!=': return a != b
        if op == '//': return num(a) // div(b)

        # Throw an error if unrecognized operator
        raise SyntaxError(f'Unrecognized operator {op}')
    

    def makeLambda(self, token, env):
        """The makeLambda function will return a function that will
        evaluate tokens and run them when called."""

        # The function to be returned, this will
        # usually be saved to the environment
        def func(*argv):
            # Read the variable names given by the lambda token
            names = token.vars

            # Create a new environment that will simulate scope,
            # ensuring that variables saved in the function will not
            # be accessible from outside of the function
            scope = Environment(parent=env)

            # Saves the given parameters in *argv to the names given
            # to the function inside the local scope
            for i in range(len(names)):
                # If a position arg wasn't given, save it as False
                scope[names[i]] = argv[i] if i < len(argv) else False
            
            # Returns the last read value
            return self.evaluate(token.body, scope)
        
        # Returns the generated function
        return func
    

    def forEval(self, token, env):
        "Loops through for loop while its condition is true."

        scope = Environment(parent=env)

        self.evaluate(token.init, scope)

        while self.evaluate(token.cond, scope):
            self.evaluate(token.body, scope)
            self.evaluate(token.incr, scope)
        
        return None
    

    def loadColor(self, x, y):
        r, g, b = self.pixels[x, y]

        self.env['r'] = r
        self.env['g'] = g
        self.env['b'] = b


    def makeRef(self):
        self.ref = self.img.copy().load()


    def loadRef(self, x, y):
        r, g, b = self.ref[x, y]

        self.env['r'] = r
        self.env['g'] = g
        self.env['b'] = b
    

    def __call__(self, text):
        """When an initiated ImgFilter class is called and given code
        to read, it will run that code."""

        parser = Parser(text)

        self.evaluate(parser.tokens, self.env)
        self.img.save(f'static/images/filtered/{self.imgname}')


if __name__ == '__main__':
    with open('filters/grayscale.txt', 'r') as file:
        text = file.read()

    img = ImgFilter('cad.png')
    img.env['print'] = lambda x : print(x)

    img(text)
