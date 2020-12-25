from lexer import Lexer, Token, TokenValueError, TokenTypeError, TokenParseError
from typing import TextIO, Union, Sequence
from jack_elements import JackClass, JackSubroutine, Statement, LetStatement, \
                            IfStatement, WhileStatement, DoStatement, ReturnStatement, \
                            Expression, Term, SubroutineCallTerm, AddExpression, SubstractExpression, \
                            MultiplyExpression, DivideExpression, AndExpression, OrExpression, \
                            LessThanExpression, GreaterThanExpression, EqualExpression, \
                            NegateTerm, NotTerm, IntegerConstant, StringConstant, \
                            KeywordConstant, VariableTerm, BracketsTerm

import os


BINARY_OPERATIONS = {
    '+': AddExpression,
    '-': SubstractExpression,
    '*': MultiplyExpression,
    '/': DivideExpression,
    '&': AndExpression,
    '|': OrExpression,
    '<': LessThanExpression,
    '>': GreaterThanExpression,
    '=': EqualExpression
}

UNARY_OPERATIONS = {
    '-': NegateTerm,
    '~': NotTerm
}


class JackVmCompiler:
    """
    A compiler that compiles jack into XML hierarchy.
    """
    _writer: TextIO
    _lexer: Lexer
    _current_line: str

    def __init__(self, content: str, output_file: TextIO):
        self._writer = output_file
        self._lexer = Lexer(content)
        self._current_line = ''

    def compile(self) -> None:
        parsed_class = self._parse_class()
        if not self._lexer.finished:
            next_token = self._lexer.next()
            raise TokenTypeError('EOF', next_token.value, next_token.position)

        if parsed_class.name != os.path.splitext(os.path.basename(self._writer.name))[0]:
            raise TokenParseError("Class name doesn't match file name", 0, 0)

        self._writer.write(parsed_class.generate_vm_code())

    def _next(self) -> Token:
        token = self._lexer.next()
        self._current_line += token.value
        return token

    def _eat(self, value: Union[str, Sequence]) -> None:
        """
        Pops the next parsed token and verify it matches to the given value or value sequence.
        """
        token = self._next()
        if isinstance(value, str) and token.value != value:
            raise TokenValueError(value, token.value, token.position)

        elif (token.value not in value):
            # Value is a Sequence
            raise TokenValueError(' | '.join(value), token.value, token.position)

    def _read_identifier(self) -> str:
        """Read an identifier as the next token"""
        token = self._next()
        if token.type != 'identifier':
            raise TokenTypeError('identifier', token.value, token.position)

        return token.value

    def _is_type(self, token: Token) -> bool:
        if token.type == 'identifier':
            return True
        elif token.type == 'keyword' and token.value in ('int', 'char', 'boolean'):
            return True
        else:
            return False

    def _read_type(self) -> str:
        """Read an identifier and write it to the xml output"""
        token = self._next()
        if not self._is_type(token):
            # Token is not a valid type
            raise TokenTypeError('type', token.value, token.position)

        return token.value

    def _read_subroutine_return_type(self) -> str:
        if self._lexer.peek().value == 'void':
            return self._next().value
        else:
            return self._read_type()

    def _parse_subroutine_call_term(self, subroutine: JackSubroutine) -> SubroutineCallTerm:
        # Grammar for subroutineCall:
        #   subroutineName '(' expressionList ')' |
        #   (className | varName) '.' subroutineName '(' expressionList ')'
        # Where expressionList grammar is defined as this:
        #   (expression (',' expression)*)?
        first_identifier = self._read_identifier()
        if self._lexer.peek().value == '.':
            self._eat('.')
            if first_identifier in subroutine:
                # User asked to call a method of a given variable
                this = subroutine[first_identifier]
                class_name = this.type

            else:
                # User asked to call a function or a constructor
                this = None
                class_name = first_identifier

            subroutine_name = self._read_identifier()

        else:
            # User asked to call a method of this.
            this = subroutine['this']
            class_name = this.type
            subroutine_name = first_identifier

        expressions: list[Expression]
        if this is None:
            expressions = []
        else:
            expressions = [VariableTerm(this)]

        self._eat('(')

        if self._lexer.peek().value != ')':
            expressions.append(self._parse_expression(subroutine))
            while self._lexer.peek().value != ')':
                self._eat(',')
                expressions.append(self._parse_expression(subroutine))

        self._eat(')')

        return SubroutineCallTerm(f'{class_name}.{subroutine_name}', expressions)

    def _parse_constant_term(self, subroutine: JackSubroutine) -> Term:
        term_token = self._next()
        if term_token.type == 'integerConstant':
            return IntegerConstant(int(term_token.value))
        elif term_token.type == 'stringConstant':
            return StringConstant(term_token.value)

        assert(term_token.type == 'keyword')
        if term_token.value == 'this':
            return VariableTerm(subroutine['this'])

        if term_token.value not in ('true', 'false', 'null'):
            raise TokenTypeError('term', term_token.value, term_token.position)

        return KeywordConstant(term_token.value)

    def _parse_variable_term(self, subroutine: JackSubroutine) -> VariableTerm:
        variable = subroutine[self._read_identifier()]

        if self._lexer.peek().value == '[':
            self._eat('[')
            offset = self._parse_expression(subroutine)
            self._eat(']')
        else:
            offset = None

        return VariableTerm(variable, offset)

    def _parse_term(self, subroutine: JackSubroutine) -> Term:
        # Grammar for term:
        #   integerConstant|stringConstant|keywordConstant|varName|varName '[' expression ']'|
        #   subroutineCall|'(' expression ')'|unaryOp term
        term_token = self._lexer.peek()
        if term_token.type in ('integerConstant', 'stringConstant', 'keyword'):
            return self._parse_constant_term(subroutine)

        elif term_token.type == 'identifier':
            # Can be one of the following:
            #   varName
            #   varName '[' expression ']'
            #   subroutineCall, which can be:
            #       subroutineName '(' expressionList ')'
            #       (className|varName) '.' subroutineName '(' expressionList ')'
            after_identifier_token = self._lexer.peek(2)
            if after_identifier_token.value in ('(', '.'):
                return self._parse_subroutine_call_term(subroutine)
            else:
                return self._parse_variable_term(subroutine)

        elif term_token.value in UNARY_OPERATIONS:
            term_token = self._next()
            operation = UNARY_OPERATIONS[term_token.value]
            inner = self._parse_term(subroutine)
            return operation(inner)

        elif term_token.value == '(':
            self._eat('(')
            expression = self._parse_expression(subroutine)
            self._eat(')')

            return BracketsTerm(expression)

        else:
            raise TokenTypeError('term', term_token.value, term_token.position)

    def _parse_expression(self, subroutine: JackSubroutine) -> Expression:
        current_expression = self._parse_term(subroutine)
        while self._lexer.peek().value in BINARY_OPERATIONS:
            operation_type = BINARY_OPERATIONS[self._next().value]
            next_term = self._parse_term(subroutine)
            current_expression = operation_type(current_expression, next_term)

        return current_expression

    def _parse_let_statement(self, subroutine: JackSubroutine) -> LetStatement:
        # Grammar for a letStatement:
        #   'let' varName ('[' expression ']')? '=' expression ';'
        self._eat('let')

        variable_term = self._parse_variable_term(subroutine)

        self._eat('=')
        value = self._parse_expression(subroutine)
        self._eat(';')

        return LetStatement(variable_term, value)

    def _parse_if_statement(self, subroutine: JackSubroutine) -> IfStatement:
        # Grammar for an ifStatement:
        #   'if '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self._eat('if')
        self._eat('(')

        condition = self._parse_expression(subroutine)
        # TODO: Verify that condition is boolean

        self._eat(')')
        self._eat('{')
        true_statements = self._parse_statements(subroutine)
        self._eat('}')

        if self._lexer.peek().value == 'else':
            # Handle else case
            self._eat('else')
            self._eat('{')
            false_statements = self._parse_statements(subroutine)
            self._eat('}')

        else:
            false_statements = None

        return IfStatement(condition, true_statements, false_statements)

    def _parse_while_statement(self, subroutine: JackSubroutine) -> WhileStatement:
        # Grammar for a whileStatement:
        #   'while' '(' expression ')' '{' statements '}'
        self._eat('while')
        self._eat('(')
        condition = self._parse_expression(subroutine)
        self._eat(')')
        self._eat('{')
        statements = self._parse_statements(subroutine)
        self._eat('}')

        return WhileStatement(condition, statements)

    def _parse_do_statement(self, subroutine: JackSubroutine) -> DoStatement:
        # Grammar for a doStatement:
        #   'do' subroutineCall ';'
        self._eat('do')
        call_term = self._parse_subroutine_call_term(subroutine)
        self._eat(';')

        return DoStatement(call_term)

    def _parse_return_statement(self, subroutine: JackSubroutine) -> ReturnStatement:
        # Grammar for a returnStatement:
        #   'return' expression? ';'
        self._eat('return')
        if self._lexer.peek().value != ';':
            expression = self._parse_expression(subroutine)

        else:
            expression = None

        # TODO: Verify that the expression type matches the given expression

        self._eat(';')

        return ReturnStatement(expression)

    def _parse_statement(self, subroutine: JackSubroutine) -> Statement:
        statement_token = self._lexer.peek()
        if statement_token.value == 'let':
            return self._parse_let_statement(subroutine)

        elif statement_token.value == 'if':
            return self._parse_if_statement(subroutine)

        elif statement_token.value == 'while':
            return self._parse_while_statement(subroutine)

        elif statement_token.value == 'do':
            return self._parse_do_statement(subroutine)

        elif statement_token.value == 'return':
            return self._parse_return_statement(subroutine)

        else:
            # Parsed token is not a valid statement
            raise TokenTypeError('statement', statement_token.value, statement_token.position)

    def _parse_statements(self, subroutine: JackSubroutine) -> Sequence[Statement]:
        output = []
        while self._lexer.peek().value in ('let', 'if', 'while', 'do', 'return'):
            output.append(self._parse_statement(subroutine))

        return output

    def _parse_subroutine_body(self, subroutine) -> None:
        # Grammar for subroutineBody:
        #   '{' varDec* statements '}'
        self._eat('{')
        while self._lexer.peek().value == 'var':
            # Grammar for varDec:
            #   'var' type varName (',' varName)* ';'
            self._eat('var')

            variable_type = self._read_type()
            variable_name = self._read_identifier()
            subroutine.add_local(variable_name, variable_type)

            while self._lexer.peek().value == ',':
                self._eat(',')
                variable_name = self._read_identifier()
                subroutine.add_local(variable_name, variable_type)

            self._eat(';')

        subroutine.add_statements(self._parse_statements(subroutine))
        self._eat('}')

    def _add_argument(self, subroutine: JackSubroutine) -> None:
        argument_type = self._read_type()
        argument_name = self._read_identifier()
        subroutine.add_argument(argument_name, argument_type)

    def _parse_class_subroutines(self, jack_class: JackClass) -> None:
        while self._lexer.peek().value in ('constructor', 'function', 'method'):
            # Grammar for a subroutineDec is:
            #   ('constructor'|'function'|'method') ('void'|type) subroutineName '('
            #   parameterList ')' subroutineBody
            # Where subroutineName is an identifier

            # Create the subroutine
            subroutine_kind = self._next().value
            subroutine_return_type = self._read_subroutine_return_type()
            subroutine_name = self._read_identifier()
            subroutine = jack_class.create_subroutine(subroutine_kind, subroutine_name, subroutine_return_type)

            # Add all arguments
            self._eat('(')

            # Grammar for a parameterList is:
            #   (type varName (',' type varName)*)?
            # Where varName is an identifier
            if ')' != self._lexer.peek().value:
                self._add_argument(subroutine)
                while self._lexer.peek().value == ',':
                    self._eat(',')
                    self._add_argument(subroutine)

            self._eat(')')

            # Parse its body
            self._parse_subroutine_body(subroutine)

    def _parse_class_variables(self, jack_class: JackClass) -> None:
        """Parse all class variables"""
        while self._lexer.peek().value in ('field', 'static'):
            # Grammar for a classVarDec is:
            #   ('static'|'field') type varName (',' varName)* ';'
            # Where varName is an identifier
            variable_kind_token = self._next()
            variable_type = self._read_type()
            variable_name = self._read_identifier()

            jack_class.add_variable(variable_kind_token.value, variable_name, variable_type)

            while self._lexer.peek().value == ',':
                self._eat(',')
                variable_name = self._read_identifier()
                jack_class.add_variable(variable_kind_token.value, variable_name, variable_type)

            self._eat(';')

    def _parse_class(self) -> JackClass:
        """Parses a class"""
        # Define a jack class
        self._eat('class')
        class_name = self._read_identifier()
        jack_class = JackClass(class_name)

        self._eat('{')

        self._parse_class_variables(jack_class)
        self._parse_class_subroutines(jack_class)

        self._eat('}')

        return jack_class
