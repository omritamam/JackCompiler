from .Variable import Variable
from typing import Sequence


class Expression:
    pass


class Term(Expression):
    pass


class SubroutineCallTerm(Term):
    _subroutine_name: str
    _expressions: Sequence[Expression]

    def __repr__(self):
        return f'{self._subroutine_name}({", ".join(str(exp) for exp in self._expressions)})'

    def __init__(self, subroutine_name: str, expressions: Sequence[Expression]):
        super().__init__()
        self._subroutine_name = subroutine_name
        self._expressions = expressions[:]

    def generate_vm_code(self) -> list[str]:
        lines = []
        for expression in self._expressions:
            # Push the expression to the stack
            lines.extend(expression.generate_vm_code())

        # Append the call line
        lines.append(
            f'call {self._subroutine_name} {len(self._expressions)}'
        )

        return lines


class IntegerConstant(Term):
    _value: int

    def __repr__(self):
        return f'{self._value}'

    def __init__(self, value: int):
        super().__init__()
        self._value = value

    def generate_vm_code(self) -> list[str]:
        return [f'push constant {self._value}']


class StringConstant(Term):
    _value: str

    def __repr__(self):
        return f'{self._value}'

    def __init__(self, value: str):
        super().__init__()
        self._value = value

    def generate_vm_code(self) -> list[str]:
        lines = [
            # Allocate string
            f'push constant {len(self._value)}',
            'call String.new 1'
        ]

        for char in self._value:
            lines.extend([
                # String was alread pushed to the stack
                f'push constant {ord(char)}',
                'call String.appendChar 2',
                # No need to pop return value, it is our string
            ])

        # Generated string is already in the stack, no need to push anything
        return lines


class KeywordConstant(Term):
    _value: str

    def __repr__(self):
        return f'{self._value}'

    def __init__(self, value: str):
        super().__init__()

        assert(value in ('true', 'false', 'null'))
        self._value = value

    def generate_vm_code(self) -> list[str]:
        if self._value == 'true':
            return [
                'push constant 1',
                'neg'
            ]
        else:
            assert(self._value in ('false', 'null'))
            return ['push constant 0']


class VariableTerm(Term):
    _variable: Variable
    _offset: Expression

    def __repr__(self):
        if self._offset is None:
            return f'{self._variable}'
        else:
            return f'{self._variable}[{self._offset}]'

    def __init__(self, variable: Variable, offset: Expression = None):
        super().__init__()
        self._variable = variable
        self._offset = offset

    def generate_vm_set_code(self) -> list[str]:
        if self._offset is None:
            return [f'pop {self._variable.VM_SEGMENT} {self._variable.index}']

        else:
            return [
                # Add offset to variable value
                f'push {self._variable.VM_SEGMENT} {self._variable.index}',
                *self._offset.generate_vm_code(),
                'add',

                # Set that to point to the result
                'pop pointer 1',

                # Pop that 0
                'pop that 0'
            ]

    def generate_vm_code(self) -> list[str]:
        lines = [f'push {self._variable.VM_SEGMENT} {self._variable.index}']

        if self._offset is not None:
            lines.extend([
                # Add offset to variable value
                *self._offset.generate_vm_code(),
                'add',

                # Set that to point to the result
                'pop pointer 1',

                # Push that 0
                'push that 0'
            ])

        return lines


class BracketsTerm(Term):
    _expression: Expression

    def __repr__(self):
        return f'({self._expression})'

    def __init__(self, expression: Expression):
        super().__init__()
        self._expression = expression

    def generate_vm_code(self) -> list[str]:
        return self._expression.generate_vm_code()


class BinaryOperation(Expression):
    _first_expression: Expression
    _second_expression: Expression

    OP = '?'
    INSTRUCTION = 'inst'

    def __repr__(self):
        return f'{self._first_expression} {self.OP} {self._second_expression}'

    def __init__(self, first_expression: Expression, second_expression: Expression):
        super().__init__()
        self._first_expression = first_expression
        self._second_expression = second_expression

    def generate_vm_code(self) -> list[str]:
        return [
            *self._first_expression.generate_vm_code(),
            *self._second_expression.generate_vm_code(),
            self.INSTRUCTION
        ]


class UnaryOperation(Term):
    _expression: Expression

    OP = '?'
    INSTRUCTION = 'inst'

    def __repr__(self):
        return f'{self.OP}{self._expression}'

    def __init__(self, expression: Expression):
        super().__init__()
        self._expression = expression

    def generate_vm_code(self) -> list[str]:
        return [
            *self._expression.generate_vm_code(),
            self.INSTRUCTION
        ]


class IntegerBinaryOperation(BinaryOperation):
    pass


class BooleanBinaryOperation(BinaryOperation):
    pass


class IntegerUnaryOperation(UnaryOperation):
    pass


class BooleanUnaryOperation(UnaryOperation):
    pass


class AddExpression(IntegerBinaryOperation):
    OP = '+'
    INSTRUCTION = 'add'


class SubstractExpression(IntegerBinaryOperation):
    OP = '-'
    INSTRUCTION = 'sub'


class MultiplyExpression(IntegerBinaryOperation):
    OP = '*'
    INSTRUCTION = 'call Math.multiply 2'


class DivideExpression(IntegerBinaryOperation):
    OP = '/'
    INSTRUCTION = 'call Math.divide 2'


class AndExpression(BooleanBinaryOperation):
    OP = '&'
    INSTRUCTION = 'and'


class OrExpression(BooleanBinaryOperation):
    OP = '|'
    INSTRUCTION = 'or'


class LessThanExpression(BooleanBinaryOperation):
    OP = '<'
    INSTRUCTION = 'lt'


class EqualExpression(BooleanBinaryOperation):
    OP = '='
    INSTRUCTION = 'eq'


class GreaterThanExpression(BooleanBinaryOperation):
    OP = '>'
    INSTRUCTION = 'gt'


class NegateTerm(IntegerUnaryOperation):
    OP = '-'
    INSTRUCTION = 'neg'


class NotTerm(BooleanUnaryOperation):
    OP = '~'
    INSTRUCTION = 'not'
