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

    def optimize_exp(self, exp, token_table, macro_table):
        """
        " Take Expression and possible tables
        " If we can use table, replace it in expression
        """
        # tokens = self.parse(exp)
        optimized_exp = ""
        term_exp = re.compile("[\(\)\+\-\/\*\=\{\}\s]")
        start = 0
        pos = 0
        tokens = []
        # we need this in case that we have a token at the end
        exp = exp.replace('{', '')
        exp = exp.replace('}', '')
        exp += " "
        while pos < len(exp):
            m = term_exp.match(exp[pos])
            if m:
                token = exp[start:pos]
                if token:
                    if macro_table and token in macro_table:
                        optimized_exp += "TABLE_{0}(_iml)"\
                                         .format(token.upper())
                    elif token in token_table:
                        optimized_exp += "_{0}_table[_iml]"\
                                         .format(token)
                    else:
                        optimized_exp += token
                optimized_exp += exp[pos]
                start = pos + 1
            pos += 1
        return optimized_exp[:len(optimized_exp)-1]

    def optimize_table_ptr(self, tab_size, token_table, macro_table):
        """
        " Take a list of tokens then generate pointer to table
        """
        code = ""
        tab = "\t" * tab_size
        for token in token_table:
            if macro_table and token in macro_table:
                code += "{0}double* {1}_table = "\
                        "&(TABLE_{2}(BUFFER_SIZE * _nth->_id));\n"\
                        .format(tab, token, token.upper())
            else:
                code += "{0}double* {1}_table = "\
                        "&(_{1}_table[BUFFER_SIZE * _nth->_id]);\n"\
                        .format(tab, token)
        return code

    def parse(self, exp):
        """
        " Expression is supposed to contain
        " '(', ')', '*/-+', numbers, function names and variables
        """
        pass
