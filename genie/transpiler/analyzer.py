import os
import re
from os.path import join, dirname, abspath
from textx.model import children_of_type, parent_of_type
from itertools import chain
from transpiler.parser.lems import LemsCompTypeGenerator
from utils.fileutil import *


ROOT = abspath(dirname(__file__))


class Analyzer():
    def __init__(self):
        self.lems_comp_type_generator = LemsCompTypeGenerator()

    def parse(self):
        with open(self.path, "r") as f:
            data = f.read()
        self.lems_comp_type_generator.compile_to_string(data)
        return self.lems_comp_type_generator.root

    def parse_into_token(self, exp):
        term_exp = re.compile("[\(\)\+\-\/\*\=\{\}\s]")
        start = 0
        pos = 0
        tokens = []
        # we need this in case that we have a token at the end
        exp += " "
        while pos < len(exp):
            m = term_exp.match(exp[pos])
            if m:
                token = exp[start:pos]
                if token:
                    tokens.append(token)
                start = pos + 1
            pos += 1
        return list(set(tokens))

    def gen(self, path):
        self.path = path
        self.setup_dir()
        write_file(
            self.get_output_filepath(),
            self.compile())

    def get_all_symbols(self, path):
        symbols = self.get_derivative_symbols(path) +\
                  self.get_breakpoint_symbols(path) +\
                  self.get_global_symbols(path)
        return set(list(chain.from_iterable(symbols)))

    def get_table_candidate(self, path):
        derivative_sym = self.get_derivative_symbols(path)
        breakpoint_sym = self.get_breakpoint_symbols(path)
        global_sym = self.get_global_symbols(path)
        pass

    def get_symbols(self, path, stmt_type):
        self.path = path
        root = self.parse()
        symbols = []
        stmts = children_of_type(stmt_type, root)[0].b.stmts
        for stmt in stmts:
            tokens = []
            if hasattr(stmt, 'variable'):
                if stmt.variable:
                    if hasattr(stmt.variable, 'lems'):
                        exp = stmt.variable.lems
                    else:
                        exp = stmt.variable
                    tokens_lhs = self.parse_into_token(exp)
                    if len(tokens_lhs):
                        tokens.append(tokens_lhs)
            if hasattr(stmt, 'expression'):
                if stmt.expression.lems:
                    tokens_rhs = self.parse_into_token(stmt.expression.lems)
                    if len(tokens_rhs):
                        tokens.append(tokens_rhs)
            if len(tokens):
                symbols.append(list(chain.from_iterable(tokens)))
        return symbols

    def get_derivative_symbols(self, path):
        return self.get_symbols(path, 'Derivative')

    def get_breakpoint_symbols(self, path):
        return self.get_symbols(path, 'Breakpoint')

    def get_global_symbols(self, path):
        self.path = path
        root = self.parse()
        symbols = []
        global_syms = children_of_type('Global', root)[0].globals
        for global_sym in global_syms:
            symbols.append(global_sym.name)
        return [symbols]


class UnionFindToken:
    """
    " Union-Find tree structure only for categorizing tokens.
    """
    def __init__(self, tokens):
        """
        " tokens: [[token, token,...], [token, token,...], [token, token,...]]
        """
        pass
