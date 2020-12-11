from .token import Token
from typing import Union, Sequence, Mapping


class Lexer:
    _content: str
    _computed: Sequence
    _position: Mapping[str, int]

    def __init__(self, content):
        self._content = content
        self._computed = []
        self._position = {
            'last_line': 0,
            'last_column': 0,
            'line': 0,
            'column': 0
        }

    def next(self, token_type: Union[None, str] = None) -> Token:
        """Pops the next parsed token"""
        if self._computed:
            return self._computed.pop()

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
    def position(self) -> Mapping[str, int]:
        """Returns the current position"""
        return self._position.copy()

    @property
    def finished(self) -> bool:
        """Returns whether we finished parsing all code, or there are more tokens to parse."""
        # TODO: Replace this line with a working logic to check if we finished parsing all code.
        return True


class TokenParseError(Exception):
    def __init__(self, description: str, line: int, column: int):
        super().__init__(f'Parse error at line {line}, column {column}: {description}')


class TokenTypeError(TokenParseError):
    def __init__(self, expected: str, got: str, position: Mapping[str, int]):
        super().__init__(f"Expected {expected} and got \"{got}\"", position['line'], position['column'])


class TokenValueError(TokenParseError):
    def __init__(self, expected: str, got: str, position: Mapping[str, int]):
        super().__init__(f"Expected \"{expected}\" and got \"{got}\"", position['last_line'], position['last_column'])
