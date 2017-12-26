import re
from textx.model import children_of_type, parent_of_type


class Parser():
    """
    " This class is used to parse expressions
    """
    def __init__(self):
        pass


class Optimizer():
    """
    " This class is used to parse expressions.
    " Since we need to obtain which variables are used in there.
    """
    def __init__(self):
        pass

    def check_and_replace_token(self, exp, token, suffix):
        term_exp = re.compile("[\(\)\+\-\/\*\=\{\}\s]")
        start = 0
        while True:
            pos = exp.find(token, start)
            replace = True
            if pos < 0:
                break
            if pos > 0:
                # check left
                if not term_exp.match(exp[pos - 1]):
                    replace = False
            if pos + len(token) + 1 < len(exp):
                # check right
                if not term_exp.match(exp[pos+len(token)]):
                    replace = False
            if replace:
                exp = exp[:pos+len(token)] + suffix + exp[pos+len(token):]
            start = pos + len(token)
        exp = exp.replace('{', '')
        exp = exp.replace('}', '')
        return exp

    def optimize(self, exp, tables, suffix):
        """
        " Take Expression and possible tables
        " If we can use table, replace it in expression
        """
        # tokens = self.parse(exp)
        for token in tables:
            exp = self.check_and_replace_token(exp, token, suffix)
        return exp

    def parse(self, exp):
        """
        " Expression is supposed to contain
        " '(', ')', '*/-+', numbers, function names and variables
        """
        pass
