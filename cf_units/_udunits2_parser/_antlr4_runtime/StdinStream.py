import codecs
import sys

from cf_units._udunits2_parser._antlr4_runtime.InputStream import InputStream


class StdinStream(InputStream):
    def __init__(
        self, encoding: str = "ascii", errors: str = "strict"
    ) -> None:
        bytes = sys.stdin.buffer.read()
        data = codecs.decode(bytes, encoding, errors)
        super().__init__(data)
