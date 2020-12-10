from .token import Token
from typing import Union, Sequence, Mapping, Callable


class Lexer:
    _content: str
    _computed: Sequence
    _position: Mapping[str, int]

    def __init__(self, content):
        self._content = content
        self._computed = []
        self._position = {
            'line': 0,
            'column': 0
        }

    def next(self, token_type: Union[None, str] = None) -> Token:
        if self._computed:
            return self._computed.pop()

        # Parse next token
        return Token('haha', 'haha')

    def eat(self, value, token_type=None):
        next_token = self.next(token_type)

        if not next_token.value == value:
            raise TokenTypeError(value, next_token.value, self.position)

    def peek(self):
        next_token = self.next()
        self._computed.insert(0, next_token)
        return next_token

    @property
    def position(self):
        return self._position.copy()

    @property
    def finished(self):
        return True


class TokenParseError(Exception):
    def __init__(self, description, position):
        super().__init__(f'Parse error at line {position["line"]}, column {position["column"]}: {description}')


class TokenTypeError(TokenParseError):
    def __init__(self, expected, got, position):
        super().__init__(f"Expected {expected} and got \"{got}\"", position)


class TokenValueError(TokenParseError):
    def __init__(self, expected, got, position):
        super().__init__(f"Expected \"{expected}\" and got \"{got}\"", position)
