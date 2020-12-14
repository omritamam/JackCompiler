import argparse
import sys
import os
from typing import Sequence
from xml_compiler import JackXmlCompiler
from lexer import TokenParseError


def files_from_path(path: str) -> Sequence[str]:
    """Translate supplied assembly path to a list of objects to assemble"""
    if os.path.isdir(path):
        # Handle case path is a directory
        full_paths = (os.path.abspath(os.path.join(path, filename)) for filename in os.listdir(path))
        output = [path for path in full_paths if os.path.isfile(path) and path.endswith('.jack')]

        return output

    elif os.path.isfile(path):
        # Handle case path is a file
        return [os.path.abspath(path)]

    else:
        raise ValueError(f'Path "{str(path)}" is not a file or a directory')


def handle_file(input_path: str, output_path: str) -> None:
    """Compiles a given file using JackXmlCompiler"""
    try:
        with open(input_path, 'r') as input_obj:
            with open(output_path, 'w') as output_obj:
                compiler = JackXmlCompiler(input_obj.read())
                compiler.compile(output_obj)

    except TokenParseError as err:
        print(f'{input_path}:')
        print(err)


def main() -> int:
    """Main entrypoint of the module"""
    # Parse args
    parser = argparse.ArgumentParser(description="Jack language compiler.")
    parser.add_argument('--analyze', action="store_true",
                        help="Analyze the give file/files and dump their hierarchy to an XML file.")
    parser.add_argument('path', help="A path to a jack file, or a directory with jack files.")

    args = parser.parse_args()

    try:
        files = files_from_path(args.path)
    except ValueError as err:
        print(f'Error: {str(err)}')
        return -1

    for obj_path in files:
        output_path = f'{os.path.splitext(obj_path)[0]}.xml'
        handle_file(obj_path, output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
