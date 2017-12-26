from functools import reduce
from collections import defaultdict
from textx.model import children_of_type, parent_of_type


class NrnState():
    def __init__(self):
        pass

    def gen(self, root):
        return {
            "link_table": self.get_link_table(root),
            "calc_table": self.get_calc_table(root)
        }

    def get_link_table(self, root):
        code = ""
        params = [x.name for x in children_of_type('Range', root)[0].ranges] +\
            children_of_type('Nonspecific', root)[0].nonspecifics +\
            [x.name for x in children_of_type('State', root)[0].state_vars] +\
            ['v', 'g']
        for param in params:
            code += "\tdouble* {0}_table ="\
                    " &(_{0}_table[BUFFER_SIZE * _nth->_id]);\n"\
                    .format(param)
        # code += "#ifndef KPLUS_WITHOUT_SHARED_CURRENT\n"
        ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
                for x in children_of_type('UseIon', root)]
        for ion in reduce(lambda x, y: x+y, ions):
            code += "\tdouble* {0}_table ="\
                    " &(_{0}_table[BUFFER_SIZE * _nth->_id]);\n"\
                    .format(ion)
        # code += "#endif\n"
        return code

    def get_calc_table(self, root):
        code = "#ifdef KPLUS_USE_MOD_OMP\n"\
               "#pragma omp for\n"\
               "#endif\n"\
               "#pragma loop noalias\n"\
               "#pragma loop norecurrence\n"\
               "\tfor (_iml = 0; _iml < _cntml; _iml++) {\n"
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\tFLOAT {0};\n".format(param.name)
        code += "\t\tint v_i = _i_table[_iml];\n"\
                "\t\tFLOAT theta = _theta_table[_iml];\n"
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\t{0} = TABLE_{1}(v_i);\n"\
                    .format(param.name, param.name.upper())
        for state in children_of_type('State', root)[0].state_vars:
            code += "\t\t{0}_table[_iml] += (1.0f - EXP(-local_dt/{0}tau))"\
                    " * ({0}inf + theta * (TABLE_{1}INF(v_i + 1) - {0}inf)"\
                    " - {0}_table[_iml]);\n"\
                    .format(state.name, state.name.upper())
        code += "\t}\n"
        return code
