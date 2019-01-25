def py_3_only():
    # This function is only syntactically valid in Python 3.
    # We want PY2 users to see this syntax error, rather than a
    # significantly more complex SyntaxError in the generated parser.

    return f'is_py_3!'
