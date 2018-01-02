import re
from functools import reduce
from collections import defaultdict
from transpiler.neuron.optimizer import Optimizer
from textx.model import children_of_type, parent_of_type


class NrnCur():
    def __init__(self):
        self.optimizer = Optimizer()

    def gen(self, root):
        return {
            "link_table": self.get_link_table(root),
            "break_point":
            self.get_break_point(root),
            "break_point_without_current":
            self.get_break_point_without_current(root)
        }

    def obtain_link_table(self, root):
        ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
                for x in children_of_type('UseIon', root)]
        return [x.name for x in children_of_type('Range', root)[0].ranges] +\
            children_of_type('Nonspecific', root)[0].nonspecifics +\
            [x.name for x in children_of_type('State', root)[0].state_vars] +\
            reduce(lambda x, y: x+y, ions) +\
            ['v', 'g']

    def get_link_table(self, root):
        code = ""
        params = self.obtain_link_table(root)
        for param in params:
            code += "\tdouble* {0}_table ="\
                    " &(_{0}_table[BUFFER_SIZE * _nth->_id]);\n"\
                    .format(param)
        # code += "#ifndef KPLUS_WITHOUT_SHARED_CURRENT\n"
        # code += "#endif\n"
        return code

    def get_break_point_without_current(self, root):
        """
        " TODO: Still needs to figure out what these eqs mean.
        """
        code = ""
        method = children_of_type('Breakpoint', root)[0].b.stmts[0].method
        if method == "cnexp":
            stmts = defaultdict(dict)
            tables = self.obtain_link_table(root)
            prefix = "#ifdef KPLUS_USE_MOD_OMP\n"\
                     "#pragma omp for\n"\
                     "#endif\n"\
                     "#pragma loop noalias\n"\
                     "#pragma loop norecurrence\n"
            loop_prefix = "\tfor (_iml = 0; _iml < _cntml; _iml++) {\n"
            code += "#ifdef KPLUS_WITHOUT_SHARED_CURRENT\n"\
                    "#ifdef KPLUS_USE_MOD_OMP\n"\
                    "#pragma omp parallel\n"\
                    "#endif\n"\
                    "{\n"
            for stmt in children_of_type('Breakpoint', root)[0].b.stmts[1:]:
                stmts[stmt.variable.lems] = stmt.expression.lems
            # calculate v
            code += prefix
            code += loop_prefix
            code += "\t\tv_table[_iml] = vec_v[_ni[_iml]];\n"\
                    "\t}\n"
            # core calculation
            code += prefix
            code += loop_prefix
            # calculate g
            g_ions = ""
            for ion in children_of_type('UseIon', root):
                target = "g{0}".format(ion.ion)
                g_ions += " + _{0}".format(target)
                exp = stmts[target]
                code += "\t\tdouble _{0};\n".format(target)
                code += "\t\t_{0} = {1};\n"\
                        .format(target, self.optimizer.optimize(exp,
                                                                tables,
                                                                "_table[_iml]"
                                                                ))
            code += "\t\tg_table[_iml] = gl_table[_iml]{0};\n".format(g_ions)
            # calculate i
            i_ions = ""
            for ion in children_of_type('UseIon', root):
                target = ion.w[0].writes[0].name
                i_ions += "+ _{0}".format(target)
                exp = stmts[target]
                code += "\t\tdouble _{0};\n".format(target)
                code += "\t\t_{0} = {1};\n"\
                        .format(target,
                                self.optimizer.optimize(exp,
                                                        tables,
                                                        "_table[_iml]"
                                                        ))
            code += "\t\ti_table[_iml] = gl_table[_iml] * (v_table[_iml] - "\
                    "el_table[_iml]) {0};\n"\
                    .format(g_ions)
            code += "\t}\n"

            # calculate vec_rhs
            code += prefix
            code += loop_prefix
            code += "\t\tvec_rhs[_ni[_iml]] -= il_table[_iml];\n"\
                    "\t}\n"\
                    "}\n"
        return code

    def get_break_point(self, root):
        """
        " TODO: Still needs to figure out what these eqs mean.
        """
        code = ""
        method = children_of_type('Breakpoint', root)[0].b.stmts[0].method
        if method == "cnexp":
            stmts = defaultdict(dict)
            tables = self.obtain_link_table(root)
            loop_prefix = "\tfor (_iml = 0; _iml < _cntml; _iml++) {\n"
            for stmt in children_of_type('Breakpoint', root)[0].b.stmts[1:]:
                stmts[stmt.variable.lems] = stmt.expression.lems
            # calculate v
            code += loop_prefix
            code += "\t\tv_table[_iml] = vec_v[_ni[_iml]];\n"\
                    "\t}\n"
            # core calculation
            code += loop_prefix
            # calculate g
            for ion in children_of_type('UseIon', root):
                target = "g{0}".format(ion.ion)
                exp = stmts[target]
                code += "\t\t{0};\n"\
                        .format(
                            self.optimizer.optimize("{0} = {1}".format(
                                target, exp),
                                tables,
                                "_table[_iml]"))
            code += "\t\t{0};\n"\
                    .format(
                        self.optimizer.optimize("g = gna + gk + gl",
                                                tables,
                                                "_table[_iml]"))
            code += "\t}\n"
            code += loop_prefix
            # calculate i
            i_exp = re.compile("i\w+")
            for token in tables:
                if i_exp.match(token):
                    exp = stmts[token]
                    code += "\t\t{0};\n"\
                            .format(
                                self.optimizer.optimize("{0} = {1}".format(
                                    token, exp),
                                    tables,
                                    "_table[_iml]"))
            code += "\t\t{0};\n"\
                    .format(
                        self.optimizer.optimize("il += ina + ik",
                                                tables,
                                                "_table[_iml]"))
            code += "\t}\n"

            # calculate vec_rhs
            code += loop_prefix
            code += "\t\tvec_rhs[_ni[_iml]] -= il_table[_iml];\n"\
                    "\t}\n"
            code += loop_prefix
            for ion in children_of_type('UseIon', root):
                code += "\t\t_ion_di{0}dv += g{0}_table[_iml];\n"\
                        "\t\t_ion_i{0} += i{0}_table[_iml];\n"\
                        .format(ion.ion)
            code += "\t}\n"
        return code
