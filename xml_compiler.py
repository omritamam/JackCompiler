from lexer import Lexer, Token, TokenValueError, TokenTypeError
from xml_writer import XmlWriter
from typing import TextIO, Union, Sequence


OPERATIONS = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
UNARY_OPERATIONS = {'-', '~'}


class JackXmlCompiler:
    """
    A compiler that compiles jack into XML hierarchy.
    """
    _content: str

    def __init__(self, content: str):
        self._content = content

    def compile_tokens(self, output_file: TextIO) -> None:
        """
        Compiles given file into an XML file without complex hierarchy.
        For example:

            let x=5+yy; let city="Paris";

        Turn into:

            <tokens>
                <keyword> let </keyword>
                <identifier> x </identifier>
                <symbol> = </symbol>
                <integerConstant> 5 </integerConstant>
                <symbol> + </symbol>
                <identifier> yy </identifier>
                <symbol> ; </symbol>
                <keyword> let </keyword>
                <identifier> city </identifier>
                <symbol> = </symbol>
                <stringConstant> Paris </stringConstant>
                <symbol> ; </symbol>
            </tokens>
        """
        output = XmlWriter(output_file)
        lexer = Lexer(self._content)
        with output.element('tokens'):
            while not lexer.finished:
                output.write_token(lexer.next())

    def analyze(self, output_file: TextIO) -> None:
        writer = XmlWriter(output_file)
        lexer = Lexer(self._content)

        self._compile_class(lexer, writer)
        if not lexer.finished:
            next_token = lexer.next()
            raise TokenTypeError('EOF', next_token.value, next_token.position)

    def _eat(self, lexer: Lexer, writer: XmlWriter, value: Union[str, Sequence]) -> None:
        """
        Pops the next parsed token and verify it matches to the given value or value sequence.
        """
        token = lexer.next()
        if isinstance(value, str) and token.value != value:
            raise TokenValueError(value, token.value, token.position)

        elif (token.value not in value):
            # Value is a Sequence
            raise TokenValueError(' | '.join(value), token.value, token.position)

        # Expected token was found, write it to output
        writer.write_token(token)

    def _read_identifier(self, lexer: Lexer, writer: XmlWriter) -> None:
        """Read an identifier and write it to the xml output"""
        token = lexer.next()
        if token.type != 'identifier':
            raise TokenTypeError('identifier', token.value, token.position)

        writer.write_token(token)

    def _is_type(self, token: Token) -> bool:
        if token.type == 'identifier':
            return True
        elif token.type == 'keyword' and token.value in ('int', 'char', 'boolean'):
            return True
        else:
            return False

    def _read_type(self, lexer: Lexer, writer: XmlWriter) -> None:
        """Read an identifier and write it to the xml output"""
        token = lexer.next()
        if self._is_type(token):
            writer.write_token(token)

        else:
            # Token is not a valid type
            raise TokenTypeError('type', token.value, token.position)

    def _compile_class_variables(self, lexer: Lexer, writer: XmlWriter) -> None:
        """Compile all class variables"""
        while lexer.peek().value in ('field', 'static'):
            with writer.element('classVarDec'):
                # Grammar for a classVarDec is:
                #   ('static'|'field') type varName (',' varName)* ';'
                # Where varName is an identifier
                self._eat(lexer, writer, ['static', 'field'])
                self._read_type(lexer, writer)
                self._read_identifier(lexer, writer)
                while lexer.peek().value == ',':
                    self._eat(lexer, writer, ',')
                    self._read_identifier(lexer, writer)
                self._eat(lexer, writer, ';')

    def _read_subroutine_return_type(self, lexer: Lexer, writer: XmlWriter) -> None:
        if lexer.peek().value == 'void':
            self._eat(lexer, writer, 'void')
        else:
            self._read_type(lexer, writer)

    def _compile_parameter_list(self, lexer: Lexer, writer: XmlWriter) -> None:
        # Grammar for a parameterList is:
        #   (type varName (',' type varName)*)?
        # Where varName is an identifier
        with writer.element('parameterList'):
            if self._is_type(lexer.peek()):
                self._read_type(lexer, writer)
                self._read_identifier(lexer, writer)

                while lexer.peek().value == ',':
                    self._eat(lexer, writer, ',')
                    self._read_type(lexer, writer)
                    self._read_identifier(lexer, writer)

    def _compile_term(self, lexer: Lexer, writer: XmlWriter) -> None:
        # Grammar for term:
        #   integerConstant|stringConstant|keywordConstant|varName|varName '[' expression ']'|
        #   subroutineCall|'(' expression ')'|unaryOp term
        with writer.element('term'):
            term_token = lexer.peek()
            if term_token.type in ('integerConstant', 'stringConstant', 'keyword'):
                if term_token.type == 'keyword' and term_token.value not in ('true', 'false', 'null', 'this'):
                    raise TokenTypeError('term', term_token.value, term_token.position)
                writer.write_token(lexer.next())

            elif term_token.type == 'identifier':
                # Can be one of the following:
                #   varName
                #   varName '[' expression ']'
                #   subroutineCall, which can be:
                #       subroutineName '(' expressionList ')'
                #       (className|varName) '.' subroutineName '(' expressionList ')'
                after_identifier_token = lexer.peek(2)
                if after_identifier_token.value in ('(', '.'):
                    self._read_subroutine_call(lexer, writer)
                else:
                    self._read_identifier(lexer, writer)
                    if lexer.peek().value == '[':
                        self._eat(lexer, writer, '[')
                        self._compile_expression(lexer, writer)
                        self._eat(lexer, writer, ']')

            elif term_token.value in UNARY_OPERATIONS:
                self._eat(lexer, writer, UNARY_OPERATIONS)
                self._compile_term(lexer, writer)

            elif term_token.value == '(':
                self._eat(lexer, writer, '(')
                self._compile_expression(lexer, writer)
                self._eat(lexer, writer, ')')

            else:
                raise TokenTypeError('term', term_token.value, term_token.position)

    def _compile_expression(self, lexer: Lexer, writer: XmlWriter) -> None:
        with writer.element('expression'):
            self._compile_term(lexer, writer)
            while lexer.peek().value in OPERATIONS:
                self._eat(lexer, writer, OPERATIONS)
                self._compile_term(lexer, writer)

    def _read_subroutine_call(self, lexer: Lexer, writer: XmlWriter) -> None:
        # Grammar for subroutineCall:
        #   subroutineName '(' expressionList ')' |
        #   (className | varName) '.' subroutineName '(' expressionList ')'
        # Where expressionList grammar is defined as this:
        #   (expression (',' expression)*)?
        self._read_identifier(lexer, writer)
        if lexer.peek().value == '.':
            self._eat(lexer, writer, '.')
            self._read_identifier(lexer, writer)

        self._eat(lexer, writer, '(')
        with writer.element('expressionList'):
            if lexer.peek().value != ')':
                self._compile_expression(lexer, writer)
                while lexer.peek().value != ')':
                    self._eat(lexer, writer, ',')
                    self._compile_expression(lexer, writer)

        self._eat(lexer, writer, ')')

    def _compile_statement(self, lexer: Lexer, writer: XmlWriter) -> None:
        statement_token = lexer.peek()
        if statement_token.value == 'let':
            # Grammar for a letStatement:
            #   'let' varName ('[' expression ']')? '=' expression ';'
            with writer.element('letStatement'):
                self._eat(lexer, writer, 'let')
                self._read_identifier(lexer, writer)

                if lexer.peek().value == '[':
                    # Array assignment
                    self._eat(lexer, writer, '[')
                    self._compile_expression(lexer, writer)
                    self._eat(lexer, writer, ']')

                self._eat(lexer, writer, '=')
                self._compile_expression(lexer, writer)
                self._eat(lexer, writer, ';')

        elif statement_token.value == 'if':
            # Grammar for an ifStatement:
            #   'if '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
            with writer.element('ifStatement'):
                self._eat(lexer, writer, 'if')
                self._eat(lexer, writer, '(')
                self._compile_expression(lexer, writer)
                self._eat(lexer, writer, ')')
                self._eat(lexer, writer, '{')
                self._compile_statements(lexer, writer)
                self._eat(lexer, writer, '}')

                if lexer.peek().value == 'else':
                    # Handle else case
                    self._eat(lexer, writer, 'else')
                    self._eat(lexer, writer, '{')
                    self._compile_statements(lexer, writer)
                    self._eat(lexer, writer, '}')

        elif statement_token.value == 'while':
            # Grammar for a whileStatement:
            #   'while' '(' expression ')' '{' statements '}'
            with writer.element('whileStatement'):
                self._eat(lexer, writer, 'while')
                self._eat(lexer, writer, '(')
                self._compile_expression(lexer, writer)
                self._eat(lexer, writer, ')')
                self._eat(lexer, writer, '{')
                self._compile_statements(lexer, writer)
                self._eat(lexer, writer, '}')

        elif statement_token.value == 'do':
            # Grammar for a doStatement:
            #   'do' subroutineCall ';'
            with writer.element('doStatement'):
                self._eat(lexer, writer, 'do')
                self._read_subroutine_call(lexer, writer)
                self._eat(lexer, writer, ';')

        elif statement_token.value == 'return':
            # Grammar for a returnStatement:
            #   'return' expression? ';'
            with writer.element('returnStatement'):
                self._eat(lexer, writer, 'return')
                if lexer.peek().value != ';':
                    self._compile_expression(lexer, writer)

                self._eat(lexer, writer, ';')

        else:
            # Parsed token is not a valid statement
            raise TokenTypeError('statement', statement_token.value, statement_token.position)

    def _compile_statements(self, lexer: Lexer, writer: XmlWriter) -> None:
        with writer.element('statements'):
            while lexer.peek().value in ('let', 'if', 'while', 'do', 'return'):
                self._compile_statement(lexer, writer)

    def _compile_subroutine_body(self, lexer: Lexer, writer: XmlWriter) -> None:
        with writer.element('subroutineBody'):
            # Grammar for subroutineBody:
            #   '{' varDec* statements '}'
            self._eat(lexer, writer, '{')
            while lexer.peek().value == 'var':
                with writer.element('varDec'):
                    # Grammar for varDec:
                    #   'var' type varName (',' varName)* ';'
                    self._eat(lexer, writer, 'var')
                    self._read_type(lexer, writer)
                    self._read_identifier(lexer, writer)
                    while lexer.peek().value == ',':
                        self._eat(lexer, writer, ',')
                        self._read_identifier(lexer, writer)
                    self._eat(lexer, writer, ';')

            self._compile_statements(lexer, writer)
            self._eat(lexer, writer, '}')

    def _compile_class_subroutines(self, lexer: Lexer, writer: XmlWriter) -> None:
        while lexer.peek().value in ('constructor', 'function', 'method'):
            with writer.element('subroutineDec'):
                # Grammar for a subroutineDec is:
                #   ('constructor'|'function'|'method') ('void'|type) subroutineName '('
                #   parameterList ')' subroutineBody
                # Where subroutineName is an identifier
                self._eat(lexer, writer, ['constructor', 'function', 'method'])
                self._read_subroutine_return_type(lexer, writer)
                self._read_identifier(lexer, writer)
                self._eat(lexer, writer, '(')
                self._compile_parameter_list(lexer, writer)
                self._eat(lexer, writer, ')')
                self._compile_subroutine_body(lexer, writer)

    def _compile_class(self, lexer: Lexer, writer: XmlWriter) -> None:
        """Compiles a class"""
        with writer.element('class'):
            self._eat(lexer, writer, 'class')
            self._read_identifier(lexer, writer)
            self._eat(lexer, writer, '{')
            self._compile_class_variables(lexer, writer)
            self._compile_class_subroutines(lexer, writer)
            self._eat(lexer, writer, '}')
