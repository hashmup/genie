import os
import re
from os.path import join, dirname, abspath
from collections import defaultdict
from textx.model import children_of_type, parent_of_type
from itertools import chain, combinations
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

    def remove_token(self, candidate, remove_list):
        li = [[] for x in range(len(candidate))]
        for i in range(len(candidate)):
            li[i] = [x for x in candidate[i] if x not in remove_list[0]]
        return li

    def get_table_candidate(self, path):
        derivative_sym = self.get_derivative_symbols(path)
        breakpoint_sym = self.get_breakpoint_symbols(path)
        global_sym = self.get_global_symbols(path)
        derivative_sym = self.remove_token(derivative_sym, global_sym)
        breakpoint_sym = self.remove_token(breakpoint_sym, global_sym)
        table_candidate = derivative_sym + breakpoint_sym
        uft = UnionFindToken(table_candidate)
        return uft.get_related_tokens()

    def powerset(self, iterable):
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

    def get_table_candidates(self, path):
        token_candidate = self.get_table_candidate(path)
        return list(self.powerset(token_candidate))

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
        # make flatten table of tokens
        self.table = list(set(list(chain.from_iterable(tokens))))
        self.translate_table = defaultdict(dict)
        self._parent = [x for x in range(len(self.table))]
        self._rank = [0] * len(self.table)
        for i in range(len(self.table)):
            self.translate_table[self.table[i]] = i
        for _tokens in tokens:
            if len(_tokens):
                for token in _tokens[1:]:
                    self.unite(self.translate_table[_tokens[0]],
                               self.translate_table[token])

    def get_related_tokens(self):
        tokens = [[] for i in range(len(self.table))]
        for i in range(len(self.table)):
            root = self.find(i)
            tokens[root].append(self.table[i])
        return [x for x in tokens if x != []]

    def find(self, x):
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def unite(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if x != y:
            if self._rank[x] < self._rank[y]:
                self._parent[x] = y
            else:
                self._parent[y] = x
                if self._rank[x] == self._rank[y]:
                    self._rank[x] += 1
