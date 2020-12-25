class Variable:
    _name: str
    _type: str
    _index: int
    VM_SEGMENT: str

    def __init__(self, name: str, type: str, index: int):
        self._name = name
        self._type = type
        self._index = index

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def index(self):
        return self._index

    def __str__(self):
        return f'{self.name}'

    @property
    def _vm_reference(self):
        return f'{self.VM_SEGMENT} {self.index}'

    def push(self):
        return f'push {self._vm_reference}'

    def pop(self):
        return f'pop {self._vm_reference}'


class Field(Variable):
    VM_SEGMENT = 'this'


class Static(Variable):
    VM_SEGMENT = 'static'


class Local(Variable):
    VM_SEGMENT = 'local'


class Argument(Variable):
    VM_SEGMENT = 'argument'


class This(Variable):
    VM_SEGMENT = 'pointer'
