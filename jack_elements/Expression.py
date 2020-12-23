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
        self._subroutine_name = subroutine_name
        self._expressions = expressions[:]


class IntegerConstant(Term):
    _value: int

    def __repr__(self):
        return f'{self._value}'

    def __init__(self, value: int):
        super().__init__()
        self._value = value


class StringConstant(Term):
    _value: str

    def __repr__(self):
        return f'{self._value}'

    def __init__(self, value: str):
        super().__init__()
        self._value = value


class KeywordConstant(Term):
    _value: str

    def __repr__(self):
        return f'{self._value}'

    def __init__(self, value: str):
        super().__init__()

        assert(value in ('true', 'false', 'null', 'this'))
        self._value = value


class VariableTerm(Term):
    _variable: Variable
    _offset: Expression

    def __repr__(self):
        if self._offset is None:
            return f'{self._variable}'
        else:
            return f'{self._variable}[{self._offset}]'

    def __init__(self, variable: Variable, offset: Expression):
        super().__init__()
        self._variable = variable
        self._offset = offset


class BracketsTerm(Term):
    _expression: Expression

    def __repr__(self):
        return f'({self._expression})'

    def __init__(self, expression: Expression):
        super().__init__()
        self._expression = expression


class BinaryOperation(Expression):
    _first_expression: Expression
    _second_expression: Expression

    OP = '?'

    def __repr__(self):
        return f'{self._first_expression} {self.OP} {self._second_expression}'

    def __init__(self, first_expression: Expression, second_expression: Expression):
        super().__init__()
        self._first_expression = first_expression
        self._second_expression = second_expression


class UnaryOperation(Term):
    _expression: Expression

    OP = '?'

    def __repr__(self):
        return f'{self.OP}{self._expression}'

    def __init__(self, expression: Expression):
        super().__init__()
        self._expression = expression


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


class SubstractExpression(IntegerBinaryOperation):
    OP = '-'


class MultiplyExpression(IntegerBinaryOperation):
    OP = '*'


class DivideExpression(IntegerBinaryOperation):
    OP = '/'


class AndExpression(BooleanBinaryOperation):
    OP = '&'


class OrExpression(BooleanBinaryOperation):
    OP = '|'


class LessThanExpression(BooleanBinaryOperation):
    OP = '<'


class EqualExpression(BooleanBinaryOperation):
    OP = '='


class GreaterThanExpression(BooleanBinaryOperation):
    OP = '>'


class NegateTerm(IntegerUnaryOperation):
    OP = '-'


class NotTerm(BooleanUnaryOperation):
    OP = '~'
