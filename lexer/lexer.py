from .token import Token
from typing import Union, Sequence, Mapping

SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ', ', ';', '+', '-', '*', '/', '&', ', ', '<', '>', '=', '~', '|'}
KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 
            'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}


class Lexer:
    _content: str
    _computed: Sequence
    _position: Mapping[str, int]

    def __init__(self, content):
        self._content = content.splitlines()
        self._computed = []
        self._position = {
            'last_line': 0,
            'last_column': 0,
            'line': 0,
            'column': 0
        }

    def update_position(self, last_position: bool = False) -> bool:
        "return true if the position updated to the next line"
        "last position mark if the methof should update last_line, last_column"
        # end of line
        if self._position["column"] == len(self._content[self._position["line"]])-1:
            self._position["line"] += 1
            self._position["column"] = 0
            # empty lines
            while not self._content[self._position["line"]]:
                self._position["line"] += 1
                self._position["column"] = 0
            if last_position:
                self._position["last_line"] = self._position["line"]
                self._position["last-column"] = self._position["column"]

            # end of all lines
            if len(self._content) == self._position["line"]:
                raise EndOfFileError      
            return True
        
        else:
            self._position["column"] += 1
            if last_position:
                self._position["last_line"] = self._position["line"]
                self._position["last-column"] = self._position["column"]
            return False
 
    def get_constantInt(self, token_type) -> Token:
        value = ""

        while self.ch.isnumeric():
            value += self.ch
            if self.update_position():
                # TODO: raise a error of newline at constantInt
                pass
            line = self._position["line"]
            column = self._position["column"]

        token = Token(value, "constantInt")
        if token_type and token.type != token_type:
            raise TokenTypeError(token_type, token.type, self._position)
        return token

    def get_constantString(self, token_type) -> Token:
        value = ""
        try:
            while ord(self.ch) != 34:
                value += self.ch
                if self.update_position():
                    raise InvalidNewLineError(self._position)
        except (EndOfFileError):
            raise EndlessStringError(self._position) 
        # eat the closing quotation 
        self.update_position()
        token = Token(value, "constantString")
        if token_type and token.type != token_type:
            raise TokenTypeError(token_type, token.type, self._position)
        return token
        
    def get_keyword_or_identifier(self, token_type):
        word = ""
        while (self.ch.isalpha() or self.ch.isnumeric() or self.ch == "_"):
            word += self.ch
            if self.update_position():
                raise TokenParseError("A new line in keyword / identifier", self.position["line"], self.position["column"])
        if word in KEYWORDS:
            token = Token(word, "keyword")
        else:
            token = Token(word,  "identifier")
        if token_type and token.type != token_type:
            raise TokenTypeError(token_type, token.type, self._position)
        return token

    def peek_position(self):
        if self._position["column"] == len(self._content[self._position["line"]])-1:
            # end of all lines
            if len(self._content) == self._position["line"]+1:
                raise EndOfFileError()
            return self._position["line"] + 1, 0
        
        else:
            return self._position["line"], self._position["column"] + 1
    
    def remove_comment(self):
        new_line = False
        while not new_line:
            new_line = self.update_position()

    def remove_documentation(self):
        try:
            while True:
                if ord(self.ch) == 42:
                    line, column = self.peek_position()
                    if ord(self._content[line][column]) == 47:
                        self.update_position()
                        self.update_position()
                        return
                    else:
                        self.update_position()
                else:
                    self.update_position()
        except: EndOfFileError
            raise TokenParseError("endless doucumantion", self._position["last_line"], self._position["last_coulmn"])

    def next(self, token_type: Union[None, str] = None) -> Token:
        """Pops the next parsed token"""
        if self._computed:
            return self._computed.pop()
        # empty line
        while not self._content[self._position["line"]]: 
            self.update_position()
        line = self._position["line"]
        column = self._position["column"]
        
        # updates last positions values
        self._position["last_line"] = line
        self._position["last-column"] = column

        # ord('tab') = 32, ord(' ') = 9 
        if ord(self.ch) == 32 or ord(self.ch) == 9:
            self.update_position()
            return self.next(token_type)
        # constantInt 
        if self.ch.isnumeric():
            return self.get_constantInt(token_type)
        # constantString
        # ASCII code 34 is quotaion mark 
        if ord(self.ch) == 34:
            self.update_position()
            return self.get_constantString(token_type)

        # symbol or comment
        if self.ch in SYMBOLS:
            # ord('/') = 47
            if ord(self.ch) == 47:
                line, column = self.peek_position()
                # check if comment //
                if ord(self._content[line][column]) == 47:
                    self.remove_comment()
                    return self.next(token_type)
                # check if doucumantition /**
                # ord ('*') = 42
                if ord(self._content[line][column]) == 42:
                    self.update_position()
                    line, column = self.peek_position()
                    if ord(self._content[line][column]) == 42:
                        self.remove_documentation()
                        return self.next(token_type)
                    else:
                        raise TokenParseError("/* is not a legal sequance",
                              self._position["line"], self._position["column"])

            token = Token(self.ch, "symbol")
            self.update_position()
            return token
         
        return self.get_keyword_or_identifier(token_type)
        # unreachable code

        # Parse next token
        raise NotImplementedError

    def eat(self, value, token_type: str = None) -> None:
        """
        Pops the next parsed token and verify it matches to the give value and type.
        If no token_type was given, only value match is checked.
        """
        next_token = self.next(token_type)

        if not next_token.value == value:
            raise TokenTypeError(value, next_token.value, self.position)

    def peek(self) -> Token:
        """Returns the next parsed token without fetching it from the token queue"""
        next_token = self.next()
        self._computed.insert(0, next_token)
        return next_token

    @property
    def ch(self):
        line = self._position["line"]
        column = self._position["column"]
        return self._content[line][column]

    @property
    def position(self) -> Mapping[str, int]:
        """Returns the current position"""
        return self._position.copy()

    @property
    def finished(self) -> bool:
        """Returns whether we finished parsing all code, or there are more tokens to parse."""
        # TODO: Replace this line with a working logic to check if we finished parsing all code.
        return True

class EndOfFileError(Exception):
    def __init__(self):
        super().__init__("End Of File")

class TokenParseError(Exception):
    def __init__(self, description: str, line: int, column: int):
        super().__init__(f'Parse error at line {line}, column {column}: {description}')


class InvalidNewLineError(TokenParseError):
    def __init__(self, position: Mapping[str, int]):
        super().__init__(f'''The string after \" at {position['last_line']} , {position['last_column']},
         contains new line at {position['line']}, {position['column']}''')


class EndlessStringError(TokenParseError):
    def __init__(self, position: Mapping[str, int]):
        super().__init__(f'''The string \" at {position['last_line']} , {position['last_column']} 
        missing a closing quation''')

class TokenTypeError(TokenParseError):
    def __init__(self, expected: str, got: str, position: Mapping[str, int]):
        super().__init__(f"Expected {expected} and got \"{got}\"", position['line'], position['column'])


class TokenValueError(TokenParseError):
    def __init__(self, expected: str, got: str, position: Mapping[str, int]):
        super().__init__(f"Expected \"{expected}\" and got \"{got}\"", position['last_line'], position['last_column'])
