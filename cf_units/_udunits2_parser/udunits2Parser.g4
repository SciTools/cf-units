// Derived from https://www.unidata.ucar.edu/software/udunits/udunits-2.0.4/udunits2lib.html#Grammar

parser grammar udunits2Parser;

// Use tokens from our UDUNITS2 lex rules.
options { tokenVocab=udunits2Lexer; }


unit_spec:
    shift_spec? EOF  // Zero or one "shift_spec", followed by the end of the input.
;

shift_spec:
    product
    | product WS? SHIFT_OP WS? number    // e.g. Kelvin @ 273.15
    | product WS? SHIFT_OP WS? timestamp // e.g. hours since 2001-12-31 23:59:59.999 +6
;

product:
    power
    | product power             // e.g. m2s (s*m^2)
    | product MULTIPLY power    // e.g. m2*s
    | product DIVIDE power      // e.g. m2/2
    | product WS+ power         // e.g. "m2 s"
;

power:
    basic_spec integer   // e.g. m+2, m2. Note that this occurs *before* basic_spec,
                         // as m2 should be matched before m for precendence of power
                         // being greater than multiplication (e.g. m2==m^2, not m*2).
    | basic_spec
    | basic_spec RAISE integer      // e.g. m^2
    | basic_spec UNICODE_EXPONENT   // e.g. m²
;

basic_spec:
    ID
    | '(' shift_spec ')'
// Log not yet implemented, but it is supported in UDUNITS2.
//    | LOGREF product_spec ')'
    | number
;

integer:
    INT | SIGNED_INT
;

number:
    integer | FLOAT
;


timestamp:
    (DATE | INT)     // e.g "s since 1990", "s since 1990:01[:02]"

    | ((DATE | INT) WS? signed_clock (WS? timezone_offset)?)    // e.g. "s since 1990:01:01 12:21 +6

    | DT_T_CLOCK    // e.g. "s since 1990:01:02T1900"
    | (TIMESTAMP WS? timezone_offset?)    // e.g. "s since 19900101T190030"
;

signed_clock:
    HOUR_MINUTE_SECOND  // e.g. 10:11:12
  | HOUR_MINUTE         // e.g. 10:11
  | integer             // e.g. +101112
;

timezone_offset:
    HOUR_MINUTE         // e.g. 10:11
    | integer           // e.g. 1011
    // NOTE: UDUNITS2 also supports named timezones, but these aren't documented
    // in the grammar, and aren't yet implemented here.
;
