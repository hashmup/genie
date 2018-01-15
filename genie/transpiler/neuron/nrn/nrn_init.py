from functools import reduce
from collections import defaultdict
from itertools import chain
from textx.model import children_of_type, parent_of_type
from transpiler.neuron.optimizer import Optimizer


class NrnInit():
    def __init__(self):
        self.optimizer = Optimizer()

    def gen(self, root, macro_table):
        return {
            "link_table": self.get_link_table(root, macro_table),
            "initialize_table": self.get_initialize_table(root),
            "initmodel": self.get_initmodel(root),
            "read_ions": self.get_read_ions(root),
            "restruct_table": self.get_restruct_table(root)
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
        # for param in params:
        #     code += "\tdouble* {0}_table ="\
        #             " &(_{0}_table[BUFFER_SIZE * _nth->_id]);\n"\
        #             .format(param)
        # # code += "#ifndef KPLUS_WITHOUT_SHARED_CURRENT\n"
        # ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
        #         for x in children_of_type('UseIon', root)]
        # for ion in reduce(lambda x, y: x+y, ions):
        #     code += "\tdouble* {0}_table ="\
        #             " &(_{0}_table[BUFFER_SIZE * _nth->_id]);\n"\
        #             .format(ion)
        # # code += "#endif\n"
        # return code

    def get_initialize_table(self, root):
        code = ""
        params = \
            [x.name for x in children_of_type('ParDef', root)] +\
            [x.name for x in children_of_type('State', root)[0].state_vars] +\
            ['v']
        for param in params:
            code += "\t\t{0}_table[_iml] = {0};\n"\
                    .format(param)
        ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
                for x in children_of_type('UseIon', root)]
        for ion in children_of_type('UseIon', root):
            code += "\t\t{0}_table[_iml] = _ion_{0};\n"\
                    .format(ion.r[0].reads[0].name)
        return code

    def get_restruct_table(self, root):
        code = "\tfor(_iml = 0; _iml < TABLE_SIZE; _iml++) {\n"
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\tTABLE_{0}(_iml) = _t_{1}[_iml];\n"\
                    .format(param.name.upper(), param.name)
        code += "\t}\n"
        return code

    def get_read_ions(self, root):
        code = ""
        for x in children_of_type('UseIon', root):
            code += "\t\t{0} = _ion_{0};\n"\
                    .format(x.r[0].reads[0].name)
        return code

    def get_initmodel(self, root):
        code = ""
        for state in children_of_type('State', root)[0].state_vars:
            code += "\t{0} = {0}inf;\n".format(state.name)
        return code
