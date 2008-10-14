"""Read a string dict into a dict, without using eval.

Based on a comp.lang.python post by Fredrik Lundh

TODO: Switch to ast.literal_eval, once Python 2.6 is mainstream.
"""

import cStringIO as StringIO
import tokenize

def _parse(token, src):
    if token[1] == "{":
        out = {}
        token = src.next()
        while token[1] != "}":
            key = _parse(token, src)
            token = src.next()
            if token[1] != ":":
                raise SyntaxError("malformed dictionary")
            value = _parse(src.next(), src)
            out[key] = value
            token = src.next()
            if token[1] == ",":
                token = src.next()
        return out
    elif token[1] == "[" or token[1] == "(":
        if token[1] == "[":
            endtoken = "]"
        else:
            endtoken = ")"
        out = []
        token = src.next()
        while token[1] != endtoken:
            out.append(_parse(token, src))
            token = src.next()
            if token[1] == ",":
                token = src.next()
        return out
    elif token[0] == tokenize.STRING:
        return token[1][1:-1].decode("string-escape")
    elif token[0] == tokenize.NUMBER:
        try:
            return int(token[1], 0)
        except ValueError:
            return float(token[1])
    elif token[0] == tokenize.NAME:
        return eval(token[1])
    else:
        raise SyntaxError("malformed expression %s" % (str(token)))

def reval(source):
    src = StringIO.StringIO(source).readline
    src = tokenize.generate_tokens(src)
    return _parse(src.next(), src)
