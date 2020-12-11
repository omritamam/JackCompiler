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
