from typing import Mapping
from .Variable import Variable, Static, Field, This
from .JackSubroutine import JackSubroutine, JackConstructor, JackFunction, JackMethod
from itertools import chain


class JackClass:
    _name: str
    _statics: Mapping[str, Static]
    _fields: Mapping[str, Field]
    _this: This

    def __init__(self, name: str):
        self._name = name
        self._statics = {}
        self._fields = {}
        self._subroutines = []
        self._this = This('this', name, 0)

    def __getitem__(self, key) -> Variable:
        """Return a static variable or a field variable that was added before"""
        if key == 'this':
            return self._this
        elif key in self._statics:
            return self._statics[key]
        elif key in self._fields:
            return self._fields[key]
        else:
            raise KeyError(f'{key} was not defined in this class')

    def __iter__(self):
        """Iterate over all variable names in scope"""
        return iter(chain(self._fields, self._statics))

    @property
    def name(self):
        return self._name

    def add_static(self, name: str, var_type: str) -> None:
        """Add a static variable to the class"""
        if name in self._statics or name in self._fields:
            raise ValueError(f'{name} was already defined')

        self._statics[name] = Static(name, var_type, len(self._statics))

    def add_field(self, name: str, var_type: str) -> None:
        """Add a field variable to the class"""
        if name in self._statics or name in self._fields:
            raise ValueError(f'{name} was already defined')

        self._fields[name] = Field(name, var_type, len(self._fields))

    def add_variable(self, kind: str, name: str, var_type: str) -> None:
        """Add a static/field variable to the class"""
        if kind == 'field':
            self.add_field(name, var_type)
        else:
            assert(kind == 'static')
            self.add_static(name, var_type)

    def create_subroutine(self, kind: str, name: str, return_type: str) -> JackSubroutine:
        if kind == 'constructor':
            subroutine = JackConstructor(name, return_type, self)

        elif kind == 'function':
            subroutine = JackFunction(name, return_type, self)

        else:
            assert(kind == 'method')
            subroutine = JackMethod(name, return_type, self)

        self._subroutines.append(subroutine)
        return subroutine

    def generate_vm_code(self) -> str:
        subroutines_code = ['\n'.join(subroutine.generate_vm_code()) for subroutine in self._subroutines]
        return '\n'.join(subroutines_code)
