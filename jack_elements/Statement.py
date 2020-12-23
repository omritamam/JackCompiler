from .Expression import Expression, SubroutineCallTerm, VariableTerm
from typing import Sequence, Union


class Statement:
    def generate_vm_code(self):
        raise NotImplementedError


class IfStatement(Statement):
    _condition: Expression
    _true_statements: Sequence[Statement]
    _false_statements: Union[None, Sequence[Statement]]

    def __repr__(self):
        if self._false_statements is None:
            return f'if ({self._condition}) {{...}}'
        else:
            return f'if ({self._condition}) {{...}} else {{...}}'

    def __init__(self, condition: Expression, true_statements: Sequence[Statement],
                 false_statements: Union[Sequence[Statement], None] = None):
        super().__init__()
        self._condition = condition
        self._true_statements = true_statements
        self._false_statements = false_statements

    def generate_vm_code(self, statement_indicator: str):
        raise NotImplementedError


class LetStatement(Statement):
    _variable_term: VariableTerm
    _value: Expression

    def __repr__(self):
        return f'let {self._variable_term} = {self._value}'

    def __init__(self, variable_term: VariableTerm, value: Expression):
        super().__init__()
        self._variable_term = variable_term
        self._value = value


class WhileStatement(Statement):
    _condition: Expression
    _statements: Sequence[Statement]

    def __repr__(self):
        return f'while ({self._condition}) {{...}}'

    def __init__(self, condition: Expression, statements: Sequence[Statement]):
        super().__init__()
        self._condition = condition
        self._statements = statements


class DoStatement(Statement):
    _call_term: SubroutineCallTerm

    def __repr__(self):
        return f'do {self._call_term}'

    def __init__(self, call_term: SubroutineCallTerm):
        super().__init__()
        self._call_term = call_term


class ReturnStatement(Statement):
    _expression: Expression

    def __repr__(self):
        if self._expression is None:
            return 'return'
        else:
            return f'return {self._expression}'

    def __init__(self, expression: Expression):
        super().__init__()
        self._expression = expression
