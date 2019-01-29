# Generated from /Users/pelson/dev/scitools/cf-units/cf_units/_udunits2_parser/udunits2Parser.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .udunits2Parser import udunits2Parser
else:
    from udunits2Parser import udunits2Parser

# This class defines a complete generic visitor for a parse tree produced by udunits2Parser.

class udunits2ParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by udunits2Parser#unit_spec.
    def visitUnit_spec(self, ctx:udunits2Parser.Unit_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#shift_spec.
    def visitShift_spec(self, ctx:udunits2Parser.Shift_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#product.
    def visitProduct(self, ctx:udunits2Parser.ProductContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#power.
    def visitPower(self, ctx:udunits2Parser.PowerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#basic_spec.
    def visitBasic_spec(self, ctx:udunits2Parser.Basic_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#integer.
    def visitInteger(self, ctx:udunits2Parser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#number.
    def visitNumber(self, ctx:udunits2Parser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#timestamp.
    def visitTimestamp(self, ctx:udunits2Parser.TimestampContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#signed_clock.
    def visitSigned_clock(self, ctx:udunits2Parser.Signed_clockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#timezone_offset.
    def visitTimezone_offset(self, ctx:udunits2Parser.Timezone_offsetContext):
        return self.visitChildren(ctx)



del udunits2Parser