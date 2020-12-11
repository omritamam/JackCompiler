class Token:
    def __init__(self, value, token_type):
        self._value = value
        self._type = token_type

    @property
    def value(self):
        """The value of the token"""
        return self._value

    @property
    def type(self):
        """The type of the token"""
        return self._type
