from functools import reduce
from collections import defaultdict
from itertools import chain
from transpiler.neuron.optimizer import Optimizer
from textx.model import children_of_type, parent_of_type


class NrnState():
    def __init__(self):
        self.optimizer = Optimizer()

    def gen(self, root, macro_table):
        return {
            "link_table": self.get_link_table(root, macro_table),
            "calc_table": self.get_calc_table(root)
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

    def get_calc_table(self, root):
        code = "#ifdef KPLUS_USE_MOD_OMP\n"\
               "#pragma omp for\n"\
               "#endif\n"\
               "#pragma loop noalias\n"\
               "#pragma loop norecurrence\n"\
               "\tfor (_iml = 0; _iml < _cntml; _iml++) {\n"
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\tFLOAT _{0};\n".format(param.name)
        code += "\t\tint v_i = _i_table[_iml];\n"\
                "\t\tFLOAT theta = _theta_table[_iml];\n"
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\t{0} = TABLE_{1}(v_i);\n"\
                    .format(param.name, param.name.upper())
        for state in children_of_type('State', root)[0].state_vars:
            code += "\t\t{0}_table[_iml] += (1.0f - EXP(-local_dt/_{0}tau))"\
                    " * (_{0}inf + theta * (TABLE_{1}INF(v_i + 1) - _{0}inf)"\
                    " - {0}_table[_iml]);\n"\
                    .format(state.name, state.name.upper())
        code += "\t}\n"
        return code
