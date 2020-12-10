from lexer import Lexer
from xml_writer import XmlWriter
from typing import TextIO


class JackXmlCompiler:
    def __init__(self, content: str, output_file: TextIO):
        self._output = output_file
        self._lexer = Lexer(content)
        self._output = XmlWriter(output_file)


    def compile_tokens(self) -> None:
        with self._output.element('tokens'):
            while not self._lexer.finished:
                while not self._lexer.finished:
                    self._output.write_token(self._lexer.next())
