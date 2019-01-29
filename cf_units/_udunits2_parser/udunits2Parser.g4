parser grammar udunits2Parser;

options { tokenVocab=udunits2Lexer; }


unit_spec:
    shift_spec? EOF  // Zero or one "shift_spec", followed by the end of the input.
;

shift_spec:
    product
    | product shift number    // Kelvin @ 273.15
    | product shift timestamp // hours since 2001-12-31 23:59:59.999 +6
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
//    | LOGREF product_spec ')'
    | number
;

integer:
    INT | SIGNED_INT
;

number:
    integer | FLOAT
;


timestamp: WS?
    (DATE | INT)    // e.g "s since 1990", "s since 1990:01[:02]"
    | ((DATE | INT) WS? signed_clock (WS? signed_hour_minute)?)
    | DT_T_CLOCK  // "1990:01:02T1900"
//     | (date WS+ signed_int)            // Date + packed_clock
//     | (date WS+ signed_int WS+ clock)  // Date + (packed_clock - )
//     | (date sign (INT|clock) WS+ hour_minute)  // Date + (packed_clock - tz offset)
// 
//     | (date WS+ signed_int ((WS+ INT) | (WS* signed_int)))  // Date + packed_clock + Timezone Offset
    | WS? TIMESTAMP

//    | (date WS+ clock WS+ ID) // UNKNOWN!
//    | (TIMESTAMP WS+ INT) // UNKNOWN!
//    | (TIMESTAMP WS+ ID) // TIMEZONE (UNDOCUMENTED)!
;

signed_clock:
    HOUR_MINUTE_SECOND | HOUR_MINUTE | integer 
;

signed_hour_minute:
    // Second not allowed.
    (HOUR_MINUTE | integer)
    | (WS* SIGNED_INT)
;

clock: HOUR_MINUTE | HOUR_MINUTE_SECOND;

shift:
    WS* SHIFT_OP WS*
;
