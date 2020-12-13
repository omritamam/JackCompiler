from lexer import Lexer
from xml_writer import XmlWriter
from typing import TextIO


class JackXmlCompiler:
    """
    A compiler that compiles jack into XML hierarchy.
    """

    _lexer: Lexer
    _output: XmlWriter

    def __init__(self, content: str, output_file: TextIO):
        self._lexer = Lexer(content)
        self._output = XmlWriter(output_file)

    def compile_tokens(self) -> None:
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
        with self._output.element('tokens'):
            while not self._lexer.finished:
                self._output.write_token(self._lexer.next())

    def compile_class(self) -> None:
        # with self._output.element('tokens'):
        self._output._start_element("class")
        self._output.write_token(self._lexer.next("identifier"))                    # className
        self._output.write_token(self._lexer.next("symbol"))                        # {
        while(self._lexer.peek().value in {"static", "field"}):                     # plural classVarDec
            self.compile_classVarDec()
        while (self._lexer.peek().value in {'constructor', 'function', 'method'}):  # plural subroutineDec
            self.compile_subroutineDec()
        self._output.write_token(self._lexer.next("symbol"))                        # }
        self._output._close_element()

    def compile_classVarDec(self):
        self._output._start_element("classVarDec")
        self._output.write_token(self._lexer.next("keyword"))           # static | field
        self._output.write_token(self._lexer.next())                    # int | char | boolean | className
        while(self._lexer.peek().value == ','):                         # plural , varname
            self._output.write_token(self._lexer.next("symbol"))        # ,
            self._output.write_token(self._lexer.next("identifier"))    # varName
        self._output.write_token(self._lexer.next("symbol"))            # ;
        self._output._close_element()

    def compile_subrutineDec(self):
        self._output._start_element("subrutineDec")
        self._output.write_token(self._lexer.next("keyword"))           # constructor | function | method
        self._output.write_token(self._lexer.next())                    # void | int | char | boolean | className
        self._output.write_token(self._lexer.next("identifier"))        # subroutineName
        self._output.write_token(self._lexer.next("symbol"))            # (
        self.compile_parameterList()
        self._output.write_token(self._lexer.next("symbol"))            # )
        self.compile_subroutineBody()
        self._output._close_element()
