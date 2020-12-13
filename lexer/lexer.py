from .token import Token
from typing import Sequence, Mapping
import string

SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char',
            'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
WHITESPACES_CHARS = (' ', '\t', '\n')
IDENTIFIER_ALLOWED_CHARS = string.ascii_letters + '_' + string.digits


class Lexer:
    _content: str
    _computed: Sequence
    _position: Mapping[str, int]

    def __init__(self, content: str):
        self._content = content
        self._computed = []
        self._position = {
            'last_line': 0,
            'last_column': 0,
            'line': 0,
            'column': 0
        }

    def _get_next_char_with_comments(self, peek: bool = False) -> str:
        """Returns the next unparsed char without skipping comments"""
        # Check if we read beyond the file limits
        if not self._content:
            raise EndOfFileError(self.position)

        # Read next character
        result = self._content[0]
        if not peek:
            self._content = self._content[1:]

        # Update self._position
        if result == '\n':
            self._position['line'] += 1
            self._position['column'] = 0
        else:
            self._position['column'] += 1

        # Return read char
        return result

    def _get_next_char(self, peek: bool = False) -> str:
        """Returns the next unparsed char while skipping comments"""
        # In case the caller asked for peek, backup self._content original state
        if peek:
            original_content = self._content
            original_position = self._position.copy()

        if self._content.startswith('//'):
            # Next char starts a line comment
            next_character = self._get_next_char_with_comments()
            while next_character != '\n':
                next_character = self._get_next_char_with_comments()

            # Comment was ended, we can return next character.
            # Since a new comment can begin right away, we will call self._get_next_char
            # to handle the next character
            result = self._get_next_char()

        elif self._content.startswith('/*'):
            # Next char starts a multiline comment
            next_character = self._get_next_char_with_comments()
            while not (next_character == '*' and self._get_next_char_with_comments(peek=True) == '/'):
                next_character = self._get_next_char_with_comments()

            # Next character is '/' (after we poped '*'), pop it
            self._get_next_char_with_comments()

            # Comment was ended, we can return next character.
            # Since a new comment can begin right away, we will call self._get_next_char
            # to handle the next character
            result = self._get_next_char()

        else:
            # Next char is a regular character
            result = self._get_next_char_with_comments()

        # We can't modify self._content if the caller asked for peek, restore it to its original state
        if peek:
            self._content = original_content
            self._position = original_position

        return result

    def _get_next_sequence(self, allowed_chars: str) -> str:
        """Return the next maximum valid sequence that contains only allowed_chars"""
        result = ''
        # Check that there is a next_char, and that the next char is in allowed_chars
        while self._content and self._get_next_char(peek=True) in allowed_chars:
            result += self._get_next_char()
        return result

    def _skip_whitespaces(self) -> None:
        """Pops from queue all whitespaces characters"""
        self._get_next_sequence(WHITESPACES_CHARS)

    def next(self) -> Token:
        """Return the next maximum valid sequence that can be parsed as a token"""
        # Update last position
        self._position['last_line'], self._position['last_column'] = self.line, self.column

        # Skip whitespaces
        self._skip_whitespaces()

        # Determine which token type is being parsed
        next_char = self._get_next_char()
        if next_char in string.digits:
            # Next token is a integerConstant
            full_expression = next_char + self._get_next_sequence(string.digits)
            return Token(full_expression, 'integerConstant')

        elif next_char in string.ascii_letters or next_char == '_':
            # Next token is an identifier or a keyword
            full_expression = next_char + self._get_next_sequence(IDENTIFIER_ALLOWED_CHARS)
            if full_expression in KEYWORDS:
                return Token(full_expression, 'keyword')
            else:
                return Token(full_expression, 'identifier')

        elif next_char == '"':
            # Next token is a stringConstant
            full_expression = ''
            next_char = self._get_next_char()
            while next_char != '"':
                if next_char == '\n':
                    raise UnterminatedStringError(self.position)

                full_expression += next_char
                next_char = self._get_next_char()

            return Token(full_expression, 'stringConstant')

        elif next_char in SYMBOLS:
            # Next token is a symbol
            return Token(next_char, 'symbol')

        else:
            # next_char cannot start any valid token
            raise UnexpectedCharacterError(next_char, self.position)

    def eat(self, value: str, token_type: str = None) -> None:
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
    def position(self) -> Mapping[str, int]:
        """Returns the current position"""
        return self._position.copy()

    @property
    def line(self) -> int:
        """Return the current line"""
        return self._position["line"]

    @property
    def column(self) -> int:
        """Return the current column"""
        return self._position["column"]

    @property
    def finished(self) -> bool:
        """Returns whether we finished parsing all code, or there are more tokens to parse."""
        self._skip_whitespaces()
        return self._content == ''


class TokenParseError(Exception):
    def __init__(self, description: str, line: int, column: int):
        super().__init__(f'Parse error at line {line}, column {column}: {description}')


class EndOfFileError(TokenParseError):
    def __init__(self, position: Mapping[str, int]):
        super().__init__("End Of File reached", position['line'], position['column'])


class UnterminatedStringError(TokenParseError):
    def __init__(self, position: Mapping[str, int]):
        super().__init__('Unterminated string', position['last_line'], position['last_column'])


class TokenTypeError(TokenParseError):
    def __init__(self, expected: str, got: str, position: Mapping[str, int]):
        super().__init__(f"Expected {expected} and got \"{got}\"", position['line'], position['column'])


class TokenValueError(TokenParseError):
    def __init__(self, expected: str, got: str, position: Mapping[str, int]):
        super().__init__(f"Expected \"{expected}\" and got \"{got}\"", position['last_line'], position['last_column'])


class UnexpectedCharacterError(TokenParseError):
    def __init__(self, char: str, position: Mapping[str, int]):
        super().__init__(f"Unxpected character: {repr(char)}", position['line'], position['column'])
