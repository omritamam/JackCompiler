from typing import Mapping


class SymbolTable:
    _class_scope_table: Mapping[str, str]
    _subroutine_scope_table: Mapping[str, str]
    _varCounter: Mapping[str, int]

    def __init__(self):
        self._class_scope_table = {}
        self._varCounter = {"static": 0, "field": 0, "argument": 0, "var": 0}
        self._subroutine_scope_table = {}

    def reset_subroutine(self):
        self._subroutine_scope_table = {}
        self._varCounter["var"] = 0
        self._varCounter["argument"] = 0

    def define(self, name: str, type: str, kind: str):
        if kind in ("static", "field"):
            table = self._class_scope_table
        else:
            table = self.subroutine_scope_table
        table[name] = {"type": type, "kind": kind, "index": self.varCount(kind)}

    def varCount(self, kind: str):
        if kind not in ("static", "field", "argument", "var"):
            raise Exception("unknown kind: " + kind)
        val = self._varCounter[kind]
        self._varCounter[kind] += 1
        return val

    def typeOf(self, name: str):
        if name in self._class_scope_table:
            return self._class_scope_table[name]["type"]

        elif name in self._subroutine_scope_table:
            return self._subroutine_scope_table[name]["type"]

        else:
            raise Exception("undefined indefier")

    def indexOf(self, name: str):
        if name in self._class_scope_table:
            return self._class_scope_table[name]["index"]

        elif name in self._subroutine_scope_table:
            return self._subroutine_scope_table[name]["index"]

        else:
            raise Exception("undefined indefier")
