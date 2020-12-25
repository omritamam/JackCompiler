from .Expression import Expression, SubroutineCallTerm, VariableTerm
from typing import Sequence, Union
from itertools import chain


class Statement:
    def generate_vm_code(self, statement_indicator: str):
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
        # Create lists of generated statements
        true_statements = list(chain(*[statement.generate_vm_code(f'{statement_indicator}.T{i}')
                                       for i, statement in enumerate(self._true_statements)]))
        if self._false_statements is None:
            false_statements = list()
        else:
            false_statements = list(chain(*[statement.generate_vm_code(f'{statement_indicator}.F{i}')
                                            for i, statement in enumerate(self._false_statements)]))

        # Fill condition, false_statements, true_statements in the if-template
        lines = [
            *self._condition.generate_vm_code(),
            f'if-goto IF_TRUE{statement_indicator}',
            *false_statements,
            f'goto IF_END{statement_indicator}',
            f'label IF_TRUE{statement_indicator}',
            *true_statements,
            f'label IF_END{statement_indicator}'
        ]

        return lines


class LetStatement(Statement):
    _variable_term: VariableTerm
    _value: Expression

    def __repr__(self):
        return f'let {self._variable_term} = {self._value}'

    def __init__(self, variable_term: VariableTerm, value: Expression):
        super().__init__()
        self._variable_term = variable_term
        self._value = value

    def generate_vm_code(self, statement_indicator: str):
        return [
            # Push the evaluated expression to the stack
            *self._value.generate_vm_code(),

            # Pop it to that variable
            *self._variable_term.generate_vm_set_code()
        ]


class WhileStatement(Statement):
    _condition: Expression
    _statements: Sequence[Statement]

    def __repr__(self):
        return f'while ({self._condition}) {{...}}'

    def __init__(self, condition: Expression, statements: Sequence[Statement]):
        super().__init__()
        self._condition = condition
        self._statements = statements

    def generate_vm_code(self, statement_indicator: str):
        # Create lists of generated statements
        statements = list(chain(*[statement.generate_vm_code(f'{statement_indicator}.{i}')
                                  for i, statement in enumerate(self._statements)]))

        # Fill condition and statements in the while-template
        lines = [
            f'label LOOP{statement_indicator}',
            *self._condition.generate_vm_code(),
            'not',
            f'if-goto LOOP_END{statement_indicator}',
            *statements,
            f'goto LOOP{statement_indicator}',
            f'label LOOP_END{statement_indicator}'
        ]

        return lines


class DoStatement(Statement):
    _call_term: SubroutineCallTerm

    def __repr__(self):
        return f'do {self._call_term}'

    def __init__(self, call_term: SubroutineCallTerm):
        super().__init__()
        self._call_term = call_term

    def generate_vm_code(self, statement_indicator: str):
        # Evaluate the call term, and then dump its result
        return [
            *self._call_term.generate_vm_code(),
            'pop temp 0'
        ]


class ReturnStatement(Statement):
    _expression: Union[Expression, None]

    def __repr__(self):
        if self._expression is None:
            return 'return'
        else:
            return f'return {self._expression}'

    def __init__(self, expression: Union[Expression, None]):
        super().__init__()
        self._expression = expression

    def generate_vm_code(self, statement_indicator: str):
        # Push the return value and return
        if self._expression is None:
            return [
                'push constant 0',
                'return'
            ]
        else:
            return [
                *self._expression.generate_vm_code(),
                'return'
            ]
