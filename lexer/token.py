class Token:
    def __init__(self, value, token_type):
        self._value = value
        self._type = token_type

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type
