from typing import NamedTuple


class Variable(NamedTuple):
    name: str
    type: str
    index: int

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
