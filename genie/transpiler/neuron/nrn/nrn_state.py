from functools import reduce
from collections import defaultdict
from itertools import chain
from transpiler.neuron.optimizer import Optimizer
from transpiler.analyzer import Analyzer
from textx.model import children_of_type, parent_of_type


class NrnState():
    def __init__(self):
        self.optimizer = Optimizer()
        self.analyzer = Analyzer()

    def gen(self, root, do_loop_division, macro_table):
        return {
            "link_table": self.get_link_table(root, macro_table),
            "calc_table": self.get_calc_table(root, do_loop_division, macro_table)
        }

    def obtain_link_table(self, root):
        ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
                for x in children_of_type('UseIon', root)]
        return [x.name for x in children_of_type('Range', root)[0].ranges] +\
            children_of_type('Nonspecific', root)[0].nonspecifics +\
            [x.name for x in children_of_type('State', root)[0].state_vars] +\
            reduce(lambda x, y: x+y, ions) +\
            ['v', 'g']

    def get_link_table(self, root, macro_table):
        code = ""
        params = self.obtain_link_table(root)
        if macro_table:
            flatten_table = list(chain.from_iterable(macro_table))
        else:
            flatten_table = []
        return self.optimizer.optimize_table_ptr(tab_size=1,
                                                 token_table=params,
                                                 macro_table=flatten_table)

    def get_calc_table(self, root, do_loop_division, macro_table):
        code = ""
        stmts = children_of_type('Derivative', root)[0].b.stmts
        exclude = [x.name for x in children_of_type('Global', root)[0].globals]
        loop_prefix = "#ifdef KPLUS_USE_MOD_OMP\n"\
                      "#pragma omp for\n"\
                      "#endif\n"\
                      "#pragma loop noalias\n"\
                      "#pragma loop norecurrence\n"\
                      "\tfor (_iml = 0; _iml < _cntml; _iml++) {\n"
        loop_suffix = "\t}\n"
        if macro_table:
            relation_list = [[] for x in range(len(macro_table))]
        else:
            relation_list = [[]]
        remain_stmt = []
        if do_loop_division and macro_table:
            for stmt in stmts:
                if stmt.variable and stmt.expression:
                    table_id =\
                        self.analyzer.is_stmt_in_group(macro_table, stmt, exclude)
                    if table_id >= 0:
                        relation_list[table_id].append(stmt)
                    else:
                        remain_stmt.append(stmt)
        else:
            for stmt in stmts:
                if stmt.variable and stmt.expression:
                    remain_stmt.append(stmt)
        for related_stmts in relation_list:
            if len(related_stmts):
                code += loop_prefix
                code += "\t\tint v_i = _i_table[_iml];\n"\
                        "\t\tFLOAT theta = _theta_table[_iml];\n"
                # first obtain global vars
                for stmt in related_stmts:
                    tokens = self.analyzer.get_symbols_from_stmt(stmt)
                    for token in tokens:
                        if token in exclude:
                            code += "\t\tFLOAT _{0};\n"\
                                    "\t\t_{0} = TABLE_{1}(v_i);\n"\
                                    .format(token, token.upper())
                # next append expression
                for stmt in related_stmts:
                    tokens = self.analyzer.get_symbols_from_stmt(stmt)
                    code += "\t\t{0}_table[_iml] += (1.0f - EXP(-local_dt/_{0}tau))"\
                            " * (_{0}inf + theta * (TABLE_{1}INF(v_i + 1) - _{0}inf)"\
                            " - {0}_table[_iml]);\n"\
                            .format(stmt.variable, stmt.variable.upper())
                code += loop_suffix
        if len(remain_stmt):
            code += loop_prefix
            code += "\t\tint v_i = _i_table[_iml];\n"\
                    "\t\tFLOAT theta = _theta_table[_iml];\n"
            # first obtain global vars
            for stmt in remain_stmt:
                tokens = self.analyzer.get_symbols_from_stmt(stmt)
                for token in tokens:
                    if token in exclude:
                        code += "\t\tFLOAT _{0};\n"\
                                "\t\t_{0} = TABLE_{1}(v_i);\n"\
                                .format(token, token.upper())
            # next append expression
            for stmt in remain_stmt:
                tokens = self.analyzer.get_symbols_from_stmt(stmt)
                code += "\t\t{0}_table[_iml] += (1.0f - EXP(-local_dt/_{0}tau))"\
                        " * (_{0}inf + theta * (TABLE_{1}INF(v_i + 1) - _{0}inf)"\
                        " - {0}_table[_iml]);\n"\
                        .format(stmt.variable, stmt.variable.upper())
            code += loop_suffix

        return code
