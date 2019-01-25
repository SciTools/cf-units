# Generated from udunits2Parser.g4 by ANTLR 4.7.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\3")
        buf.write("\7\4\2\t\2\3\2\3\2\3\2\2\2\3\2\2\2\2\5\2\4\3\2\2\2\4\5")
        buf.write("\7\3\2\2\5\3\3\2\2\2\2")
        return buf.getvalue()


class udunits2Parser ( Parser ):

    grammarFileName = "udunits2Parser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "ALL" ]

    RULE_unit_spec = 0

    ruleNames =  [ "unit_spec" ]

    EOF = Token.EOF
    ALL=1

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Unit_specContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALL(self):
            return self.getToken(udunits2Parser.ALL, 0)

        def getRuleIndex(self):
            return udunits2Parser.RULE_unit_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnit_spec" ):
                listener.enterUnit_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnit_spec" ):
                listener.exitUnit_spec(self)




    def unit_spec(self):

        localctx = udunits2Parser.Unit_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_unit_spec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2
            self.match(udunits2Parser.ALL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





