class Token:
    def __init__(self, value, token_type, position):
        self._value = value
        self._type = token_type
        self._position = position

    @property
    def value(self):
        """The value of the token"""
        return self._value

    @property
    def type(self):
        """The type of the token"""
        return self._type

    @property
    def position(self):
        """The position that the token was defined"""
        return self._position.copy()
