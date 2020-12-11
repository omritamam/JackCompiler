from lexer import Token
from typing import TextIO


def _encapsulate(string: str) -> str:
    return string \
            .replace('&', '&amp') \
            .replace('<', '&lt') \
            .replace('>', '&gt') \
            .replace("'", '&apos') \
            .replace('"', '&quot')


class XmlWriter:
    _file_obj: TextIO
    _hierarchy_stack: list
    _indentation: str

    def __init__(self, file_obj, indentation='    '):
        self._file_obj = file_obj
        self._hierarchy_stack = []
        self._indentation = indentation

    def _write_new_line(self) -> None:
        """Writes a new line to the file."""
        self._file_obj.write('\n')

    def _write_indentation(self) -> None:
        """Writes indentation to the file based on the opened tags hierarchy."""
        count = len(self._hierarchy_stack)
        self._file_obj.write(self._indentation * count)

    def _write_tag(self, content: str, closing=False) -> None:
        """Outputs the given tag."""
        if closing:
            self._file_obj.write(f'</{_encapsulate(content)}>')
        else:
            self._file_obj.write(f'<{_encapsulate(content)}>')

    def _start_element(self, element_type: str) -> None:
        """
        Starts a new tag with the given hierarchy that will be closed after calling
        self._close_element
        """
        self._write_indentation()
        self._write_tag(element_type)
        self._write_new_line()
        self._hierarchy_stack.append(element_type)

    def _close_element(self) -> None:
        """
        Closes the last opened element.
        """
        element_type = self._hierarchy_stack.pop()
        self._write_indentation()
        self._write_tag(f'{element_type}', closing=True)
        self._write_new_line()

    def element(self, element_type: str) -> '_XmlElementContext':
        """
        Returns a context manager that can be used in with statements.
        For example:
            with writer.element('hello'):
                writer.write_token(Token('value', 'type'))

        Will produce:
            <hello>
                <type> value </type>
            </hello
        """
        return _XmlElementContext(self, element_type)

    def write_token(self, token: Token) -> None:
        """
        Writes a line represents a given token in to following format:
            <token_type> token_value </token_type>
        """
        self._write_indentation()
        self._write_tag(token.type)
        self._file_obj.write(f' {_encapsulate(token.value)} ')
        self._write_tag(token.type, closing=True)
        self._write_new_line()


class _XmlElementContext:
    def __init__(self, writer: XmlWriter, element_type: str):
        self._writer = writer
        self._type = element_type

    def __enter__(self) -> '_XmlElementContext':
        self._writer._start_element(self._type)
        return self

    def __exit__(self, *exc) -> bool:
        self._writer._close_element()
        return False
