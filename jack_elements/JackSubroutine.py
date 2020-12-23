from .Variable import Local, Argument
from .Statement import Statement
from typing import Mapping, Sequence
from itertools import chain


class JackSubroutine:
    _name: str
    _return_type: str
    _arguments: Mapping[str, Argument]
    _locals: Mapping[str, Local]
    _statements: Sequence[Statement]

    def __init__(self, name: str, return_type: str, jack_class):
        self._name = name
        self._jack_class = jack_class
        self._return_type = return_type
        self._arguments = {}
        self._locals = {}
        self._statements = []

    def __repr__(self):
        arguments = ", ".join(f"{argument.type} {argument.name}" for argument in self._arguments.values())
        return f'{self._return_type} {self._name}({arguments})'

    def __getitem__(self, key):
        """Return a symbol in the function's scope"""
        if key in self._arguments:
            return self._arguments[key]
        elif key in self._locals:
            return self._locals[key]
        else:
            return self._jack_class[key]

    def __iter__(self):
        """Iterate over all variable names in scope"""
        return iter(chain(self._arguments, self._locals, self._jack_class))

    def add_argument(self, name: str, var_type: str) -> None:
        """Add a argument variable to the class"""
        if name in self._arguments or name in self._locals:
            raise ValueError(f'{name} was already defined')

        self._arguments[name] = Argument(name, var_type, len(self._arguments))

    def add_local(self, name: str, var_type: str) -> None:
        """Add a local variable to the class"""
        if name in self._arguments or name in self._locals:
            raise ValueError(f'{name} was already defined')

        self._locals[name] = Local(name, var_type, len(self._locals))

    def add_statements(self, statements: Sequence[Statement]):
        """Add a sequence of parsed statements to the subroutine's statements"""
        self._statements.extend(statements)

    def generate_vm_code(self) -> list[str]:
        lines = [
            f'function {self._jack_class.name}.{self._name} {len(self._locals)}',
            *self._PROLOGUE,
        ]

        for i, statement in enumerate(self._statements):
            lines.extend(statement.generate_vm_code(str(i)))

        return lines


class JackConstructor(JackSubroutine):
    @property
    def _PROLOGUE(self) -> str:
        lines = [
            f'push constant {len(self._jack_class._fields)}',
            'call Memory.alloc 1',
            'pop pointer 0'
        ]

        return lines


class JackFunction(JackSubroutine):
    _PROLOGUE = []


class JackMethod(JackSubroutine):
    _PROLOGUE = [
        'push argument 0',
        'pop pointer 0'
    ]

    def __init__(self, name: str, return_type: str, jack_class):
        super().__init__(name, return_type, jack_class)

        # We need to add a dummy argument instead of this (because this was pushed as an argument),
        # so the indexing to the other arguments will be correct
        self.add_argument('', '')
